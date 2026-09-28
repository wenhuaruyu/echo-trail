from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserOut(BaseModel):
    id: str
    display_name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnonymousSessionOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

