from sqlalchemy import select

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.lyric_line import LyricLine
from app.models.province import Province
from app.models.song import Song
from app.models.statistics import ProvinceMoodBaseline, ProvinceMusicInsight, ResonanceBaseline
from app.seed.data import MOOD_BASELINES, MUSIC_INSIGHTS, PROVINCES, RESONANCE_BASELINES, SONGS


def seed_database() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        province_map = {}
        for item in PROVINCES:
            province = db.get(Province, item["code"])
            if province is None:
                province = Province(code=item["code"], name=item["name"])
                db.add(province)
            province.name = item["name"]
            province.slogan = item.get("slogan")
            province.status = item.get("status", "placeholder")
            province_map[province.code] = province

        db.flush()

        song_map = {}
        for item in SONGS:
            song = db.scalar(select(Song).where(Song.slug == item["slug"]))
            if song is None:
                song = Song(slug=item["slug"])
                db.add(song)
            song.title = item["title"]
            song.artist = item["artist"]
            song.cover_url = "https://example.com/echo-trail/covers/{}.jpg".format(item["slug"])
            song.audio_url = "https://example.com/echo-trail/audio/{}.mp3".format(item["slug"])
            song.duration_seconds = item["duration_seconds"]
            song.scene_description = item["scene_description"]
            song.is_featured = item["is_featured"]
            song.provinces = [province_map[code] for code in item["province_codes"]]

            db.flush()
            song.lyrics.clear()
            for index, content in enumerate(item["lyrics"], start=1):
                song.lyrics.append(LyricLine(content=content, sort_order=index))
            song_map[item["slug"]] = song

        db.flush()

        for province_code, songs in RESONANCE_BASELINES.items():
            for slug, base_count in songs.items():
                key = {"province_code": province_code, "song_id": song_map[slug].id}
                baseline = db.get(ResonanceBaseline, (province_code, song_map[slug].id))
                if baseline is None:
                    baseline = ResonanceBaseline(**key)
                    db.add(baseline)
                baseline.base_count = base_count

        for province_code, insights in MUSIC_INSIGHTS.items():
            for scene, label, slug in insights:
                insight = db.scalar(
                    select(ProvinceMusicInsight).where(
                        ProvinceMusicInsight.province_code == province_code,
                        ProvinceMusicInsight.scene == scene,
                    )
                )
                if insight is None:
                    insight = ProvinceMusicInsight(province_code=province_code, scene=scene)
                    db.add(insight)
                insight.label = label
                insight.song_id = song_map[slug].id
                insight.is_demo_data = True

        for province_code, moods in MOOD_BASELINES.items():
            for mood, base_count in moods.items():
                baseline = db.get(ProvinceMoodBaseline, (province_code, mood))
                if baseline is None:
                    baseline = ProvinceMoodBaseline(province_code=province_code, mood=mood)
                    db.add(baseline)
                baseline.base_count = base_count

        db.commit()


if __name__ == "__main__":
    seed_database()
    print("演示数据初始化完成")
