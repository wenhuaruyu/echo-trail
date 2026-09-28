from datetime import datetime, timezone
from typing import Dict, List

from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.repositories.province_repository import get_province
from app.repositories.song_repository import get_song
from app.repositories.statistics_repository import (
    count_resonating_users,
    get_resonance_baseline,
    list_insights,
    mood_counts,
    weekly_top_song,
)


SCENE_ORDER = [
    "weekly_most_lit",
    "daily_theme",
    "rainy_most_lit",
    "late_night_most_lit",
    "traveler_favorite",
]


def get_resonance(db: Session, province_code: str, song_id: str) -> Dict[str, object]:
    province = get_province(db, province_code)
    if province is None:
        raise AppError(404, "PROVINCE_NOT_FOUND", "省份不存在")
    if province.status != "available":
        raise AppError(422, "PROVINCE_NOT_AVAILABLE", "当前省份暂未开放共鸣统计")
    song = get_song(db, song_id)
    if song is None:
        raise AppError(404, "SONG_NOT_FOUND", "歌曲不存在")
    baseline = get_resonance_baseline(db, province_code, song_id)
    base_count = baseline.base_count if baseline else 0
    real_user_count = count_resonating_users(db, province_code, song_id)
    count = base_count + real_user_count
    return {
        "song_id": song_id,
        "province_code": province_code,
        "count": count,
        "real_user_count": real_user_count,
        "base_count": base_count,
        "display_text": "已有{:,}位音乐旅人在{}点亮过这首歌".format(count, province.name),
        "is_demo_data": base_count > 0,
    }


def _percentages(counts: Dict[str, int]) -> List[Dict[str, object]]:
    total = sum(counts.values())
    if total == 0:
        return []
    exact = {key: value * 100 / total for key, value in counts.items()}
    result = {key: int(value) for key, value in exact.items()}
    remaining = 100 - sum(result.values())
    ranked = sorted(counts, key=lambda key: (exact[key] - result[key], counts[key]), reverse=True)
    for key in ranked[:remaining]:
        result[key] += 1
    return [
        {"mood": key, "percentage": result[key]}
        for key in sorted(result, key=lambda item: (-result[item], item))
    ]


def get_emotion_map(db: Session, province_code: str) -> Dict[str, object]:
    province = get_province(db, province_code)
    if province is None:
        raise AppError(404, "PROVINCE_NOT_FOUND", "省份不存在")
    if province.status != "available":
        raise AppError(422, "PROVINCE_NOT_AVAILABLE", "当前省份暂未开放音乐情绪地图")

    insight_rows = list_insights(db, province_code)
    insights = {
        insight.scene: {
            "scene": insight.scene,
            "label": insight.label,
            "song_id": song.id,
            "song_title": song.title,
            "artist": song.artist,
            "is_demo_data": insight.is_demo_data,
        }
        for insight, song in insight_rows
    }

    weekly = weekly_top_song(db, province_code)
    if weekly is not None and weekly[1] >= 3:
        song, _ = weekly
        insights["weekly_most_lit"] = {
            "scene": "weekly_most_lit",
            "label": "本周最多点亮",
            "song_id": song.id,
            "song_title": song.title,
            "artist": song.artist,
            "is_demo_data": False,
        }

    ordered = [insights[scene] for scene in SCENE_ORDER if scene in insights]
    return {
        "province_code": province_code,
        "is_demo_data": any(item["is_demo_data"] for item in ordered),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "music_insights": ordered,
        "mood_distribution": _percentages(mood_counts(db, province_code)),
    }
