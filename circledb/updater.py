import concurrent.futures
from circleapi import ApiV2, UserToken, ExternalApi
from .circledb import CircleDB
from .logger import logger


def update_beatmap_threadpool(token: UserToken, db_path: str, skip_if_in_db=True):
    maps_id = ExternalApi.get_ranked_and_loved_ids()
    with CircleDB(db_path) as orm:
        if skip_if_in_db:
            maps_in_db = orm.get_beatmap_in_db()
            maps_id = list(set(maps_id).difference(maps_in_db))

        with ApiV2(token) as api:
            with concurrent.futures.ThreadPoolExecutor(max_workers=8, thread_name_prefix="pool") as pool:
                futures = []
                while len(maps_id) > 0:
                    current_batch = [maps_id.pop() for _ in range(50) if len(maps_id) > 0]
                    futures.append(pool.submit(api.get_beatmaps, ids=current_batch))

                completed = 0
                total = len(futures)
                for future in concurrent.futures.as_completed(futures):
                    completed += 1
                    try:
                        data = future.result()
                    except Exception as exc:
                        logger.error(f"[  \033[1;31mERROR\033[0m  ] An exception occurred", exc_info=exc)
                    else:
                        orm.add_beatmaps(data, on_conflict="replace")
                        if completed % 10 == 0 or completed == total:
                            orm.save()
                    logger.info(f"[  \033[1;33m..\033[0m  ] Completion: {completed}/{total}")
