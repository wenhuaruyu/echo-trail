from typing import Dict

from app.models.song import Song


def serialize_song(song: Song) -> Dict[str, object]:
    return {
        "id": song.id,
        "title": song.title,
        "artist": song.artist,
        "cover_url": song.cover_url,
        "audio_url": song.audio_url,
        "duration_seconds": song.duration_seconds,
        "province_codes": [province.code for province in song.provinces],
        "scene_description": song.scene_description,
        "is_featured": song.is_featured,
    }

