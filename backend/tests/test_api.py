def test_health_check(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "ok"


def test_create_anonymous_session_and_get_me(client):
    session_response = client.post("/api/v1/sessions/anonymous")
    assert session_response.status_code == 201
    payload = session_response.json()["data"]
    assert payload["token_type"] == "bearer"
    assert payload["user"]["display_name"] == "音乐旅人"

    me_response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer {}".format(payload["access_token"])},
    )
    assert me_response.status_code == 200
    assert me_response.json()["data"]["id"] == payload["user"]["id"]


def test_missing_token_uses_unified_error(client):
    response = client.get("/api/v1/songs")
    assert response.status_code == 401
    assert response.json()["error_code"] == "AUTH_TOKEN_MISSING"


def test_song_list_and_lyrics(client, auth_headers):
    response = client.get("/api/v1/songs?province_code=guangdong", headers=auth_headers)
    assert response.status_code == 200
    songs = response.json()["data"]["items"]
    assert len(songs) == 8
    assert {song["title"] for song in songs}.issuperset(
        {"海阔天空", "成都", "董小姐", "理想三旬", "斑马斑马"}
    )
    assert all("guangdong" in song["province_codes"] for song in songs)

    song_id = songs[0]["id"]
    lyric_response = client.get(
        "/api/v1/songs/{}/lyrics?limit=3".format(song_id),
        headers=auth_headers,
    )
    assert lyric_response.status_code == 200
    assert len(lyric_response.json()["data"]["items"]) == 3


def test_province_availability(client, auth_headers):
    response = client.get("/api/v1/provinces", headers=auth_headers)
    assert response.status_code == 200
    provinces = {item["code"]: item for item in response.json()["data"]["items"]}
    assert provinces["guangdong"]["status"] == "available"
    assert provinces["shaanxi"]["status"] == "available"
    assert provinces["zhejiang"]["status"] == "placeholder"
    assert provinces["guangdong"]["ticket_count"] == 0


def test_not_found_errors(client, auth_headers):
    song_response = client.get("/api/v1/songs/not-found", headers=auth_headers)
    assert song_response.status_code == 404
    assert song_response.json()["error_code"] == "SONG_NOT_FOUND"

    province_response = client.get("/api/v1/provinces/not-found", headers=auth_headers)
    assert province_response.status_code == 404
    assert province_response.json()["error_code"] == "PROVINCE_NOT_FOUND"
