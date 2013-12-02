from pluggo import PluggoPlugin


class AnkhBotPlugin(PluggoPlugin):
    name = "AnkhBot base plugin"
    version = 0.1
    priority = 100
    description = "Base class for AnkhBot plugins to inherit from."

    bot = None

    def activate(self):
        """
        Called when the module is activated. Generally you'll want to put code in here instead of __init__
        to avoid unexpected behavior. If you override activate, make sure to make a super call.
        """
        self.config = {}
        if self.name in self.bot.config["Plugin Settings"]["Plugins"]:
            self.config = self.bot.config["Plugin Settings"]["Plugins"][self.name]
        else:
            self.bot.config["Plugin Settings"]["Plugins"][self.name] = {}
            self.config = self.bot.config["Plugin Settings"]["Plugins"][self.name]


    def deactivate(self):
        """
        Called on deactivation. Use this as you would a __del__ constructor for a normal class.
        Clean up any LoopingCalls, open files, or open connections.
        """
        pass

    def on_message(self, user, channel, msg):
        """
        Called when a message, private or not, is received.
        """
        pass

    def on_join(self, channel):
        pass

    def on_part(self, channel):
        pass

    def on_mode(self, channel, mode):
        pass

    def on_connect(self):
        """
        Called after a connection is made. This is called *immediately* after the plugins are initially activated,
        so unless you have a good reason you should probably just keep your methods there.
        """
        pass

    def on_notice(self, user, channel, message):
        pass

    def on_pong(self, user, secs):
        pass

    def on_self_kicked(self, channel, kicker, message):
        pass

    def on_self_nick_change(self, nick):
        pass

    def on_user_join(self, user, channel):
        pass

    def on_user_part(self, user, channel):
        pass

    def on_user_quit(self, user, quit_message):
        pass

    def on_user_kick(self, kickee, channel, kicker, message):
        pass

    def on_action(self, user, channel, data):
        pass

    def on_topic_update(self, user, channel, new_topic):
        pass

    def on_user_nick_change(self, old_nick, new_nick):
        pass

    def on_motd(self, motd):
        pass

    @staticmethod
    def pretty_username(username):
        return username.split("!")[0]


class CommandPlugin(AnkhBotPlugin):
    """
    Plugin class to provide the ability to respond to user commands easily.
    """

    def activate(self):
        super(CommandPlugin, self).activate()
        self.commands = {}

    def add_commands(self, command_dictionary):
        self.commands.update(command_dictionary)

    def tokenize_message(self, msg):
        return msg.split()

    def on_message(self, user, channel, msg):
        """
        Dispatches commands that match the self.commands dict.

        TODO: User verification via decorators.
        """
        print self.bot.config["Plugin Settings"]["command_prefix"]
        if msg[0] == self.bot.config["Plugin Settings"]["command_prefix"]:
            tokenized_message = self.tokenize_message(msg)
            command = tokenized_message[0][1:]
            parameters = tokenized_message[1:]
            if command in self.commands:
                self.commands[command](user=user, channel=channel, parameters=parameters)