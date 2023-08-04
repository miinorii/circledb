from circleapi import UserToken, ApiV2, ExternalApi, setup_queue_logging as circleapi_log_queue
from circledb import (
    CircleDB, update_beatmap_threadpool, DBBestRank,
    update_lb_threadpool, update_best_rank_from_score_id_threadpool,
    update_spinner_from_monthly_dump,
    setup_queue_logging as circledb_log_queue
)
from dotenv import dotenv_values
import shutil


if __name__ == "__main__":
    # Script used to fill an empty database
    # Average run time is ~3h at 1000 req/s

    DB_PATH = "data.db"
    LOG_PATH = "update.log"
    DUMP_PATH = r"2023_08_01_osu_files.tar.bz2"

    # Setup logging
    log_db = circledb_log_queue(to_console=True, to_file=LOG_PATH)
    log_api = circleapi_log_queue(to_console=True, to_file=LOG_PATH)
    log_db.start()
    log_api.start()

    # Setup apiv2 token
    env = dotenv_values(".env")
    token = UserToken(
        int(env["CLIENT"]),
        env["SECRET"],
        filepath="user_token"
    )

    # Setup empty db
    shutil.copy("../ressources/empty_data.db", DB_PATH)

    # Update db content
    with CircleDB(DB_PATH) as orm, ApiV2(token) as api:
        # Get all available ranked/loved beatmaps
        beatmap_ids = ExternalApi.get_ranked_and_loved_ids()

        # Update all available beatmaps
        failed = update_beatmap_threadpool(api, orm, beatmap_ids)
        if failed:
            update_beatmap_threadpool(api, orm, failed)

        # Update global leaderboards (top #50)
        failed = update_lb_threadpool(api, orm, beatmap_ids, "osu", "global", max_threads=12)
        if failed:
            update_lb_threadpool(api, orm, beatmap_ids, "osu", "global", max_threads=12)

        # Fill country leaderboards from global leaderboards
        orm.update_country_lb_from_global_lb(on_conflict="replace")
        orm.save()

        # Update remaining country leaderboards with no scores in global leaderboards
        failed = update_lb_threadpool(api, orm, beatmap_ids, "osu", "country", max_threads=12)
        if failed:
            update_lb_threadpool(api, orm, beatmap_ids, "osu", "country", max_threads=12)

        # Update "best_rank" from available leaderboards
        orm.update_best_rank_from_lb(on_conflict="replace")
        orm.save()

        # Update "best_rank" from available scores
        country_code = api.get_own_data().country.code
        score_ids = orm.get_score_id_needing_manual_best_rank_check(country_code)
        failed = update_best_rank_from_score_id_threadpool(api, orm, score_ids, "osu", max_threads=10)
        if failed:
            update_best_rank_from_score_id_threadpool(api, orm, failed, "osu", max_threads=10)

        # Update "best_rank" from missing beatmap ids
        missing_ids = orm.get_missing_beatmap_id_from_best_rank(country_code)
        for beatmap_id in missing_ids:
            orm.add_best_rank(DBBestRank(country_code=country_code, beatmap_id=beatmap_id))
        orm.save()

        # Update spinners data from monthly dump
        data = orm.cur.execute("select id from beatmap where spinners <> 0")
        id_filter = set(x[0] for x in data)

        # skip aspire maps
        aspire_maps = {2573166, 2573162, 2573163, 2573167, 2573165, 2628991, 2573161, 2619200, 2571051, 2573164}
        id_filter = id_filter.difference(aspire_maps)

        update_spinner_from_monthly_dump(DUMP_PATH, orm, id_filter)

    log_db.stop()
    log_api.stop()
