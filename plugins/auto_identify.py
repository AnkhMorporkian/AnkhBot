from plugin import AnkhBotPlugin


class AutoIdentifier(AnkhBotPlugin):
    name = "Auto Identifier"
    version = 0.1
    description = "Identifies the bot to nickserv automatically."
    priority = 2

    def __init__(self):
        self.waiting_for_ident = False

    def activate(self):
        super(AutoIdentifier, self).activate()
        self.waiting_for_ident = True
        self.bot.msg(self.config["nickserv"], "IDENTIFY %s %s" % (self.config["username"], self.config["password"]))

    def on_notice(self, user, channel, msg):
        if self.waiting_for_ident and self.pretty_username(user).lower() == self.config["nickserv"].lower():
            print "Got NickServ message."
            if "identified" in msg.lower():
                self.bot.identified = True
                self.waiting_for_ident = False
                print "Successfully identified"
            elif "invalid password" in msg.lower():
                print "Did not successfully identify."