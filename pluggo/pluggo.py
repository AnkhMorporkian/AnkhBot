"""
Implements a simple plug-in manager.
"""
import imp
import glob
import inspect
import sys
import time
from watchdog.observers import Observer
from pluggo_plugin import PluggoPlugin


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Pluggo(object):
    """
    Singleton object that gathers plugins, stores information about them, allows unloading and reloading,
    watches for live filesystem changes and attempts to reload them, and allows dynamic dispatch.

    TODO:

    """
    __metaclass__ = Singleton
    _instance = None

    def call(self, method, *args, **kwargs):
        for plugin in self.plugins:
            try:
                instance_method = getattr(plugin['instance'], method, None)
                if instance_method is not None:
                    if method == "activate": print "Activating %s" % plugin['name']
                    instance_method(*args, **kwargs)
            except KeyError:
                print "Key error in call function; plugin without an instance. %s" % str(plugin)

    def __init__(self):
        self.plugins = []
        self.directory = None
        self.plugin_class = None
        self.ignore_subclasses = None
        self.attach = None
        self.call_default = None
        self.watch = None

    def load_plugins(self, directory, plugin_class=PluggoPlugin, ignore_subclasses=(), attach=None,
                     call_default=False, watch_for_changes=True):
        sys.path.append(directory)
        self.directory = directory
        self.plugin_class = plugin_class
        self.ignore_subclasses = ignore_subclasses
        self.attach = None
        self.call_default = call_default
        self.watch = watch_for_changes

        for plugin_candidate in glob.glob("%s/*.py" % directory.rstrip("/")):
            with open(plugin_candidate) as plugin_file:
                name = ".".join(plugin_candidate.split(".")[:-1]).split('/')[-1]
                module = imp.load_module(name, plugin_file, directory, (".py", "r", imp.PY_SOURCE))
                for name, obj in inspect.getmembers(module):
                    if obj is plugin_class or obj in ignore_subclasses:
                        continue
                    if inspect.isclass(obj):
                        if issubclass(obj, plugin_class):
                            try:
                                plugin_information = {
                                    "name": obj.name,
                                    "version": obj.version,
                                    "description": obj.description,
                                    "priority": obj.priority,
                                    "requires": obj.requires,
                                    "class": obj,
                                    "instance": obj(),
                                    "module": module,
                                    "default_method": obj._default_method,
                                }
                                if attach is not None:
                                    setattr(obj, *attach)
                                if not any([o.__class__ is obj for o in self.plugins]):
                                    self.plugins.append(plugin_information)
                                else:
                                    print "Didn't add, duplicate."

                            except TypeError:
                                methods = set(
                                    [method[0] for method in inspect.getmembers(obj, predicate=inspect.ismethod)])
                                print "Unable to instantiate %s due to missing methods. " \
                                      "Please ensure all of the following methods are implemented: %s" % (
                                          name, ", ".join(methods))
                            except KeyError:
                                print "Unable to access all information attributes in %s. " \
                                      "Please ensure you have the necessary information attributes in your class definition." % name
                        else:
                            print "%s is NOT an instance of %s!" % (name, str(plugin_class))
                self.plugins.sort(key=lambda k: k['priority'])
                if call_default:
                    for plugin in self.plugins:
                        method = getattr(plugin['instance'], plugin['default_method'], None)
                        if method is not None:
                            method()

    def reload_plugins(self, activate=True):
        print "reload_plugins called"
        self.call("deactivate")
        for plugin in self.plugins:
            try:
                del plugin['instance']
            except KeyError:
                continue
        del self.plugins
        self.plugins = []
        time.sleep(.1)
        self.load_plugins(self.directory, self.plugin_class, self.ignore_subclasses, self.attach, False, self.watch)
        if activate: self.call("activate")

    def watch_for_changes(self):
        event_handler = self.reload_file()
        observer = Observer()
        observer.schedule(event_handler, path=self.directory, recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        finally:
            observer.stop()
        observer.join()

    def get_plugin_by_name(self, name):
        return [plugin for plugin in self.plugins if plugin['name'].lower() == name.lower()][0]

    def reload_file(self):
        pass