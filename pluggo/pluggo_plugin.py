import abc

__author__ = 'ankhmorporkian'


class PluggoPlugin(object):
    __metaclass__ = abc.ABCMeta
    _default_method = 'activate'
    priority = 100
    requires = None

    @abc.abstractmethod
    def activate(self):
        pass

    @abc.abstractmethod
    def deactivate(self):
        pass
