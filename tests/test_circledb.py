import unittest
from circleapi import BeatmapExtended, BeatmapsExtended, BeatmapsetExtended, BeatmapScores, User
from circledb import CircleDB, DBBestRank
import msgspec


SAMPLE_BEATMAP = msgspec.json.decode(
    b'{"beatmapset_id":3,"difficulty_rating":2.16,"id":53,"mode":"osu","status":"ranked","total_length":83,"user_id":141,"version":"-Crusin-","beatmapset":{"artist":"Ni-Ni","artist_unicode":"Ni-Ni","covers":{"cover":"https://assets.ppy.sh/beatmaps/3/covers/cover.jpg?1622017885","cover@2x":"https://assets.ppy.sh/beatmaps/3/covers/cover@2x.jpg?1622017885","card":"https://assets.ppy.sh/beatmaps/3/covers/card.jpg?1622017885","card@2x":"https://assets.ppy.sh/beatmaps/3/covers/card@2x.jpg?1622017885","list":"https://assets.ppy.sh/beatmaps/3/covers/list.jpg?1622017885","list@2x":"https://assets.ppy.sh/beatmaps/3/covers/list@2x.jpg?1622017885","slimcover":"https://assets.ppy.sh/beatmaps/3/covers/slimcover.jpg?1622017885","slimcover@2x":"https://assets.ppy.sh/beatmaps/3/covers/slimcover@2x.jpg?1622017885"},"creator":"MCXD","favourite_count":255,"id":3,"nsfw":false,"play_count":629247,"preview_url":"//b.ppy.sh/preview/3.mp3","source":"","status":"ranked","spotlight":false,"title":"1,2,3,4, 007 [Wipeout Series]","title_unicode":"1,2,3,4, 007 [Wipeout Series]","user_id":141,"video":false,"offset":40,"beatmaps":null,"has_favourited":null,"nominations_summary":{"current":0,"required":2},"pack_tags":null,"ratings":[0,147,50,46,45,82,127,189,228,177,902],"track_id":null,"availability":{"download_disabled":false,"more_information":null},"bpm":172.0,"can_be_hyped":false,"discussion_locked":false,"is_scoreable":true,"last_updated":"2007-10-06T19:32:02Z","nominations":null,"ranked":1,"storyboard":false,"tags":"","hype":null,"legacy_thread_url":"https://osu.ppy.sh/community/forums/topics/65","submitted_date":"2007-10-06T19:32:02Z","ranked_date":"2007-10-06T19:32:02Z","deleted_at":null,"discussion_enabled":true},"max_combo":124,"checksum":"1d23c37a2fda439be752ae2bca06c0cd","failtimes":{"exit":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,9,0,1,0,0,9,78,462,145,304,330,2024,1056,965,1030,1161,323,101,306,662,449,1311,1269,1036,2568,2668,1504,805,753,579,652,782,764,1206,541,379,613,457,370,348,470,357,367,536,510,422,751,720,527,346,354,294,623,907,635,440,444,219,152,138,110,86,134,134,91,66,69,88,142,120,133,83,49,133,91,105,117,101,78,107,228,809],"fail":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,15,12,5,4,7,10,5,14,99,14,139,86,589,130,168,115,31,2,58,100,97,93,320,129,175,522,524,123,175,226,265,276,272,396,264,180,181,391,153,147,249,292,291,370,463,681,127,385,304,209,351,225,280,313,444,311,409,495,161,46,80,106,101,66,78,15,36,81,153,159,121,120,119,102,214,233,167,171,116,140,64,71,77,83]},"accuracy":4.0,"ar":4.0,"convert":false,"count_circles":67,"count_sliders":15,"count_spinners":1,"cs":5.0,"drain":3.0,"hit_length":77,"is_scoreable":true,"last_updated":"2014-05-18T16:56:27Z","mode_int":0,"passcount":57129,"playcount":124191,"ranked":1,"url":"https://osu.ppy.sh/beatmaps/53","deleted_at":null,"bpm":172.0}', # noqa
    type=BeatmapExtended, strict=False
)
SAMPLE_BEATMAPS = msgspec.json.decode(
    b'{"beatmaps":[{"beatmapset_id":3,"difficulty_rating":2.16,"id":53,"mode":"osu","status":"ranked","total_length":83,"user_id":141,"version":"-Crusin-","beatmapset":{"artist":"Ni-Ni","artist_unicode":"Ni-Ni","covers":{"cover":"https://assets.ppy.sh/beatmaps/3/covers/cover.jpg?1622017885","cover@2x":"https://assets.ppy.sh/beatmaps/3/covers/cover@2x.jpg?1622017885","card":"https://assets.ppy.sh/beatmaps/3/covers/card.jpg?1622017885","card@2x":"https://assets.ppy.sh/beatmaps/3/covers/card@2x.jpg?1622017885","list":"https://assets.ppy.sh/beatmaps/3/covers/list.jpg?1622017885","list@2x":"https://assets.ppy.sh/beatmaps/3/covers/list@2x.jpg?1622017885","slimcover":"https://assets.ppy.sh/beatmaps/3/covers/slimcover.jpg?1622017885","slimcover@2x":"https://assets.ppy.sh/beatmaps/3/covers/slimcover@2x.jpg?1622017885"},"creator":"MCXD","favourite_count":255,"id":3,"nsfw":false,"play_count":629247,"preview_url":"//b.ppy.sh/preview/3.mp3","source":"","status":"ranked","spotlight":false,"title":"1,2,3,4, 007 [Wipeout Series]","title_unicode":"1,2,3,4, 007 [Wipeout Series]","user_id":141,"video":false,"offset":40,"beatmaps":null,"has_favourited":null,"nominations_summary":{"current":0,"required":2},"pack_tags":null,"ratings":[0,147,50,46,45,82,127,189,228,177,902],"track_id":null,"availability":{"download_disabled":false,"more_information":null},"bpm":172.0,"can_be_hyped":false,"discussion_locked":false,"is_scoreable":true,"last_updated":"2007-10-06T19:32:02Z","nominations":null,"ranked":1,"storyboard":false,"tags":"","hype":null,"legacy_thread_url":"https://osu.ppy.sh/community/forums/topics/65","submitted_date":"2007-10-06T19:32:02Z","ranked_date":"2007-10-06T19:32:02Z","deleted_at":null,"discussion_enabled":true},"max_combo":124,"checksum":"1d23c37a2fda439be752ae2bca06c0cd","failtimes":{"exit":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,9,0,1,0,0,9,78,462,145,304,330,2024,1056,965,1030,1161,323,101,306,662,449,1311,1269,1036,2568,2668,1504,805,753,579,652,782,764,1206,541,379,613,457,370,348,470,357,367,536,510,422,751,720,527,346,354,294,623,907,635,440,444,219,152,138,110,86,134,134,91,66,69,88,142,120,133,83,49,133,91,105,117,101,78,107,228,809],"fail":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,15,12,5,4,7,10,5,14,99,14,139,86,589,130,168,115,31,2,58,100,97,93,320,129,175,522,524,123,175,226,265,276,272,396,264,180,181,391,153,147,249,292,291,370,463,681,127,385,304,209,351,225,280,313,444,311,409,495,161,46,80,106,101,66,78,15,36,81,153,159,121,120,119,102,214,233,167,171,116,140,64,71,77,83]},"accuracy":4.0,"ar":4.0,"convert":false,"count_circles":67,"count_sliders":15,"count_spinners":1,"cs":5.0,"drain":3.0,"hit_length":77,"is_scoreable":true,"last_updated":"2014-05-18T16:56:27Z","mode_int":0,"passcount":57129,"playcount":124191,"ranked":1,"url":"https://osu.ppy.sh/beatmaps/53","deleted_at":null,"bpm":172.0},{"beatmapset_id":3,"difficulty_rating":2.82,"id":55,"mode":"osu","status":"ranked","total_length":83,"user_id":141,"version":"-Sweatin-","beatmapset":{"artist":"Ni-Ni","artist_unicode":"Ni-Ni","covers":{"cover":"https://assets.ppy.sh/beatmaps/3/covers/cover.jpg?1622017885","cover@2x":"https://assets.ppy.sh/beatmaps/3/covers/cover@2x.jpg?1622017885","card":"https://assets.ppy.sh/beatmaps/3/covers/card.jpg?1622017885","card@2x":"https://assets.ppy.sh/beatmaps/3/covers/card@2x.jpg?1622017885","list":"https://assets.ppy.sh/beatmaps/3/covers/list.jpg?1622017885","list@2x":"https://assets.ppy.sh/beatmaps/3/covers/list@2x.jpg?1622017885","slimcover":"https://assets.ppy.sh/beatmaps/3/covers/slimcover.jpg?1622017885","slimcover@2x":"https://assets.ppy.sh/beatmaps/3/covers/slimcover@2x.jpg?1622017885"},"creator":"MCXD","favourite_count":255,"id":3,"nsfw":false,"play_count":629247,"preview_url":"//b.ppy.sh/preview/3.mp3","source":"","status":"ranked","spotlight":false,"title":"1,2,3,4, 007 [Wipeout Series]","title_unicode":"1,2,3,4, 007 [Wipeout Series]","user_id":141,"video":false,"offset":40,"beatmaps":null,"has_favourited":null,"nominations_summary":{"current":0,"required":2},"pack_tags":null,"ratings":[0,147,50,46,45,82,127,189,228,177,902],"track_id":null,"availability":{"download_disabled":false,"more_information":null},"bpm":172.0,"can_be_hyped":false,"discussion_locked":false,"is_scoreable":true,"last_updated":"2007-10-06T19:32:02Z","nominations":null,"ranked":1,"storyboard":false,"tags":"","hype":null,"legacy_thread_url":"https://osu.ppy.sh/community/forums/topics/65","submitted_date":"2007-10-06T19:32:02Z","ranked_date":"2007-10-06T19:32:02Z","deleted_at":null,"discussion_enabled":true},"max_combo":182,"checksum":"a5372216d0902bacc7eb081e15e36bb9","failtimes":{"exit":[0,0,0,0,0,0,0,0,0,0,0,0,0,142,128,45,40,59,461,289,138,508,708,428,946,1076,1127,1415,1595,1082,1023,810,942,1994,705,343,697,835,521,435,1916,2169,999,765,714,291,460,1330,1272,487,1567,1611,495,568,1375,778,220,569,443,260,222,447,527,464,586,683,521,458,327,158,257,298,288,219,173,144,81,102,116,105,106,141,183,228,164,104,86,78,100,88,110,137,126,59,84,78,93,54,284,809],"fail":[0,0,0,0,0,0,0,0,0,0,0,3,26,42,23,27,37,92,39,46,81,62,13,107,84,139,220,177,237,229,357,335,451,124,235,430,595,470,422,1062,998,788,696,601,395,464,644,858,367,1140,1603,860,702,977,888,644,1451,1306,1006,617,1096,1095,758,1202,1734,1466,521,824,555,521,700,878,419,390,177,127,80,90,83,88,147,231,163,254,121,106,71,92,118,80,54,74,65,97,110,102,46,72,44,17]},"accuracy":6.0,"ar":6.0,"convert":false,"count_circles":95,"count_sliders":23,"count_spinners":1,"cs":6.0,"drain":4.0,"hit_length":77,"is_scoreable":true,"last_updated":"2014-05-18T16:56:40Z","mode_int":0,"passcount":44582,"playcount":138413,"ranked":1,"url":"https://osu.ppy.sh/beatmaps/55","deleted_at":null,"bpm":172.0}]}', # noqa
    type=BeatmapsExtended, strict=False
)
SAMPLE_BEATMAPSET = SAMPLE_BEATMAP.beatmapset
SAMPLE_BEATMAP_SCORES = msgspec.json.decode(
    msgspec.json.encode({'scores': [{'accuracy': 1, 'best_id': 2677135599, 'created_at': '2018-11-20T05:59:07Z', 'id': 2677135599, 'max_combo': 124, 'mode': 'osu', 'mode_int': 0, 'mods': ['HD', 'HR', 'NC', 'FL'], 'passed': True, 'perfect': True, 'pp': 78.102, 'rank': 'XH', 'replay': True, 'score': 285725, 'statistics': {'count_100': 0, 'count_300': 83, 'count_50': 0, 'count_geki': 21, 'count_katu': 0, 'count_miss': 0}, 'type': 'score_best_osu', 'user_id': 7162035, 'current_user_attributes': {'pin': None}, 'user': {'avatar_url': 'https://a.ppy.sh/7162035?1686579464.jpeg', 'country_code': 'US', 'default_group': 'default', 'id': 7162035, 'is_active': True, 'is_bot': False, 'is_deleted': False, 'is_online': False, 'is_supporter': True, 'last_visit': None, 'pm_friends_only': False, 'profile_colour': None, 'username': '[-Griffin-]', 'country': {'code': 'US', 'name': 'United States'}, 'cover': {'custom_url': 'https://assets.ppy.sh/user-profile-covers/7162035/df04542b852026a7f8b50f7a7e28ba8b5cf68e9dfa41b06f5a14927287a06a3f.jpeg', 'url': 'https://assets.ppy.sh/user-profile-covers/7162035/df04542b852026a7f8b50f7a7e28ba8b5cf68e9dfa41b06f5a14927287a06a3f.jpeg', 'id': None}}}], 'user_score': {'position': 11791, 'score': {'accuracy': 0.7068273092369478, 'best_id': 3769562004, 'created_at': '2021-07-14T11:30:25Z', 'id': 3769562004, 'max_combo': 41, 'mode': 'osu', 'mode_int': 0, 'mods': ['HD', 'HR', 'DT'], 'passed': True, 'perfect': False, 'pp': 4.08139, 'rank': 'C', 'replay': False, 'score': 63489, 'statistics': {'count_100': 23, 'count_300': 50, 'count_50': 6, 'count_geki': 6, 'count_katu': 9, 'count_miss': 4}, 'type': 'score_best_osu', 'user_id': 4553150, 'current_user_attributes': {'pin': {'is_pinned': False, 'score_id': 3769562004, 'score_type': 'score_best_osu'}}, 'user': {'avatar_url': 'https://a.ppy.sh/4553150?1652623670.jpeg', 'country_code': 'FR', 'default_group': 'default', 'id': 4553150, 'is_active': True, 'is_bot': False, 'is_deleted': False, 'is_online': False, 'is_supporter': True, 'last_visit': None, 'pm_friends_only': False, 'profile_colour': None, 'username': 'pemy', 'country': {'code': 'FR', 'name': 'France'}, 'cover': {'custom_url': 'https://assets.ppy.sh/user-profile-covers/4553150/76fd52a0492896484aaacf3ebd0a9a62c0b715d84891da50277ac36642383c32.jpeg', 'url': 'https://assets.ppy.sh/user-profile-covers/4553150/76fd52a0492896484aaacf3ebd0a9a62c0b715d84891da50277ac36642383c32.jpeg', 'id': None}}}}, 'beatmap_id': 53, 'scope': 'global'}),
    type=BeatmapScores, strict=False
)
SAMPLE_BEATMAP_SCORES2 = msgspec.json.decode(
    msgspec.json.encode({'scores': [{'accuracy': 1, 'best_id': 2677135599, 'created_at': '2018-11-20T05:59:07Z', 'id': 2677135599, 'max_combo': 124, 'mode': 'osu', 'mode_int': 0, 'mods': ['HD', 'HR', 'NC', 'FL'], 'passed': True, 'perfect': True, 'pp': 78.102, 'rank': 'XH', 'replay': True, 'score': 285725, 'statistics': {'count_100': 0, 'count_300': 83, 'count_50': 0, 'count_geki': 21, 'count_katu': 0, 'count_miss': 0}, 'type': 'score_best_osu', 'user_id': 7162035, 'current_user_attributes': {'pin': None}, 'user': {'avatar_url': 'https://a.ppy.sh/7162035?1686579464.jpeg', 'country_code': 'US', 'default_group': 'default', 'id': 7162035, 'is_active': True, 'is_bot': False, 'is_deleted': False, 'is_online': False, 'is_supporter': True, 'last_visit': None, 'pm_friends_only': False, 'profile_colour': None, 'username': '[-Griffin-]', 'country': {'code': 'US', 'name': 'United States'}, 'cover': {'custom_url': 'https://assets.ppy.sh/user-profile-covers/7162035/df04542b852026a7f8b50f7a7e28ba8b5cf68e9dfa41b06f5a14927287a06a3f.jpeg', 'url': 'https://assets.ppy.sh/user-profile-covers/7162035/df04542b852026a7f8b50f7a7e28ba8b5cf68e9dfa41b06f5a14927287a06a3f.jpeg', 'id': None}}}], 'user_score': {'position': 11791, 'score': {'accuracy': 0.7068273092369478, 'best_id': 3769562004, 'created_at': '2021-07-14T11:30:25Z', 'id': 3769562004, 'max_combo': 41, 'mode': 'osu', 'mode_int': 0, 'mods': ['HD', 'HR', 'DT'], 'passed': True, 'perfect': False, 'pp': 4.08139, 'rank': 'C', 'replay': False, 'score': 63489, 'statistics': {'count_100': 23, 'count_300': 50, 'count_50': 6, 'count_geki': 6, 'count_katu': 9, 'count_miss': 4}, 'type': 'score_best_osu', 'user_id': 4553150, 'current_user_attributes': {'pin': {'is_pinned': False, 'score_id': 3769562004, 'score_type': 'score_best_osu'}}, 'user': {'avatar_url': 'https://a.ppy.sh/4553150?1652623670.jpeg', 'country_code': 'FR', 'default_group': 'default', 'id': 4553150, 'is_active': True, 'is_bot': False, 'is_deleted': False, 'is_online': False, 'is_supporter': True, 'last_visit': None, 'pm_friends_only': False, 'profile_colour': None, 'username': 'pemy', 'country': {'code': 'FR', 'name': 'France'}, 'cover': {'custom_url': 'https://assets.ppy.sh/user-profile-covers/4553150/76fd52a0492896484aaacf3ebd0a9a62c0b715d84891da50277ac36642383c32.jpeg', 'url': 'https://assets.ppy.sh/user-profile-covers/4553150/76fd52a0492896484aaacf3ebd0a9a62c0b715d84891da50277ac36642383c32.jpeg', 'id': None}}}}, 'beatmap_id': 53, 'scope': 'country'}),
    type=BeatmapScores, strict=False
)
SAMPLE_USER = msgspec.json.decode(
    msgspec.json.encode({'avatar_url': 'https://a.ppy.sh/7162035?1686579464.jpeg', 'country_code': 'US', 'default_group': 'default', 'id': 7162035, 'is_active': True, 'is_bot': False, 'is_deleted': False, 'is_online': False, 'is_supporter': True, 'last_visit': None, 'pm_friends_only': False, 'profile_colour': None, 'username': '[-Griffin-]', 'country': {'code': 'US', 'name': 'United States'}, 'cover': {'custom_url': 'https://assets.ppy.sh/user-profile-covers/7162035/df04542b852026a7f8b50f7a7e28ba8b5cf68e9dfa41b06f5a14927287a06a3f.jpeg', 'url': 'https://assets.ppy.sh/user-profile-covers/7162035/df04542b852026a7f8b50f7a7e28ba8b5cf68e9dfa41b06f5a14927287a06a3f.jpeg', 'id': None}}),
    type=User, strict=False
)
SAMPLE_BEST_RANK = DBBestRank(country_code="US", beatmap_id=53, rank=1, score_id=2677135599)
SAMPLE_COUNTRY_LB = [('AR', 53, 1, 3916309992), ('AU', 53, 1, 4136022294), ('BY', 53, 1, 3299446565), ('CA', 53, 1, 3209741877), ('CA', 53, 2, 4387707953), ('CL', 53, 1, 3214569829), ('CZ', 53, 1, 3840010046), ('CZ', 53, 2, 3481433273), ('DE', 53, 1, 4447062681), ('DE', 53, 2, 2386946673), ('DE', 53, 3, 1840125485), ('FI', 53, 1, 4368872498), ('FI', 53, 2, 4203670106), ('FI', 53, 3, 4186292504), ('FI', 53, 4, 4139724925), ('FR', 53, 1, 4353679190), ('FR', 53, 2, 1153035786), ('FR', 53, 3, 3342333675), ('FR', 53, 4, 3512322150), ('GB', 53, 1, 1995481318), ('GB', 53, 2, 2888080613), ('GB', 53, 3, 4166882230), ('HK', 53, 1, 4175833838), ('JP', 53, 1, 2833365036), ('KR', 53, 1, 1930708995), ('KR', 53, 2, 1934505743), ('KR', 53, 3, 3110966475), ('KR', 53, 4, 2034311651), ('LT', 53, 1, 4464857253), ('LV', 53, 1, 2423011341), ('NL', 53, 1, 2535099336), ('NL', 53, 2, 2501276898), ('PE', 53, 1, 4335161382), ('PH', 53, 1, 3256572746), ('PL', 53, 1, 4181467764), ('PL', 53, 2, 3358103428), ('PL', 53, 3, 29269095), ('PL', 53, 4, 3113347473), ('PL', 53, 5, 1335248355), ('PL', 53, 6, 2591155245), ('RU', 53, 1, 2676773796), ('RU', 53, 2, 4372788615), ('US', 53, 1, 2677135599), ('US', 53, 2, 4059897564), ('US', 53, 3, 4235768191), ('US', 53, 4, 3099791142), ('US', 53, 5, 4363782893), ('US', 53, 6, 4290065151), ('US', 53, 7, 3868258847), ('US', 53, 8, 4143220861)]
SAMPLE_BEST_RANK_RAW = [('DE', 53, 14, 4447062681), ('US', 53, 1, 2677135599), ('PL', 53, 8, 4181467764), ('JP', 53, 15, 2833365036), ('RU', 53, 4, 2676773796), ('PE', 53, 19, 4335161382), ('LV', 53, 24, 2423011341), ('FI', 53, 9, 4368872498), ('CZ', 53, 22, 3840010046), ('AR', 53, 39, 3916309992), ('LT', 53, 21, 4464857253), ('KR', 53, 3, 1930708995), ('BY', 53, 40, 3299446565), ('CA', 53, 30, 3209741877), ('PH', 53, 6, 3256572746), ('AU', 53, 44, 4136022294), ('CL', 53, 2, 3214569829), ('FR', 53, 11, 4353679190), ('GB', 53, 17, 1995481318), ('HK', 53, 46, 4175833838), ('NL', 53, 18, 2535099336)]
SAMPLE_TEST_DB = "../ressources/test_data.db"
BEATMAPSET_QUERY = 'insert into beatmapset values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
BEATMAP_QUERY = 'insert into beatmap values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
USER_QUERY = 'insert into user values (?,?,?)'
SCORE_QUERY = 'insert into score values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
GLOBAL_LB_QUERY = 'insert into global_lb values (?,?,?)'
COUNTRY_LB_QUERY = 'insert into country_lb values (?,?,?,?)'
BEST_RANK_QUERY = 'insert into best_rank values (?,?,?,?)'


