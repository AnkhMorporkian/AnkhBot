import datetime
from configobj import ConfigObj
from twisted.internet.task import LoopingCall
from twisted.words.protocols import irc
from twisted.internet import protocol
from twisted.internet import reactor
from yapsy.PluginManager import PluginManagerSingleton


def plugin_router(target_function_name):
    """
    plugin_router provides a decorator to send the arguments from a Twisted IRC function to the more readable ones
    in the AnkhBotPlugin class.

    Usage:
    @plugin_router("plugin_function_name")
    def twisted_function_name(*args, **kwargs):
    """
    def wrapper(func):
        def wrapped_function(self, *args, **kwargs):
            func(self, *args, **kwargs)
            for plugin in self.plugin_manager.getAllPlugins():
                if hasattr(plugin.plugin_object, target_function_name):
                    getattr(plugin.plugin_object, target_function_name)(*args, **kwargs)
        return wrapped_function
    return wrapper


class AnkhBot(irc.IRCClient):
    """
    AnkhBot is a plugin-driven IRC bot. The plugins are mediated by yapsy.

    TODO: Add support for every notification event. Currently only privmsg, join, and connect are tracked.
    """
    def __init__(self):
        """
        PluginManagerSingleton is shared across all plugins and the bot. We hack in access to the bot from the
        plugins themselves by settings self.plugin_manager.bot = self. In a plugin class, we simply retrieve
        the singleton in that class and call self.plugin_manager.bot.

        history is a list of dicts of previous lines of conversations, and timers is a dictionary by name
        of any Twisted LoopingCall's.
        """
        self.plugin_manager = PluginManagerSingleton().get()
        self.plugin_manager.bot = self
        self.plugin_manager.setPluginPlaces(["plugins"])
        self.plugin_manager.collectPlugins()
        self.history = []
        self.timers = {}

    def _get_nickname(self):
        return self.factory.nickname

    def _get_config(self):
        return self.factory.config

    config = property(_get_config)  # Due to how Twisted handles shit, these are necessary.
    nickname = property(_get_nickname)

    def get_plugin_name(self, obj):
        """
        Returns the plugin name given an instance. Used from the plugins themselves to retrieve
        their own information.
        """
        for plugin in self.plugin_manager.getAllPlugins():
            if plugin.plugin_object is obj:
                print plugin.name
                return plugin.name
        raise KeyError  # This should never happen.

    def add_timer(self, seconds, function, name):
        timer = LoopingCall(f=function)
        timer.start(interval=seconds)
        self.timers[name] = timer

    def stop_timer(self, name):
        if name in self.timers:
            self.timers[name].stop()
        else:
            raise KeyError

    @plugin_router("on_connect")
    def signedOn(self):
        for channel in self.factory.channels:
            self.join(channel)
        for plugin in self.plugin_manager.getAllPlugins():
            self.plugin_manager.activatePluginByName(plugin.name)
        print "Connected as %s." % self.nickname

    @plugin_router("on_join")
    def joined(self, channel):
        print "Joined %s." % channel

    @plugin_router("on_message")
    def privmsg(self, user, channel, msg):
        self.history.append({"user": user, "channel": channel, "msg": msg, "time": datetime.datetime.now()})
        print "%s: <%s> %s" % (channel, user, msg)

class AnkhBotFactory(protocol.ClientFactory):
    """
    Factory to create the actual bot. Not much special here.
    """
    protocol = AnkhBot

    def __init__(self):
        self.config = ConfigObj("ankhbot.cfg")
        self.channels = self.config["AnkhBot"]['channels']
        self.nickname = self.config["AnkhBot"]["nickname"]

    def clientConnectionLost(self, connector, reason):
        print "Lost connection (%s), reconnecting." % reason
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "Could not connect: %s" % reason
        self.config.write()

if __name__ == "__main__":
    reactor.connectTCP('irc.freenode.net', 6667, AnkhBotFactory())
    reactor.run()