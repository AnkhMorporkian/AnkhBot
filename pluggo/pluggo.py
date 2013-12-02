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
            instance_method = getattr(plugin['instance'], method, None)
            if instance_method is not None:
                instance_method(*args, **kwargs)

    def __init__(self):
        self.plugins = []
        self.directory = None

    def load_plugins(self, directory, plugin_class=PluggoPlugin, attach=None,
                     call_default=False, watch_for_changes=True):
        sys.path.append(directory)
        self.directory = directory
        base_methods = set([method[0] for method in inspect.getmembers(plugin_class)])
        for plugin_candidate in glob.glob("%s/*.py" % directory.rstrip("/")):
            with open(plugin_candidate) as plugin_file:
                name = ".".join(plugin_candidate.split(".")[:-1]).split('/')[-1]
                module = imp.load_module(name, plugin_file, directory, (".py", "r", imp.PY_SOURCE))
                for name, obj in inspect.getmembers(module):
                    if obj is plugin_class:
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
                                self.plugins.append(plugin_information)

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