from typing import List, Optional

from pydantic import BaseModel, Field


class TicketCreate(BaseModel):
    song_id: str
    play_event_id: str
    province_code: str
    ticket_type: str
    message: Optional[str] = None
    location_text: Optional[str] = None
    mood_tags: List[str] = Field(default_factory=list)
    lyric_line_id: Optional[str] = None
    photo_url: Optional[str] = None
    idempotency_key: str


class TicketFilters(BaseModel):
    province_code: Optional[str] = None
    ticket_type: Optional[str] = None
    page: int = 1
    page_size: int = 20

