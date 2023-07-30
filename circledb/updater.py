import concurrent.futures
from circleapi import ApiV2, GameMode, ScoreScope, Score, BeatmapScores, Beatmaps
from .circledb import CircleDB, DBBestRank
from .logger import logger


def update_beatmap_threadpool(api: ApiV2,
                              orm: CircleDB,
                              beatmap_ids: list[int],
                              max_threads=8,
                              skip_if_in_db=True) -> list[int]:
    _beatmap_ids = beatmap_ids[:]
    if skip_if_in_db:
        beatmap_ids_in_db = orm.get_beatmap_in_db()
        _beatmap_ids = list(set(_beatmap_ids).difference(beatmap_ids_in_db))
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads, thread_name_prefix="pool") as pool:
        futures = {}
        while len(_beatmap_ids) > 0:
            current_batch = [_beatmap_ids.pop() for _ in range(50) if len(_beatmap_ids) > 0]
            futures[pool.submit(api.get_beatmaps, ids=current_batch)] = current_batch

        completed = 0
        failed = []
        total = len(futures)
        for future in concurrent.futures.as_completed(futures):
            current_batch = futures.pop(future)
            completed += 1
            try:
                data: Beatmaps = future.result()
            except Exception as exc:
                failed += current_batch
                logger.error(f"[  \033[1;31mERROR\033[0m  ] An exception occurred, {current_batch=}", exc_info=exc)
            else:
                orm.add_beatmaps(data, on_conflict="replace")
                if completed % 32 == 0 or completed == total:
                    orm.save()
                    logger.info(f"[  \033[1;33m..\033[0m  ] Completion: {completed}/{total}")
    return failed


def update_lb_threadpool(api: ApiV2,
                          orm: CircleDB,
                          beatmap_ids: list[int],
                          mode: GameMode,
                          scope: ScoreScope,
                          skip_if_in_db=True,
                          max_threads=8) -> list[int]:
    _beatmap_ids = beatmap_ids[:]
    country_code = api.get_own_data().country.code if scope == "country" else None

    if skip_if_in_db:
        lb_in_db = orm.get_lb_in_db(scope, country_code)
        _beatmap_ids = list(set(_beatmap_ids).difference(lb_in_db))

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads, thread_name_prefix="pool") as pool:
        futures_to_map_id = {
            pool.submit(
                api.get_beatmap_scores,
                map_id,
                mode,
                scope=scope
            ): map_id for map_id in _beatmap_ids}

        failed = []
        completed = 0
        total = len(futures_to_map_id)
        for future in concurrent.futures.as_completed(futures_to_map_id):
            map_id = futures_to_map_id.pop(future)
            completed += 1
            try:
                data: BeatmapScores = future.result()
            except Exception as exc:
                failed.append(map_id)
                logger.error(f"[  \033[1;31mERROR\033[0m  ] An exception occurred, beatmap_id: {map_id}", exc_info=exc)
            else:
                orm.add_lb(data, on_conflict="replace")
                if completed % 32 == 0 or completed == total:
                    orm.save()
                    logger.info(f"[  \033[1;33m..\033[0m  ] Completion: {completed}/{total}")
    return failed


def update_best_rank_from_score_id_threadpool(api: ApiV2,
                          orm: CircleDB,
                          score_ids: list[int],
                          mode: GameMode,
                          max_threads=8) -> list[int]:
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads, thread_name_prefix="pool") as pool:
        futures_to_scores = {
            pool.submit(
                api.get_score,
                mode,
                score_id
            ): score_id for score_id in score_ids}

        failed = []
        completed = 0
        total = len(futures_to_scores)
        for future in concurrent.futures.as_completed(futures_to_scores):
            score_id = futures_to_scores.pop(future)
            completed += 1
            try:
                data: Score = future.result()
            except Exception as exc:
                failed.append(score_id)
                logger.error(f"[  \033[1;31mERROR\033[0m  ] An exception occurred, score_id: {score_id}", exc_info=exc)
            else:
                to_insert = DBBestRank(
                    country_code=data.user.country.code,
                    beatmap_id=data.beatmap.id,
                    rank=data.rank_global,
                    score_id=data.id
                )
                orm.add_best_rank(to_insert, on_conflict="replace")
                if completed % 32 == 0 or completed == total:
                    orm.save()
                    logger.info(f"[  \033[1;33m..\033[0m  ] Completion: {completed}/{total}")
    return failed
