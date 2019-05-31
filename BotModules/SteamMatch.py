import steam
from requests import HTTPError
from steam import WebAPI, SteamID
import config


class SteamMatch:
    def __init__(self, *users):
        self._api: WebAPI = WebAPI(config.STEAM_KEY)

        if len(users) < 2:
            raise SteamMatchException("At least two users must be entered.\nUsage: `?sm SteamUser1 SteamUser2`")
        self._users = list(map(self.get_user, users))
        pass

    def get_user(self, user: str):
        if user.startswith("https://steamcommunity.com/id/") or user.startswith("https://steamcommunity.com/profiles/"):
            u = user.replace("//", "/", 1).split("/", 3)[-1]
            return steam.steamid.from_url(user), u if u[-1] != "/" else u[:-1]

        res = self._api.call("ISteamUser.ResolveVanityURL", vanityurl=user, url_type=1)
        if res["response"]["success"] == 1:
            return SteamID(res["response"]["steamid"]), user
        else:
            # TODO: Logging
            print(res)
            pass

        if user.isnumeric():
            res = self._api.call("ISteamUser.GetPlayerSummaries", steamids=user)
            if isinstance(res["response"]["players"], list) and len(res["response"]["players"]) == 1:
                u = res["response"]["players"][0]
                return SteamID(u["steamid"]), u["personaname"]
            elif isinstance(res["response"]["players"], dict) and len(res["response"]["players"]["player"]) == 1:
                u = res["response"]["players"]["player"][0]
                return SteamID(u["steamid"]), u["personaname"]
            else:
                print(res)
                pass
            pass
        raise SteamMatchException(f"User {user} not found.")

    def get_library(self, user: SteamID, include_played_free_games=True, include_appinfo=True):
        try:
            return self._api.call("IPlayerService.GetOwnedGames", steamid=user.as_64, include_appinfo=include_appinfo,
                                  include_played_free_games=include_played_free_games, appids_filter=[])["response"]
        except HTTPError:
            return None
        pass

    def compare(self):
        game_url = "https://store.steampowered.com/app/"
        libs = {}
        counts = {}
        apps = {}
        for u in self._users:
            lib = self.get_library(u[0])
            if not lib:
                counts[u[1]] = 0
                libs[u[1]] = []
                continue

            libs[u[1]] = set()
            for g in lib["games"]:
                libs[u[1]].add(g["appid"])

                if g["appid"] in apps:
                    apps[g["appid"]]["u"][u[1]] = g["playtime_forever"]
                    pass
                else:
                    apps[g["appid"]] = {
                        "name": g["name"],
                        "u": {u[1]: g["playtime_forever"]},
                    }
                    pass
                pass

            counts[u[1]] = lib["game_count"]
            pass

        intersection = libs[self._users[0][1]]
        for l in libs:
            intersection &= libs[l]
            pass

        games = list(map(lambda x: {"appid": x, "url": game_url + str(x), "info": apps[x]}, intersection))
        games.sort(key=lambda x: x["info"]["name"])
        return {"users": counts, "games": games}
    pass


class SteamMatchException(Exception):
    pass
