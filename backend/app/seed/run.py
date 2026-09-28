from sqlalchemy import select

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.lyric_line import LyricLine
from app.models.province import Province
from app.models.song import Song
from app.seed.data import PROVINCES, SONGS


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

        db.commit()


if __name__ == "__main__":
    seed_database()
    print("演示数据初始化完成")

