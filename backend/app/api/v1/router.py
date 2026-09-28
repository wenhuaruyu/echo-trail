from fastapi import APIRouter

from app.api.v1.routes import health, play_events, provinces, resonance, sessions, songs, tickets, users


api_router = APIRouter()
api_router.include_router(health.router, tags=["系统"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["匿名会话"])
api_router.include_router(users.router, prefix="/users", tags=["用户"])
api_router.include_router(songs.router, prefix="/songs", tags=["歌曲"])
api_router.include_router(provinces.router, prefix="/provinces", tags=["省份"])
api_router.include_router(play_events.router, prefix="/play-events", tags=["播放记录"])
api_router.include_router(tickets.router, prefix="/tickets", tags=["票根"])
api_router.include_router(resonance.router, prefix="/resonance", tags=["共鸣统计"])
