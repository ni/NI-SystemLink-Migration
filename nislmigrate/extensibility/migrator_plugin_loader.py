import importlib
import os
import pkgutil
import inspect
from types import ModuleType

from nislmigrate import migrators
from nislmigrate.extensibility.migrator_plugin import MigratorPlugin
from typing import List, Any


class MigratorPluginLoader:
    """
    Capable of loading all migrators of a particular type from a python package.
    """
    cached_loaded_plugins: List[MigratorPlugin] = []
    plugin_package: ModuleType = migrators
    plugin_type: type = type(int)

    def __init__(self, plugin_package: ModuleType, plugin_type: type):
        """
        Creates a new instance of PluginLoader
        :param plugin_package: A python package containing the migrators you want ot load.
        :param plugin_type: The plugin base class type.
        """
        self.plugin_package = plugin_package
        self.package_name = plugin_package.__name__
        self.plugin_type = plugin_type

    def __get_discovered_plugin_modules(self) -> List[ModuleType]:
        package_path = str(os.path.dirname(os.path.abspath(inspect.getfile(self.plugin_package))))
        module_info_list = pkgutil.iter_modules([package_path], self.package_name + '.')
        return [importlib.import_module(name) for _, name, _ in module_info_list]

    def __instantiate_plugins_from_module(self, module: ModuleType):
        return [cls() for _, cls in module.__dict__.items() if self.__is_class_a_plugin(cls)]

    def __load_plugins(self) -> List[MigratorPlugin]:
        plugin_modules: List[ModuleType] = self.__get_discovered_plugin_modules()
        plugin_classes = []
        for module in plugin_modules:
            instantiated_plugins = self.__instantiate_plugins_from_module(module)
            plugin_classes.extend(instantiated_plugins)
        return plugin_classes

    def __is_class_a_plugin(self, cls: Any) -> bool:
        is_instance: bool = isinstance(cls, type)
        is_abstract: bool = inspect.isabstract(cls)
        if is_instance and not is_abstract:
            is_subclass_of_plugin_interface: bool = issubclass(cls, self.plugin_type)
            return is_subclass_of_plugin_interface
        return False

    def get_plugins(self) -> List[MigratorPlugin]:
        """
        Gets the list of migrators loaded by this plugin loader.
        :return: List of all loaded migrators.
        """
        if not self.cached_loaded_plugins:
            self.cached_loaded_plugins = self.__load_plugins()
        return self.cached_loaded_plugins
