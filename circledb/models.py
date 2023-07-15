from pydantic import BaseModel


class DBBestRank(BaseModel):
    country_code: str
    beatmap_id: int
    rank: int | None = None
    score_id: int | None = None
