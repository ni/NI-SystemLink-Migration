import importlib
import pkgutil
import inspect
import slmigrate.service_plugins


def iter_namespace(ns_pkg):
    # Specifying the second argument (prefix) to iter_modules makes the
    # returned name an absolute name instead of a relative one. This allows
    # import_module to work without having to do additional modification to
    # the name.
    return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")


discovered_plugin_files = [
    importlib.import_module(name)
    for _, name, _
    in iter_namespace(slmigrate.service_plugins)
]


def load_plugins():
    instances = {}
    for module in discovered_plugin_files:
        for _, cls in module.__dict__.items():
            if isinstance(cls, type) and not inspect.isabstract(cls) and issubclass(cls, slmigrate.service.ServicePlugin):
                instance = cls()
                # using the first name as the key, this may change
                instances.update({instance.names[0]: instance})
    return instances


loaded_plugins = load_plugins()
