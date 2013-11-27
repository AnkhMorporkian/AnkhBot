import re

from plugin import AnkhBotPlugin


class StringSubstitution(AnkhBotPlugin):
    substitution_regex = re.compile(r's/(.+)/(.+)')

    def on_message(self, user, channel, msg):
        output = self.substitute(user, channel, msg)
        if output:
            self.bot.msg(channel, output)

    def substitute(self, user, channel, msg):
        match = re.match(self.substitution_regex, msg)
        if match:
            old, new = match.groups()
            found_one = False
            for line in reversed(self.bot.history):
                if line["user"] == user and line["channel"] == channel:
                    old_message = line["msg"]
                    if found_one:
                        break
                    found_one = True
            else:
                return
            new_message = re.sub(old, new, old_message, flags=re.IGNORECASE)
            if new_message != old_message:
                return "%s meant to say: %s" % (self.pretty_username(user), new_message)