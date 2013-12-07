import re
import requests

from plugin import AnkhBotPlugin


class xkcd(AnkhBotPlugin):

    name = "xkcd plugin"
    description = "Provides xkcd link parsing"

    def on_message(self, user, channel, msg):
        response = "Title: {} :: URL: {}"
        comic = None
        print "'{}'".format(msg.lower().strip())
        if msg.lower().strip() == ".xkcd latest":
            comic = self.get_comic_info()
        elif re.search(r"/xkcd.com/(\d+)", msg) is not None:
            comic_id = re.search(r"/xkcd.com/(\d+)", msg).group(1)
            comic = self.get_comic_info(comic_id)
        elif msg.replace(".xkcd", "").strip().isdigit():
            comic = self.get_comic_info(msg.replace(".xkcd", "").strip())
        else:
            return

        if comic is not None:
            self.bot.msg(channel, response.format(comic['title'],
                                                  "http://xkcd.com/" + str(comic['num'])))

    def get_comic_info(self, comic_id=None):
        url = "http://xkcd.com/{}info.0.json".format(
            "" if comic_id is None else comic_id + "/")
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
        else:
            return None
