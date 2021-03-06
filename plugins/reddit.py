import re
import requests
import datetime

from plugin import AnkhBotPlugin


class Reddit(AnkhBotPlugin):

    """docstring for Reddit"""

    name = "python plugin"
    description = "Provides python link parsing"

    def on_message(self, user, channel, msg):
        response = ""
        subreddits = re.findall(r'r/(\D\S*)', msg)
        users = re.findall(r'u/(\D\S*)', msg)
        links = re.findall(r'reddit[.]com/r/\D\S*/comments/(\d\D\S{4})', msg)
        if subreddits is not None:
            for sub in subreddits:
                sub_info = self.load_url(
                    "http://www.reddit.com/r/{}/about.json".format(sub))
                if sub_info is None:
                    continue
                # this fails on every link, meh too lazy to fix it, just
                # try/except-continue
                try:
                    sub_info = sub_info["data"]
                except:
                    continue
                sub_format = "http://reddit.com/r/{} [NSFW: {} :: Subscribers: {}] "
                response += sub_format.format(
                    sub, sub_info["over18"], sub_info["subscribers"])

        if users is not None:
            for user in users:
                user_info = self.load_url(
                    "http://www.reddit.com/user/{}/about.json".format(user))
                if user_info is None:
                    continue
                user_info = user_info["data"]
                user_format = "http://reddit.com/u/{} [Karma: {} :: Created on: {}] "
                response += user_format.format(
                    user, user_info['comment_karma'] + user_info['link_karma'],
                    datetime.datetime.fromtimestamp(int(user_info['created_utc'])).strftime('%Y-%m-%d %H:%M:%S'))

        if links is not None:
            for link in links:
                link_info = self.load_url(
                    "http://reddit.com/comments/{}/.json?limit=1".format(link))
                if link_info is None:
                    continue
                link_info = link_info[0]['data']['children'][0]['data']
                response += "Short Link: http://redd.it/{} :: Title: {} :: Score: {} :: {}".format(link_info['id'],
                                                                                                         link_info['title'].encode(
                                                                                                         "utf-8", "ignore"),
                                                                                                         link_info[
                                                                                                         'score'],
                                                                                                         "NSFW ::" if link_info['over_18'] else "")
                if link_info['is_self'] and link_info['selftext'] != "":
                    response += "Selftext: {} ::".format(
                        " ".join(link_info['selftext'].split("\n")))
                elif link_info['is_self'] is False:
                    response += "Domain: {}".format(link_info['domain'])

        if response != "":
            if len(response) > 405:
                self.bot.msg(channel, response[:405] + "...")
            else:
                self.bot.msg(channel, response)

    def load_url(self, url):
        if not url.endswith(".json"):
            url += ".json"  # Just in case..
        headers = {'user-agent': 'freenode ##learnpython irc bot /u/wub_wub'}
        try:
            r = requests.get(url, headers=headers)
        except:
            return None
        if r.status_code == 200:
            # reddit returns code 200 even for most 404 pages...
            # the returned content is either empty json
            # or json with key error...
            try:
                return r.json()
            except:
                return None
        else:
            return None
