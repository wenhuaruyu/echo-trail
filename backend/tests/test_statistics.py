import uuid


def identity(client):
    response = client.post("/api/v1/sessions/anonymous")
    token = response.json()["data"]["access_token"]
    return {"Authorization": "Bearer {}".format(token)}


def song_and_lyric(client, headers, province="guangdong"):
    song = client.get(
        "/api/v1/songs?province_code={}".format(province), headers=headers
    ).json()["data"]["items"][0]
    lyric = client.get(
        "/api/v1/songs/{}/lyrics".format(song["id"]), headers=headers
    ).json()["data"]["items"][0]
    return song, lyric


def create_ticket(client, headers, song, lyric, province="guangdong", mood="在路上"):
    event = client.post(
        "/api/v1/play-events",
        headers=headers,
        json={"song_id": song["id"], "event_type": "started"},
    ).json()["data"]
    return client.post(
        "/api/v1/tickets",
        headers=headers,
        json={
            "song_id": song["id"],
            "play_event_id": event["play_event_id"],
            "province_code": province,
            "ticket_type": "gold",
            "message": "统计测试票根",
            "location_text": "演示地点",
            "mood_tags": [mood],
            "lyric_line_id": lyric["id"],
            "photo_url": None,
            "idempotency_key": str(uuid.uuid4()),
        },
    )


def test_resonance_uses_baseline_and_distinct_users(client):
    first_user = identity(client)
    second_user = identity(client)
    song, lyric = song_and_lyric(client, first_user)

    initial = client.get(
        "/api/v1/resonance?song_id={}&province_code=guangdong".format(song["id"]),
        headers=first_user,
    ).json()["data"]
    assert initial["base_count"] > 0

    first = create_ticket(client, first_user, song, lyric)
    second = create_ticket(client, first_user, song, lyric)
    third = create_ticket(client, second_user, song, lyric)
    assert first.status_code == second.status_code == third.status_code == 201

    result = client.get(
        "/api/v1/resonance?song_id={}&province_code=guangdong".format(song["id"]),
        headers=first_user,
    ).json()["data"]
    assert result["real_user_count"] == initial["real_user_count"] + 2
    assert result["count"] == result["base_count"] + result["real_user_count"]
    assert "广东" in result["display_text"]


def test_ticket_creation_returns_latest_resonance(client):
    headers = identity(client)
    song, lyric = song_and_lyric(client, headers, "shaanxi")
    response = create_ticket(client, headers, song, lyric, "shaanxi", "宁静")
    data = response.json()["data"]
    assert data["resonance"]["count"] >= data["resonance"]["base_count"]
    assert data["resonance"]["real_user_count"] >= 1
    assert data["resonance"]["is_demo_data"] is True


def test_emotion_map_has_five_scenes_and_percentages_total_100(client):
    headers = identity(client)
    for province in ("guangdong", "shaanxi"):
        response = client.get(
            "/api/v1/provinces/{}/emotion-map".format(province), headers=headers
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data["music_insights"]) == 5
        assert sum(item["percentage"] for item in data["mood_distribution"]) == 100
        assert data["is_demo_data"] is True


def test_placeholder_province_has_no_emotion_map(client):
    headers = identity(client)
    response = client.get("/api/v1/provinces/zhejiang/emotion-map", headers=headers)
    assert response.status_code == 422
    assert response.json()["error_code"] == "PROVINCE_NOT_AVAILABLE"


def test_real_weekly_data_can_replace_demo_weekly_song(client):
    headers = identity(client)
    songs = client.get(
        "/api/v1/songs?province_code=shaanxi", headers=headers
    ).json()["data"]["items"]
    target = next(song for song in songs if song["title"] == "西安以东")
    lyric = client.get(
        "/api/v1/songs/{}/lyrics".format(target["id"]), headers=headers
    ).json()["data"]["items"][0]
    for _ in range(3):
        assert create_ticket(client, headers, target, lyric, "shaanxi", "热血").status_code == 201

    data = client.get(
        "/api/v1/provinces/shaanxi/emotion-map", headers=headers
    ).json()["data"]
    weekly = next(item for item in data["music_insights"] if item["scene"] == "weekly_most_lit")
    assert weekly["song_id"] == target["id"]
    assert weekly["is_demo_data"] is False


def test_resonance_rejects_unknown_resources(client, auth_headers):
    missing_song = client.get(
        "/api/v1/resonance?song_id=missing&province_code=guangdong", headers=auth_headers
    )
    assert missing_song.status_code == 404
    assert missing_song.json()["error_code"] == "SONG_NOT_FOUND"

    placeholder = client.get(
        "/api/v1/resonance?song_id=missing&province_code=zhejiang", headers=auth_headers
    )
    assert placeholder.status_code == 422
    assert placeholder.json()["error_code"] == "PROVINCE_NOT_AVAILABLE"

