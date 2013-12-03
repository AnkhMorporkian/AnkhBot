import re
import requests
import datetime

from plugin import AnkhBotPlugin

class YouTube(AnkhBotPlugin):

    name = "YouTube plugin"
    description = "Provides youtube link parsing"

    def on_message(self, user, channel, msg):
        match = re.search(r"youtube\.com/.*v=([^&]*)", msg)
        if match:
            video_id = match.group(1)
        else:
            return

        try:
            r=requests.get("http://gdata.youtube.com/feeds/api/videos/{}?v=2&alt=jsonc".format(video_id))
            if r.status_code==200:
                v_json=r.json()
                v_json=v_json['data']
            else:
                return
        except:
            return

        response="Title: {} :: Uploader: {} :: Duration: {} :: Views: {} :: Rating: {:.2f}"
        self.bot.msg(channel,response.format(v_json['title'],v_json['uploader'],self.format_yt_time(v_json['duration']),
                        v_json['viewCount'],v_json['rating']))

    def format_yt_time(self,seconds):
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return "%d:%02d:%02d" % (h, m, s)