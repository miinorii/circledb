import threading
from datetime import datetime
import sqlite3
from circleapi import BeatmapExtended, BeatmapsExtended, BeatmapScores, BeatmapsetExtended, Score, User
from typing import Literal
from zoneinfo import ZoneInfo
from .models import DBBestRank
from .logger import logger


class CircleDB:
    def __init__(self, database, *args, **kwargs):
        self.db = sqlite3.Connection(database, *args, **kwargs)
        self.cur = self.db.cursor()
        self.queue = {}
        self.lock = threading.Lock()

    def __enter__(self):
        self.db.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.__exit__(exc_type, exc_val, exc_tb)

    def add_to_queue(self, query: str, args: tuple):
        with self.lock:
            if query not in self.queue:
                self.queue[query] = set()
            self.queue[query].add(args)

    def save(self):
        with self.lock:
            total_element = 0
            for q, a in self.queue.items():
                total_element += len(a)
                self.cur.executemany(q, a)
            self.db.commit()
            logger.info(f"[  \033[32mOK\033[0m  ] Inserted {total_element} elements")
            self.queue = {}

    def update_country_lb_from_global_lb(self, on_conflict: Literal["error", "ignore", "replace"]="error"):
        match on_conflict:
            case "ignore":
                conflict = "or ignore"
            case "replace":
                conflict = "or replace"
            case _:
                conflict = ""

        query = f"""
        insert {conflict} into country_lb
        select 
            user.country_code, 
            score.beatmap_id, 
            rank() over (
                partition by global_lb.beatmap_id, user.country_code order by global_lb.rank asc
            ) as rank,	
            score.id 
        from global_lb
            inner join score on score.id = global_lb.score_id
            inner join user on user.id = score.user_id
        """
        self.add_to_queue(query, tuple())

    def update_best_rank_from_lb(self, on_conflict: Literal["error", "ignore", "replace"]="error"):
        match on_conflict:
            case "ignore":
                conflict = "or ignore"
            case "replace":
                conflict = "or replace"
            case _:
                conflict = ""

        query = f"""
        insert {conflict} into best_rank 
        select 
            country_code, global_lb.beatmap_id, global_lb.rank, global_lb.score_id 
        from 
            country_lb, global_lb 
        where 
            global_lb.score_id = country_lb.score_id 
            and country_lb.rank = 1
        """
        self.add_to_queue(query, tuple())

    def add_beatmapset(self, beatmapset: BeatmapsetExtended, on_conflict: Literal["error", "ignore", "replace"]="error"):
        args = (
            beatmapset.id,
            beatmapset.title,
            beatmapset.artist,
            beatmapset.source if beatmapset.source else None,
            beatmapset.creator,
            beatmapset.user_id,
            beatmapset.status,
            beatmapset.bpm,
            beatmapset.play_count,
            beatmapset.favourite_count,
            beatmapset.tags if beatmapset.tags else None,
            str(beatmapset.ranked_date) if beatmapset.ranked_date else None,
            str(beatmapset.last_updated) if beatmapset.last_updated else None,
            str(beatmapset.submitted_date) if beatmapset.submitted_date else None,
            beatmapset.offset if beatmapset.offset else 0,
            int(beatmapset.availability.download_disabled),
            int(beatmapset.nsfw),
            int(beatmapset.video),
            int(beatmapset.storyboard)
        )
        match on_conflict:
            case "ignore":
                query = f"insert or ignore into beatmapset values ({','.join(['?'] * len(args))})"
            case "replace":
                query = f"insert or replace into beatmapset values ({','.join(['?'] * len(args))})"
            case _:
                query = f"insert into beatmapset values ({','.join(['?']*len(args))})"
        self.add_to_queue(query, args)

    def add_beatmap(self, beatmap: BeatmapExtended, on_conflict: Literal["error", "ignore", "replace"]="error"):
        self.add_beatmapset(beatmap.beatmapset, on_conflict=on_conflict)
        args = (
            beatmap.id,
            beatmap.difficulty_rating,
            beatmap.ar,
            beatmap.cs,
            beatmap.drain,
            beatmap.accuracy,
            beatmap.bpm,
            beatmap.count_spinners,
            beatmap.max_combo,
            beatmap.count_circles,
            beatmap.count_sliders,
            beatmap.hit_length,
            beatmap.total_length,
            beatmap.passcount,
            beatmap.playcount,
            beatmap.url,
            f"osu://b/{beatmap.id}",
            beatmap.version,
            beatmap.beatmapset_id,
            beatmap.checksum
        )

        match on_conflict:
            case "ignore":
                query = f"insert or ignore into beatmap values ({','.join(['?'] * len(args))})"
            case "replace":
                query = f"insert or replace into beatmap values ({','.join(['?'] * len(args))})"
            case _:
                query = f"insert into beatmap values ({','.join(['?']*len(args))})"
        self.add_to_queue(query, args)

    def add_beatmaps(self, beatmaps: BeatmapsExtended, on_conflict: Literal["error", "ignore", "replace"]="error"):
        for beatmap in beatmaps.beatmaps:
            self.add_beatmap(beatmap, on_conflict=on_conflict)

    def add_user(self, user: User, on_conflict: Literal["error", "ignore", "replace"]="error"):
        args = (
            user.id,
            user.username,
            user.country.code
        )
        match on_conflict:
            case "ignore":
                query = f"insert or ignore into user values ({','.join(['?'] * len(args))})"
            case "replace":
                query = f"insert or replace into user values ({','.join(['?'] * len(args))})"
            case _:
                query = f"insert into user values ({','.join(['?'] * len(args))})"
        self.add_to_queue(query, args)

    def add_score(self, score: Score, beatmap_id, on_conflict: Literal["error", "ignore", "replace"]="error"):
        if score.user:
            self.add_user(score.user, on_conflict=on_conflict)
        args = (
            score.id,
            beatmap_id,
            score.user_id,
            score.accuracy * 100,
            score.max_combo,
            score.rank,
            score.pp if score.pp else None,
            score.score,
            1 if "HD" in score.mods else 0,
            1 if "DT" in score.mods else 0,
            1 if "NC" in score.mods else 0,
            1 if "HR" in score.mods else 0,
            1 if "FL" in score.mods else 0,
            1 if "EZ" in score.mods else 0,
            1 if "NF" in score.mods else 0,
            1 if "SO" in score.mods else 0,
            1 if "HT" in score.mods else 0,
            1 if "SD" in score.mods else 0,
            1 if "PF" in score.mods else 0,
            1 if "TD" in score.mods else 0,
            score.statistics.count_300,
            score.statistics.count_100,
            score.statistics.count_50,
            score.statistics.count_geki,
            score.statistics.count_katu,
            score.statistics.count_miss,
            int(score.replay),
            score.mode,
            str(score.created_at),
            str(datetime.now(tz=ZoneInfo("utc")))
        )
        match on_conflict:
            case "ignore":
                query = f"insert or ignore into score values ({','.join(['?'] * len(args))})"
            case "replace":
                query = f"insert or replace into score values ({','.join(['?'] * len(args))})"
            case _:
                query = f"insert into score values ({','.join(['?'] * len(args))})"
        self.add_to_queue(query, args)

    def add_lb(self,
               lb: BeatmapScores,
               on_conflict: Literal["error", "ignore", "replace"]="error"):
        for index, score in enumerate(lb.scores):
            self.add_score(score, lb.beatmap_id, on_conflict=on_conflict)
            rank = index + 1
            match lb.scope:
                case "global":
                    args = (lb.beatmap_id, rank, score.id)
                    match on_conflict:
                        case "ignore":
                            query = f"insert or ignore into global_lb values ({','.join(['?'] * len(args))})"
                        case "replace":
                            query = f"insert or replace into global_lb values ({','.join(['?'] * len(args))})"
                        case _:
                            query = f"insert into global_lb values ({','.join(['?'] * len(args))})"
                case "country":
                    args = (score.user.country.code, lb.beatmap_id, rank, score.id)
                    match on_conflict:
                        case "ignore":
                            query = f"insert or ignore into country_lb values ({','.join(['?'] * len(args))})"
                        case "replace":
                            query = f"insert or replace into country_lb values ({','.join(['?'] * len(args))})"
                        case _:
                            query = f"insert into country_lb values ({','.join(['?'] * len(args))})"
            self.add_to_queue(query, args)

    def add_best_rank(self, best_rank: DBBestRank, on_conflict: Literal["error", "ignore", "replace"]="error"):
        args = (best_rank.country_code,
                best_rank.beatmap_id,
                best_rank.rank,
                best_rank.score_id)
        match on_conflict:
            case "ignore":
                query = f"insert or ignore into best_rank values ({','.join(['?'] * len(args))})"
            case "replace":
                query = f"insert or replace into best_rank values ({','.join(['?'] * len(args))})"
            case _:
                query = f"insert into best_rank values ({','.join(['?'] * len(args))})"
        self.add_to_queue(query, args)

    def get_beatmap_in_db(self) -> set[int]:
        with self.lock:
            self.cur.execute("select id from beatmap")
            data = self.cur.fetchall()
        return set(x[0] for x in data)

    def get_lb_in_db(self, scope: Literal["global", "country"], country_code: str | None = None) -> set[int]:
        with self.lock:
            match scope:
                case "global":
                    self.cur.execute("select distinct beatmap_id from global_lb")
                case "country":
                    self.cur.execute(f"select distinct beatmap_id from country_lb where country_code='{country_code}'")
                case _:
                    raise NotImplementedError
            data = self.cur.fetchall()
        return set(x[0] for x in data)

    def get_best_rank(self,
                      country_code: list[str] | None = None,
                      rank: list[int] | None = None) -> list[DBBestRank]:
        condition = ""
        if country_code:
            cc_args = ",".join([f"'{x}'" for x in country_code])
            filter = f"country_code in ({cc_args})"
            condition = f"where {filter}"
        if rank:
            rank_args = ",".join([str(x) for x in rank])
            filter = f"rank in ({rank_args})"
            if not condition:
                condition = f"where {filter}"
            else:
                condition = f"{condition} and {filter}"

        with self.lock:
            self.cur.execute(f"select * from best_rank {condition}")
            data = self.cur.fetchall()
        data = [DBBestRank(
            country_code=cc,
            beatmap_id=bid,
            rank=rank,
            score_id=sid) for cc, bid, rank, sid in data]
        return data

    def get_score_id_needing_manual_best_rank_check(self, country_code: str) -> list[int]:
        query = """
        select 
            score_id 
        from country_lb 
        where 
            rank=1 
            and country_code=? 
            and score_id not in (select score_id from global_lb) 
            and score_id not in (select score_id from best_rank)
        """
        with self.lock:
            self.cur.execute(query, [country_code])
            data = self.cur.fetchall()
        return [x[0] for x in data]

    def get_missing_beatmap_id_from_best_rank(self, country_code: str) -> list[int]:
        query = """
        select id from beatmap where id not in (
            select beatmap_id 
            from best_rank 
            where country_code = ?
        )
        """
        with self.lock:
            self.cur.execute(query, [country_code])
            data = self.cur.fetchall()
        return [x[0] for x in data]

    def get_map_checksum_out_of_country_top100(self, country_code: str) -> list[str]:
        with self.lock:
            self.cur.execute(f"select beatmap.checksum from best_rank, beatmap where best_rank.beatmap_id = beatmap.id and best_rank.country_code = '{country_code}' and (best_rank.rank is null or best_rank.rank > 100)")
            data = self.cur.fetchall()
        return [x[0] for x in data]

    def get_data_for_id_sheets(self):
        with self.lock:
            self.cur.execute("select beatmap.url, beatmap.id, beatmap.star, beatmapset.ranked_date, best_rank.rank from best_rank, beatmap, beatmapset where best_rank.country_code = 'FR' and best_rank.beatmap_id = beatmap.id and beatmap.beatmapset_id = beatmapset.id and beatmapset.status in ('ranked', 'loved', 'approved')")
            data = self.cur.fetchall()
        return data
