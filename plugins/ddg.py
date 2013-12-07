import duckduckgo
from plugin import AnkhBotPlugin


class DuckDuckGo(AnkhBotPlugin):

    """docstring for DuckDuckGo"""

    name = "DuckDuckGo.com plugin"
    description = "Provides duckduckgo searches"

    def on_message(self, user, channel, msg):
        response = None
        if msg.startswith(".ddg"):
            query = msg.replace(".ddg", "").strip()
        else:
            return

        try:  # Do I need this?
            d = duckduckgo.query(query)
        except:
            return

        if d.type == 'answer':
            if d.answer is not None:
                response = "{}".format(d.answer.text)
            else:
                response = "{} :: Source: {} - {}".format(d.abstract.text,
                                                            d.abstract.source,
                                                            d.abstract.url)
            if len(d.results) > 0:  # or should I use !=[]...
                response += " :: {}: {}".format(d.results[0].text,
                                                  d.results[0].url)

        elif d.type == 'exclusive' or d.type == 'nothing':
            if d.answer is not None:
                response = "{}".format(d.answer.text)

        elif d.type == 'disambiguation':
            if len(d.related) > 1:
                response = "Disambiguation: {} :: {}".format(d.related[0].text,
                                                               d.related[1].text)

        if response is None or response == "":
            self.bot.msg(channel, "Sorry, no results found")
        else:
            self.bot.msg(channel, response)
