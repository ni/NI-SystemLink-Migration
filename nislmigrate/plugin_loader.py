import importlib
import pkgutil
import inspect
from types import ModuleType

from nislmigrate.service import ServicePlugin
from typing import List
from typing import Dict


class PluginLoader:
    """
    Capable of loading all plugins of a particular type from a python package.
    """
    cached_loaded_plugins = None
    plugin_package = None
    plugin_type = None

    def __init__(self, plugin_package: ModuleType, plugin_type: type):
        """
        Creates a new instance of PluginLoader
        :param plugin_package: A python package containing the plugins you want ot load.
        :param plugin_type: The plugin base class type.
        """
        self.plugin_package = plugin_package
        self.plugin_type = plugin_type

    def __get_discovered_plugin_files(self) -> List[ModuleType]:
        package_path = self.plugin_package.__path__
        package_name = self.plugin_package.__name__ + "."
        module_info_list = pkgutil.iter_modules(package_path, package_name)
        return [importlib.import_module(name) for _, name, _ in module_info_list]

    def __load_plugins(self) -> Dict[str, ServicePlugin]:
        instances = {}
        plugin_files = self.__get_discovered_plugin_files()
        for module in plugin_files:
            for _, cls in module.__dict__.items():
                if self.__is_class_a_plugin(cls):
                    instance = cls()
                    instances.update({instance.names[0]: instance})
        return instances

    def __is_class_a_plugin(self, cls: any) -> bool:
        is_instance = isinstance(cls, type)
        is_abstract = inspect.isabstract(cls)
        if is_instance and not is_abstract:
            is_subclass_of_plugin_interface = issubclass(cls, self.plugin_type)
            return is_subclass_of_plugin_interface
        return False

    def get_plugins(self) -> Dict[str, ServicePlugin]:
        """
        Gets the list of plugins loaded by this plugin loader.
        :return: List of all loaded plugins.
        """
        if self.cached_loaded_plugins is None:
            self.cached_loaded_plugins = self.__load_plugins()
        return self.cached_loaded_plugins