class TestCircleDB(unittest.TestCase):
    def test_update_country_lb_from_global_lb(self):
        with CircleDB(SAMPLE_TEST_DB) as orm:
            orm.cur.execute("delete from country_lb")
            orm.update_country_lb_from_global_lb()
            orm.save()
            orm.cur.execute("select * from country_lb")
            data = orm.cur.fetchall()
        self.assertEqual(SAMPLE_COUNTRY_LB, data)

    def test_update_best_rank_from_lb(self):
        with CircleDB(SAMPLE_TEST_DB) as orm:
            orm.cur.execute("delete from best_rank")
            orm.update_best_rank_from_lb()
            orm.save()
            orm.cur.execute("select * from best_rank")
            data = orm.cur.fetchall()
        self.assertEqual(SAMPLE_BEST_RANK_RAW, data)

    def test_get_lb_in_db(self):
        with CircleDB(SAMPLE_TEST_DB) as orm:
            data1 = orm.get_lb_in_db("global")
            data2 = orm.get_lb_in_db("country", "US")
        self.assertIn(53, data1)
        self.assertIn(53, data2)

    def test_get_beatmap_in_db(self):
        with CircleDB(SAMPLE_TEST_DB) as orm:
            data = orm.get_beatmap_in_db()
        self.assertEqual(2, len(data))
        self.assertIn(53, data)
        self.assertIn(55, data)

    def test_get_best_rank(self):
        with CircleDB(SAMPLE_TEST_DB) as orm:
            data1 = orm.get_best_rank(country_code=["US"])
            data2 = orm.get_best_rank(rank=[1])
        self.assertEqual(2677135599, data1[0].score_id)
        self.assertEqual(2677135599, data2[0].score_id)

    def test_add_best_rank(self):
        with CircleDB(SAMPLE_TEST_DB) as orm:
            orm.add_best_rank(SAMPLE_BEST_RANK)
            self.assertIn(BEST_RANK_QUERY, orm.queue)
            self.assertEqual(orm.queue[BEST_RANK_QUERY], {('US', 53, 1, 2677135599)})

    def test_add_score(self):
        with CircleDB(SAMPLE_TEST_DB) as orm:
            orm.add_score(SAMPLE_BEATMAP_SCORES.scores[0], 53)
            self.assertIn(SCORE_QUERY, orm.queue)
            self.assertEqual(orm.queue[SCORE_QUERY], {(2677135599, 53, 7162035, 100.0, 124, 'XH', 78.102, 285725, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 83, 0, 0, 21, 0, 0, 1, 'osu', '2018-11-20 05:59:07+00:00', list(orm.queue[SCORE_QUERY])[0][-1])})

    def test_add_user(self):
        with CircleDB(SAMPLE_TEST_DB) as orm:
            orm.add_user(SAMPLE_USER)
            self.assertIn(USER_QUERY, orm.queue)
            self.assertEqual(orm.queue[USER_QUERY], {(7162035, '[-Griffin-]', 'US')})

    def test_add_lb(self):
        with CircleDB(SAMPLE_TEST_DB) as orm:
            orm.add_lb(SAMPLE_BEATMAP_SCORES)
            self.assertIn(USER_QUERY, orm.queue)
            self.assertIn(SCORE_QUERY, orm.queue)
            self.assertIn(GLOBAL_LB_QUERY, orm.queue)
            self.assertEqual(orm.queue[USER_QUERY], {(7162035, '[-Griffin-]', 'US')})
            self.assertEqual(orm.queue[SCORE_QUERY], {(2677135599, 53, 7162035, 100.0, 124, 'XH', 78.102, 285725, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 83, 0, 0, 21, 0, 0, 1, 'osu', '2018-11-20 05:59:07+00:00', list(orm.queue[SCORE_QUERY])[0][-1])})
            self.assertEqual(orm.queue[GLOBAL_LB_QUERY], {(53, 1, 2677135599)})
        with CircleDB(SAMPLE_TEST_DB) as orm:
            orm.add_lb(SAMPLE_BEATMAP_SCORES2)
            self.assertIn(USER_QUERY, orm.queue)
            self.assertIn(SCORE_QUERY, orm.queue)
            self.assertIn(COUNTRY_LB_QUERY, orm.queue)
            self.assertEqual(orm.queue[USER_QUERY], {(7162035, '[-Griffin-]', 'US')})
            self.assertEqual(orm.queue[SCORE_QUERY], {(2677135599, 53, 7162035, 100.0, 124, 'XH', 78.102, 285725, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 83, 0, 0, 21, 0, 0, 1, 'osu', '2018-11-20 05:59:07+00:00', list(orm.queue[SCORE_QUERY])[0][-1])})
            self.assertEqual(orm.queue[COUNTRY_LB_QUERY], {("US", 53, 1, 2677135599)})

    def test_add_beatmapset(self):
        with CircleDB(SAMPLE_TEST_DB) as orm:
            orm.add_beatmapset(SAMPLE_BEATMAPSET)
            self.assertIn(BEATMAPSET_QUERY, orm.queue)
            self.assertEqual(orm.queue[BEATMAPSET_QUERY], {(3, '1,2,3,4, 007 [Wipeout Series]', 'Ni-Ni', None, 'MCXD', 141, 'ranked', 172.0, 629247, 255, None, '2007-10-06 19:32:02+00:00', '2007-10-06 19:32:02+00:00', '2007-10-06 19:32:02+00:00', 40, 0, 0, 0, 0)})

    def test_add_beatmap(self):
        with CircleDB(SAMPLE_TEST_DB) as orm:
            orm.add_beatmap(SAMPLE_BEATMAP)
            self.assertIn(BEATMAPSET_QUERY, orm.queue)
            self.assertEqual(orm.queue[BEATMAPSET_QUERY], {(3, '1,2,3,4, 007 [Wipeout Series]', 'Ni-Ni', None, 'MCXD', 141, 'ranked', 172.0, 629247, 255, None, '2007-10-06 19:32:02+00:00', '2007-10-06 19:32:02+00:00', '2007-10-06 19:32:02+00:00', 40, 0, 0, 0, 0)})
            self.assertIn(BEATMAP_QUERY, orm.queue)
            self.assertEqual(orm.queue[BEATMAP_QUERY], {(53, 2.16, 4.0, 5.0, 3.0, 4.0, 172.0, 1, 124, 67, 15, 77, 83, 57129, 124191, 'https://osu.ppy.sh/beatmaps/53', 'osu://b/53', '-Crusin-', 3, '1d23c37a2fda439be752ae2bca06c0cd')})

    def test_add_beatmaps(self):
        with CircleDB(SAMPLE_TEST_DB) as orm:
            orm.add_beatmaps(SAMPLE_BEATMAPS)
            self.assertIn(BEATMAPSET_QUERY, orm.queue)
            self.assertEqual(orm.queue[BEATMAPSET_QUERY], {(3, '1,2,3,4, 007 [Wipeout Series]', 'Ni-Ni', None, 'MCXD', 141, 'ranked', 172.0, 629247, 255, None, '2007-10-06 19:32:02+00:00', '2007-10-06 19:32:02+00:00', '2007-10-06 19:32:02+00:00', 40, 0, 0, 0, 0)})
            self.assertIn(BEATMAP_QUERY, orm.queue)
            self.assertEqual(orm.queue[BEATMAP_QUERY], {(53, 2.16, 4.0, 5.0, 3.0, 4.0, 172.0, 1, 124, 67, 15, 77, 83, 57129, 124191, 'https://osu.ppy.sh/beatmaps/53', 'osu://b/53', '-Crusin-', 3, '1d23c37a2fda439be752ae2bca06c0cd'), (55, 2.82, 6.0, 6.0, 4.0, 6.0, 172.0, 1, 182, 95, 23, 77, 83, 44582, 138413, 'https://osu.ppy.sh/beatmaps/55', 'osu://b/55', '-Sweatin-', 3, 'a5372216d0902bacc7eb081e15e36bb9')})
