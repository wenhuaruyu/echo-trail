import uuid
from io import BytesIO

from PIL import Image


def create_identity(client):
    response = client.post("/api/v1/sessions/anonymous")
    token = response.json()["data"]["access_token"]
    return {"Authorization": "Bearer {}".format(token)}


def get_song_with_lyric(client, headers, province_code="guangdong"):
    songs_response = client.get(
        "/api/v1/songs?province_code={}".format(province_code),
        headers=headers,
    )
    song = songs_response.json()["data"]["items"][0]
    lyrics_response = client.get(
        "/api/v1/songs/{}/lyrics".format(song["id"]),
        headers=headers,
    )
    lyric = lyrics_response.json()["data"]["items"][0]
    return song, lyric


def record_play(client, headers, song_id):
    response = client.post(
        "/api/v1/play-events",
        headers=headers,
        json={"song_id": song_id, "event_type": "started"},
    )
    assert response.status_code == 201
    return response.json()["data"]["play_event_id"]


def upload_test_photo(client, headers):
    content = BytesIO()
    Image.new("RGB", (40, 30), color=(34, 85, 68)).save(content, format="PNG")
    response = client.post(
        "/api/v1/uploads/ticket-photo",
        headers=headers,
        files={"file": ("trip.png", content.getvalue(), "image/png")},
    )
    assert response.status_code == 201
    return response.json()["data"]["photo_url"]


def ticket_payload(song, lyric, play_event_id, ticket_type="gold", province_code="guangdong"):
    return {
        "song_id": song["id"],
        "play_event_id": play_event_id,
        "province_code": province_code,
        "ticket_type": ticket_type,
        "message": "听见了时间的声音。",
        "location_text": "广州·珠江边" if province_code == "guangdong" else "西安·城墙边",
        "mood_tags": ["在路上"],
        "lyric_line_id": lyric["id"],
        "photo_url": None,
        "idempotency_key": str(uuid.uuid4()),
    }


def test_record_play_rejects_missing_song(client, auth_headers):
    response = client.post(
        "/api/v1/play-events",
        headers=auth_headers,
        json={"song_id": "not-found", "event_type": "started"},
    )
    assert response.status_code == 404
    assert response.json()["error_code"] == "SONG_NOT_FOUND"


def test_ticket_requires_matching_owned_play_event(client):
    owner_headers = create_identity(client)
    other_headers = create_identity(client)
    song, lyric = get_song_with_lyric(client, owner_headers)
    owner_event = record_play(client, owner_headers, song["id"])

    payload = ticket_payload(song, lyric, owner_event)
    response = client.post("/api/v1/tickets", headers=other_headers, json=payload)
    assert response.status_code == 422
    assert response.json()["error_code"] == "PLAY_EVENT_REQUIRED"

    payload["play_event_id"] = "not-found"
    payload["idempotency_key"] = str(uuid.uuid4())
    response = client.post("/api/v1/tickets", headers=owner_headers, json=payload)
    assert response.status_code == 422
    assert response.json()["error_code"] == "PLAY_EVENT_REQUIRED"


def test_create_ticket_is_idempotent(client):
    headers = create_identity(client)
    song, lyric = get_song_with_lyric(client, headers)
    event_id = record_play(client, headers, song["id"])
    payload = ticket_payload(song, lyric, event_id)

    first = client.post("/api/v1/tickets", headers=headers, json=payload)
    second = client.post("/api/v1/tickets", headers=headers, json=payload)

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["data"]["ticket"]["id"] == second.json()["data"]["ticket"]["id"]
    assert first.json()["data"]["created"] is True
    assert second.json()["data"]["created"] is False


def test_three_ticket_types_complete_province(client):
    headers = create_identity(client)
    song, lyric = get_song_with_lyric(client, headers, "shaanxi")
    event_id = record_play(client, headers, song["id"])

    for ticket_type in ("gold", "silver", "paper"):
        payload = ticket_payload(song, lyric, event_id, ticket_type, "shaanxi")
        if ticket_type == "silver":
            payload["photo_url"] = upload_test_photo(client, headers)
        response = client.post("/api/v1/tickets", headers=headers, json=payload)
        assert response.status_code == 201

    province = client.get("/api/v1/provinces/shaanxi", headers=headers).json()["data"]
    assert province["lighting_status"] == "complete"
    assert province["collected_type_count"] == 3
    assert province["ticket_count"] == 3


