from plugin import CommandPlugin


class ConfigurationManager(CommandPlugin):
    name = "Configuration Manager"
    description = "Provides in-IRC configuration management"
    requires = ["Admin Commands", "User Manager"]

    def activate(self):
        super(ConfigurationManager, self).activate()
        self.global_config = self.bot.config
        print self.global_config
        self.commands = {
            "save_config": self.save_configuration,
            "show_config": self.show_config
        }

    def save_configuration(self, user, channel, parameters):
        print "Called save_configuration"
        if self.pretty_username(user.lower()) == self.global_config["AnkhBot"]["owner"].lower():
            print "Writing"
            self.global_config.write()
            self.bot.msg(self.pretty_username(user), "Configuration file saved.")

    def show_config(self, user, channel, parameters):
        print "Called show_config"
        print self.global_config