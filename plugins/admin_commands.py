from plugin import CommandPlugin


class AdminCommands(CommandPlugin):
    name = "Admin Commands"
    description = "Provides an admin interface"
    version = 0.1
    priority = 5

    def activate(self):
        super(AdminCommands, self).activate()
        print "got to admin commands activation"
        self.commands = {"test": self.test}

    def test(self, user, channel, parameters):
        print "Got to test"
        self.bot.msg(channel, "test complete")
