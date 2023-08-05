import concurrent.futures
from circleapi import ApiV2, GameMode, ScoreScope, Score, BeatmapScores, Beatmaps
from circleutils import OSUFile
import tarfile
from .circledb import CircleDB, DBBestRank
from .logger import logger
import polars as pl


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


def update_spinner_from_monthly_dump(dump_path: str, orm: CircleDB, id_filter):
    mods_combination = [
        ["DT", "HR"],
        ["EZ", "DT"],
        ["DT"],
        ["HR"],
        ["EZ"],
        []
    ]

    maps_df_list = []
    with tarfile.open(dump_path, "r:bz2") as tar:
        for i, file in enumerate(tar):
            if file.isdir():
                continue

            map_id = int(file.name.split("/")[-1].split(".")[0])

            if map_id not in id_filter:
                continue

            content = tar.extractfile(file)
            beatmap = OSUFile.read(content)

            spinners = beatmap.get_spinner_data(mods_combination)
            combo = beatmap.get_combo_data()

            spinner_at = combo.at_combo[beatmap.hit_objects.spinner_mask]

            to_concat = []
            for data in spinners:
                spinners_df = pl.DataFrame({
                    "length": data.length,
                    "max_rot": data.max_rot,
                    "leeway": data.leeway,
                    "amount": data.amount,
                    "extra_100": data.extra_100,
                    "odd": data.odd,
                    "accel_adjusted": data.accel_adjusted
                })
                spinners_df = spinners_df.select(
                    pl.lit(spinner_at).alias("at_combo"),
                    pl.lit("DT" in data.mods).alias("DT"),
                    pl.lit("HR" in data.mods).alias("HR"),
                    pl.lit("EZ" in data.mods).alias("EZ"),
                    pl.all()
                )
                to_concat.append(spinners_df)
            df = pl.concat(to_concat)
            df = df.select(
                pl.lit(map_id).alias("id").cast(pl.Int64),
                pl.all()
            )
            maps_df_list.append(df)
    data_df = pl.concat(maps_df_list)
    data_as_dicts = data_df.to_dicts()
    sql_args = []
    for data in data_as_dicts:
        sql_args.append(list(data.values()))
    orm.cur.executemany("insert into single_spinner_info values(?,?,?,?,?,?,?,?,?,?,?,?)", sql_args)
    orm.save()

    data_df = data_df.groupby(["id", "DT", "HR", "EZ"]).agg(
        pl.min("leeway").alias("min_spinner_leeway"),
        pl.mean("leeway").alias("avg_spinner_leeway"),
        pl.max("leeway").alias("max_spinner_leeway"),
        pl.min("length").alias("min_spinner_length"),
        pl.mean("length").alias("avg_spinner_length"),
        pl.max("length").alias("max_spinner_length"),
        pl.min("at_combo").alias("min_at_spinner_combo"),
        pl.mean("at_combo").alias("avg_spinner_at_combo"),
        pl.max("at_combo").alias("max_spinner_at_combo"),
    )
    data_as_dicts = data_df.to_dicts()
    sql_args = []
    for data in data_as_dicts:
        sql_args.append(list(data.values()))
    orm.cur.executemany("insert into beatmap_spinner_info values(?,?,?,?,?,?,?,?,?,?,?,?,?)", sql_args)
    orm.save()
