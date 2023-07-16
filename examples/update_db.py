from circleapi import UserToken, setup_queue_logging as circleapi_log_queue
from circledb import (
    update_beatmap_threadpool,
    setup_queue_logging as circledb_log_queue,
    update_lb_multithread,
    update_country_lb_from_global_lb,
    update_best_rank_from_lb
)
from dotenv import dotenv_values
import shutil


if __name__ == "__main__":
    DB_PATH = "data.db"
    LOG_PATH = "update.log"

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

    # Update db content:
    # Beatmap
    update_beatmap_threadpool(token, DB_PATH, skip_if_in_db=True)

    # Global leaderboard
    failed = update_lb_multithread(token, DB_PATH, "osu", "global", skip_if_in_db=True)
    if len(failed) > 0:
        update_lb_multithread(token, DB_PATH, "osu", "global", skip_if_in_db=True)

    # User country lb
    update_country_lb_from_global_lb(DB_PATH)
    failed = update_lb_multithread(token, DB_PATH, "osu", "country", skip_if_in_db=True, max_threads=12)
    if len(failed) > 0:
        update_lb_multithread(token, DB_PATH, "osu", "country", skip_if_in_db=True, max_threads=12)

    # Country best rank on lb
    update_best_rank_from_lb(DB_PATH)


    log_db.stop()
    log_api.stop()
