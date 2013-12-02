import pprint

from user_manager import permissions, OWNER

from plugin import CommandPlugin


class AdminCommands(CommandPlugin):
    name = "Admin Commands"
    description = "Provides an admin interface"
    version = 0.1
    priority = 5

    def activate(self):
        super(AdminCommands, self).activate()
        print "activated admin commands XX"
        self.commands = {"reload_plugins": self.reload_plugins, "list_timers": self.list_timers}

    @permissions(OWNER)
    def reload_plugins(self, user, channel, parameters):
        print channel
        self.bot.msg(user, "Reloading plugins.")
        self.bot.plugin_manager.reload_plugins()

    @permissions(OWNER)
    def list_timers(self, user, channel, parameters):
        print str(channel)
        print len(channel)
        self.bot.msg(user, pprint.pformat(self.bot.timers))