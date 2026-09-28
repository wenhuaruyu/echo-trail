from typing import Literal

from pydantic import BaseModel


class PlayEventCreate(BaseModel):
    song_id: str
    event_type: Literal["started"] = "started"

