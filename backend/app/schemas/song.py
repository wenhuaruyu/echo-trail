from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class LyricLineOut(BaseModel):
    id: str
    content: str
    sort_order: int

    model_config = ConfigDict(from_attributes=True)


class SongOut(BaseModel):
    id: str
    title: str
    artist: str
    cover_url: str
    audio_url: str
    duration_seconds: int
    province_codes: List[str]
    scene_description: Optional[str]
    is_featured: bool


class SongListOut(BaseModel):
    items: List[SongOut]


class LyricListOut(BaseModel):
    song_id: str
    items: List[LyricLineOut]

