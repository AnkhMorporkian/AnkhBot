import re
from plugin import CommandPlugin


class PluginManagerPlugin(CommandPlugin):
    def __init__(self):
        super(PluginManagerPlugin, self).__init__()
        self.commands = {"status": self.status,
                         "list_plugins": self.list_plugins,
                         "deactivate": self.deactivate_plugin}

    def status(self, user, channel, parameters):
        self.bot.msg(channel, "Got command status from %s with parameters %s" % (user, parameters))

    def list_plugins(self, user, channel, parameters):
        plugin_list = [plugin.name for plugin in self.bot.plugin_manager.getAllPlugins()]
        self.bot.msg(channel, "These are the plugins I currently have loaded: %s" % ', '.join(plugin_list))

    def deactivate_plugin(self, user, channel, parameters):
        bot_regex = r' '.join(parameters)
        plugin_list = [plugin.name for plugin in self.bot.plugin_manager.getAllPlugins()]
        deactivation_list = []
        for plugin in plugin_list:
            if re.match(bot_regex, plugin):
                self.bot.plugin_manager.deactivatePluginByName(plugin)
                deactivation_list.append(plugin)
        if len(deactivation_list) > 0:
            self.bot.msg(channel, "%s: The following plugins were deactivated: %s" % (
                self.pretty_username(user), ', '.join(deactivation_list)))