import uuid
from io import BytesIO
from urllib.parse import urlparse

from PIL import Image


def make_image(image_format="PNG", size=(80, 60), with_exif=False):
    output = BytesIO()
    image = Image.new("RGB", size, color=(35, 83, 67))
    kwargs = {}
    if with_exif:
        exif = Image.Exif()
        exif[315] = "Echo Trail Test"
        kwargs["exif"] = exif
    image.save(output, format=image_format, **kwargs)
    return output.getvalue()


def upload(client, headers, content, filename="photo.png", content_type="image/png"):
    return client.post(
        "/api/v1/uploads/ticket-photo",
        headers=headers,
        files={"file": (filename, content, content_type)},
    )


def create_identity(client):
    response = client.post("/api/v1/sessions/anonymous")
    token = response.json()["data"]["access_token"]
    return {"Authorization": "Bearer {}".format(token)}


def test_upload_requires_authentication(client):
    response = upload(client, {}, make_image())
    assert response.status_code == 401
    assert response.json()["error_code"] == "AUTH_TOKEN_MISSING"


def test_jpeg_png_and_webp_are_reencoded_and_accessible(client, auth_headers):
    urls = []
    for image_format, suffix, content_type in (
        ("JPEG", "jpg", "image/jpeg"),
        ("PNG", "png", "image/png"),
        ("WEBP", "webp", "image/webp"),
    ):
        response = upload(
            client,
            auth_headers,
            make_image(image_format),
            "same-name.{}".format(suffix),
            content_type,
        )
        assert response.status_code == 201
        data = response.json()["data"]
        assert data["format"] == "webp"
        assert data["photo_url"].endswith(".webp")
        urls.append(data["photo_url"])
        file_response = client.get(urlparse(data["photo_url"]).path)
        assert file_response.status_code == 200
        assert file_response.headers["content-type"] == "image/webp"
    assert len(set(urls)) == 3


def test_fake_unsupported_and_oversized_files_are_rejected(client, auth_headers):
    fake = upload(client, auth_headers, b"not an image", "fake.jpg", "image/jpeg")
    assert fake.status_code == 415
    assert fake.json()["error_code"] == "UPLOAD_TYPE_NOT_SUPPORTED"

    gif = upload(client, auth_headers, make_image("GIF"), "moving.gif", "image/gif")
    assert gif.status_code == 415
    assert gif.json()["error_code"] == "UPLOAD_TYPE_NOT_SUPPORTED"

    oversized = upload(client, auth_headers, b"x" * (5 * 1024 * 1024 + 1), "large.png")
    assert oversized.status_code == 413
    assert oversized.json()["error_code"] == "UPLOAD_TOO_LARGE"


def test_large_image_is_resized_and_exif_removed(client, auth_headers):
    response = upload(
        client,
        auth_headers,
        make_image("JPEG", size=(3000, 100), with_exif=True),
        "wide.jpg",
        "image/jpeg",
    )
    assert response.status_code == 201
    data = response.json()["data"]
    assert max(data["width"], data["height"]) == 2048
    stored = client.get(urlparse(data["photo_url"]).path).content
    with Image.open(BytesIO(stored)) as image:
        assert image.format == "WEBP"
        assert len(image.getexif()) == 0


def test_silver_ticket_accepts_uploaded_photo_and_rejects_external_url(client):
    headers = create_identity(client)
    song = client.get("/api/v1/songs?province_code=guangdong", headers=headers).json()["data"]["items"][0]
    lyric = client.get("/api/v1/songs/{}/lyrics".format(song["id"]), headers=headers).json()["data"]["items"][0]
    event = client.post(
        "/api/v1/play-events",
        headers=headers,
        json={"song_id": song["id"], "event_type": "started"},
    ).json()["data"]
    base_payload = {
        "song_id": song["id"],
        "play_event_id": event["play_event_id"],
        "province_code": "guangdong",
        "ticket_type": "silver",
        "message": "旅途影像",
        "location_text": "广州",
        "mood_tags": ["在路上"],
        "lyric_line_id": lyric["id"],
        "idempotency_key": str(uuid.uuid4()),
    }

    external_payload = dict(base_payload, photo_url="https://example.com/photo.jpg")
    rejected = client.post("/api/v1/tickets", headers=headers, json=external_payload)
    assert rejected.status_code == 422
    assert rejected.json()["error_code"] == "TICKET_PHOTO_INVALID"

    uploaded = upload(client, headers, make_image()).json()["data"]["photo_url"]
    valid_payload = dict(base_payload, photo_url=uploaded, idempotency_key=str(uuid.uuid4()))
    accepted = client.post("/api/v1/tickets", headers=headers, json=valid_payload)
    assert accepted.status_code == 201
    assert accepted.json()["data"]["ticket"]["photo_url"] == uploaded

