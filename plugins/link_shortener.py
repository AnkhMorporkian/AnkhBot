import re
import bitly_api

from plugin import AnkhBotPlugin


class LinkShortener(AnkhBotPlugin):
    name = "Link Shortener"
    description = "Shortens links automatically in channels."

    def activate(self):
        super(LinkShortener, self).activate()
        print "Activated LinkShortener"
        self.bitly = bitly_api.Connection(self.config["username"].lower(), self.config["api_token"])
        self.url_regex = re.compile(r'((?:https?://)?(?:[\da-z\.-]+)\.(?:[a-z\.]{2,6})(?:[/\w \.-]*)*/?)')

    def on_message(self, user, channel, msg):
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', msg)
        if urls is not None:
            shortened_urls = []
            for url in urls:
                if len(url) > 30:
                    shortened_urls.append(self.bitly.shorten(url))
            if len(shortened_urls) == 1:
                self.bot.msg(channel,
                             "%s's link shortened: %s" % (self.pretty_username(user), str(shortened_urls[0]['url'])))
            elif len(shortened_urls) > 1:
                self.bot.msg(channel, "%s's links shortened: %s" % (
                    self.pretty_username(user), str(' '.join([url['url'] for url in shortened_urls]))))
