from plugin import CommandPlugin

OWNER = 4
ADMIN = 3
OP = 2
VOICE = 1
USER = 0


class NotLoadedError(Exception):
    pass


def permissions(level=OWNER):
    """
    Provides a decorator to enable/disable permissions based on
    """

    def wrapper(func):
        def wrapped_function(self, user, channel, parameters):
            try:
                assert isinstance(self, CommandPlugin)
                user = self.pretty_username(user).lower()
                if not getattr(self, 'users', None):
                    raise NotLoadedError
                print user
                print self.users
                if user not in self.users:
                    raise PermissionError
                print self.users
                if not any([x >= level for x in self.users[user]]):
                    raise PermissionError
                func(self, user, channel, parameters)
            except PermissionError:
                self.bot.msg(channel, "Sorry %s, you don't have access to that command." % self.pretty_username(user))
            except NotLoadedError:
                self.bot.msg(channel,
                             "AnkhMorporkian: There is no permission object! This is definitely a bug. Fix it you moron.")
            except AssertionError:
                print "This can only be used in a CommandPlugin."

        return wrapped_function

    return wrapper


class PermissionError(Exception):
    pass


class UserManager(CommandPlugin):
    name = "User Manager"
    description = "Provides user management via IRC. Should be the only plugin at priority 0."
    priority = 0

    def activate(self):
        super(UserManager, self).activate()
        if 'users' not in self.config:
            self.config['users'] = {self.bot.config['AnkhBot']['owner'].lower(): [OWNER, ADMIN]}

        CommandPlugin.users = self.config['users']
        print self.users
        self.commands = {
            "list_users": self.list_users,
            "add_user": self.add_user,
            "mod_user": self.mod_user,
            "del_user": self.del_user
        }
        self.mapping = {
            "owner": OWNER,
            "admin": ADMIN,
            "op": OP,
            "voice": VOICE,
            "user": USER,
        }

    @permissions(ADMIN)
    def list_users(self, user, channel, parameters):
        self.bot.msg(channel, "I have the following users in permission list: %s" % ", ".join(self.users.iterkeys()))

    @permissions(ADMIN)
    def add_user(self, user, channel, parameters):
        new_user, level = parameters
        if new_user.lower() in self.users:
            self.bot.msg(channel, "That user already exists.")
        elif not level.isdigit():
            if level.lower() not in self.mapping:
                self.bot.msg(channel, "The access level much be a digit or a level in the following: ." % ", ".join(
                    self.mapping.iterkeys()))
            else:
                self.users[new_user.lower()] = [self.mapping[level.lower()]]
                self.bot.msg(channel, "Added user.")
        else:
            if int(level) > OWNER:
                self.bot.msg(channel, "That access level is higher than owner. Refusing to add.")
            else:
                self.users[new_user.lower()] = [int(level)]
                self.bot.msg(channel, "Added user.")

    @permissions(ADMIN)
    def del_user(self, user, channel, parameters):
        if parameters[0].lower() in self.users and parameters[0].lower() != self.bot.config["AnkhBot"]["owner"].lower():
            del (self.users[parameters[0].lower()])
            self.bot.msg(channel, "Deleted user")
        else:
            if parameters[0].lower() == self.bot.config["AnkhBot"]["owner"].lower():
                self.bot.msg(channel, "Can't delete the bot owner you silly person you!")
            else:
                self.bot.msg(channel, "User not found.")

    @permissions(ADMIN)
    def mod_user(self, user, channel, parameters):
        self.bot.msg(channel, "Use this to modify users.")


