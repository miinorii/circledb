circledb
---------

A set of tools to query, store and reuse data from osu! api.

If you want to fill the database, look at the "examples" folder.

A complete update take around 3 to 4 hours at 1000 api request per minute.

Main features
-------------

- ORM to insert osu!apiv2 responses directly
- Ready to use database schema
- Ready to use update script
- Use of threadpools for massive concurrent updates

Database schema
---------------

- Beatmap leaderboards (global/country)
- Beatmaps data
- Beatmapsets data
- Scores
- Spinners data
- Users
- Country best rank per beatmap

Installation
-----------

Development setup
```bash
$ git clone https://github.com/miinorii/circledb.git
$ cd circledb
$ pip install -r requirements.txt
$ pip install -e .
```


