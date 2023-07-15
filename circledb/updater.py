import concurrent.futures
from circleapi import ApiV2, UserToken, ExternalApi, GameMode, ScoreScope
from .circledb import CircleDB
from .logger import logger
import gc


def update_beatmap_threadpool(token: UserToken, db_path: str, skip_if_in_db=True):
    maps_id = ExternalApi.get_ranked_and_loved_ids()
    with CircleDB(db_path) as orm:
        if skip_if_in_db:
            maps_in_db = orm.get_beatmap_in_db()
            maps_id = list(set(maps_id).difference(maps_in_db))

        with ApiV2(token) as api:
            with concurrent.futures.ThreadPoolExecutor(max_workers=8, thread_name_prefix="pool") as pool:
                futures = {}
                while len(maps_id) > 0:
                    current_batch = [maps_id.pop() for _ in range(50) if len(maps_id) > 0]
                    futures[pool.submit(api.get_beatmaps, ids=current_batch)] = current_batch

                completed = 0
                total = len(futures)
                for future in concurrent.futures.as_completed(futures):
                    current_batch = futures.pop(future)
                    completed += 1
                    try:
                        data = future.result()
                    except Exception as exc:
                        logger.error(f"[  \033[1;31mERROR\033[0m  ] An exception occurred", exc_info=exc)
                    else:
                        orm.add_beatmaps(data, on_conflict="replace")
                        if completed % 32 == 0 or completed == total:
                            orm.save()
                            logger.info(f"[  \033[1;33m..\033[0m  ] Completion: {completed}/{total}")
                            gc.collect()


def update_lb_multithread(token: UserToken,
                          db_path: str,
                          mode: GameMode,
                          scope: ScoreScope,
                          skip_if_in_db=True) -> list[int]:
    maps_id = ExternalApi.get_ranked_and_loved_ids()
    with ApiV2(token) as api:
        country_code = api.get_own_data().country.code
        with CircleDB(db_path) as orm:
            if skip_if_in_db:
                lb_in_db = orm.get_lb_in_db(scope, country_code)
                maps_id = list(set(maps_id).difference(lb_in_db))

            with concurrent.futures.ThreadPoolExecutor(max_workers=8, thread_name_prefix="pool") as pool:
                futures_to_map_id = {
                    pool.submit(
                        api.get_beatmap_scores,
                        map_id,
                        mode,
                        scope=scope
                    ): map_id for map_id in maps_id}

                failed = []
                completed = 0
                total = len(futures_to_map_id)
                for future in concurrent.futures.as_completed(futures_to_map_id):
                    map_id = futures_to_map_id.pop(future)
                    completed += 1
                    try:
                        data = future.result()
                    except Exception as exc:
                        failed.append(map_id)
                        logger.error(f"[  \033[1;31mERROR\033[0m  ] An exception occurred, beatmap_id: {map_id}", exc_info=exc)
                    else:
                        orm.add_lb(data, on_conflict="replace")
                        if completed % 32 == 0 or completed == total:
                            orm.save()
                            logger.info(f"[  \033[1;33m..\033[0m  ] Completion: {completed}/{total}")
                            gc.collect()
    return failed