def test_ticket_type_and_photo_rules(client):
    headers = create_identity(client)
    song, lyric = get_song_with_lyric(client, headers)
    event_id = record_play(client, headers, song["id"])

    silver = ticket_payload(song, lyric, event_id, "silver")
    silver["photo_url"] = None
    response = client.post("/api/v1/tickets", headers=headers, json=silver)
    assert response.status_code == 422
    assert response.json()["error_code"] == "TICKET_PHOTO_REQUIRED"

    gold = ticket_payload(song, lyric, event_id, "gold")
    gold["photo_url"] = "https://example.com/not-allowed.jpg"
    response = client.post("/api/v1/tickets", headers=headers, json=gold)
    assert response.status_code == 422
    assert response.json()["error_code"] == "TICKET_PHOTO_NOT_ALLOWED"


def test_ticket_content_validation(client):
    headers = create_identity(client)
    song, lyric = get_song_with_lyric(client, headers)
    event_id = record_play(client, headers, song["id"])

    cases = [
        ("message", "声" * 61, "TICKET_MESSAGE_TOO_LONG"),
        ("location_text", "地点" * 11, "TICKET_LOCATION_TOO_LONG"),
        ("mood_tags", ["自由", "怀旧", "治愈", "宁静"], "TICKET_MOOD_LIMIT_EXCEEDED"),
        ("mood_tags", ["不存在的心情"], "TICKET_MOOD_INVALID"),
        ("lyric_line_id", "not-found", "LYRIC_NOT_IN_SONG"),
    ]
    for field, value, error_code in cases:
        payload = ticket_payload(song, lyric, event_id)
        payload[field] = value
        response = client.post("/api/v1/tickets", headers=headers, json=payload)
        assert response.status_code == 422
        assert response.json()["error_code"] == error_code


def test_placeholder_province_rejected(client):
    headers = create_identity(client)
    song, lyric = get_song_with_lyric(client, headers)
    event_id = record_play(client, headers, song["id"])
    payload = ticket_payload(song, lyric, event_id, province_code="zhejiang")
    response = client.post("/api/v1/tickets", headers=headers, json=payload)
    assert response.status_code == 422
    assert response.json()["error_code"] == "PROVINCE_NOT_AVAILABLE"


def test_ticket_list_filters_pagination_and_user_isolation(client):
    headers = create_identity(client)
    other_headers = create_identity(client)
    song, lyric = get_song_with_lyric(client, headers)
    event_id = record_play(client, headers, song["id"])

    for ticket_type in ("gold", "paper"):
        payload = ticket_payload(song, lyric, event_id, ticket_type)
        response = client.post("/api/v1/tickets", headers=headers, json=payload)
        assert response.status_code == 201

    first_page = client.get("/api/v1/tickets?page=1&page_size=1", headers=headers).json()["data"]
    assert first_page["total"] == 2
    assert len(first_page["items"]) == 1
    assert first_page["has_more"] is True

    gold = client.get("/api/v1/tickets?ticket_type=gold", headers=headers).json()["data"]
    assert gold["total"] == 1
    ticket_id = gold["items"][0]["id"]

    detail = client.get("/api/v1/tickets/{}".format(ticket_id), headers=headers)
    assert detail.status_code == 200
    forbidden_detail = client.get("/api/v1/tickets/{}".format(ticket_id), headers=other_headers)
    assert forbidden_detail.status_code == 404
    assert forbidden_detail.json()["error_code"] == "TICKET_NOT_FOUND"

    other_list = client.get("/api/v1/tickets", headers=other_headers).json()["data"]
    assert other_list["total"] == 0


def test_silver_recommendations_are_demo_data(client, auth_headers):
    song, _ = get_song_with_lyric(client, auth_headers)
    response = client.get(
        "/api/v1/provinces/guangdong/song-recommendations?source_song_id={}".format(song["id"]),
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["is_demo_data"] is True
    assert data["items"][0]["id"] == song["id"]
    assert len(data["items"]) == 3
