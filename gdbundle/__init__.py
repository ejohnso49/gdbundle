from __future__ import absolute_import

import importlib
import logging
import pkgutil
import functools

logger = logging.getLogger(__name__)

DEBUGGER = None
PLUGIN_PREFIX = "gdbundle_"
LOADED_PLUGINS = []

@functools.cache
def get_debugger():
    """
    Test importing each debuggers Python module to figure out which
    one we are in.
    """
    try:
        if importlib.util.find_spec("gdb"):
            return 'gdb'
    except Exception:
        pass

    try:
        if importlib.util.find_spec("lldb"):
            return 'lldb'
    except Exception:
        pass

    raise Exception("Could not detect debugger used")


def load_module(module_name):
    """
    Attempt to load the module with the name given.

    :param module_name: Explicit module to load. Can be called directly to load plugins
                        that don't being with `gdbundle_`.
    """
    try:
        loader_name = "{}.{}_loader".format(module_name, get_debugger())
        plugin_loader = importlib.import_module(loader_name)
    except Exception:
        logging.warning("Failed to import gdbundle module: {}".format(module_name), exc_info=True)
        return

    # Get the GDB scripts from the module
    try:
        plugin_loader.gdbundle_load()
    except Exception:
        logging.warning("gdbundle_load() failed in gdbundle module: {}".format(module_name), exc_info=True)
        return

    LOADED_PLUGINS.append(module_name)


def load_plugin(name, prefix=True):
    """
    Attempt to load the plugin with the name given.

    :param module_name: Explicit plugin to load.
    """
    load_module(PLUGIN_PREFIX + name if prefix else name)


def discover_and_load_plugins(include=None, exclude=None, additional=None):
    """
    This will load the gdbundle GDB commands and discover and load gdbundle
    plugins.
    """

    # Pull out all possible plugins matching the prefix
    plugins = [
        name.replace(PLUGIN_PREFIX, "").lower()
        for finder, name, ispkg in pkgutil.iter_modules()
        if name.startswith(PLUGIN_PREFIX)
    ]

    # Remove all plugins from the list except those in `include`
    if include:
        include = [s.lower() for s in include]
        plugins = [p for p in include if p in plugins]

    # Remove all plugins from the list that are in `exclude`
    if exclude:
        exclude = [s.lower() for s in exclude]
        plugins = [p for p in plugins if p not in exclude]

    for name in plugins:
        # Import the plugin module
        load_plugin(name)

    if additional:
        for name in additional:
            # Import other plugins that don't use PLUGIN_PREFIX
            load_plugin(name, prefix=False)


def load_commands():
    """
    Load the GDB commands for gdbundle
    """
    debugger = get_debugger()
    if debugger == 'gdb':
        from gdbundle import commands_gdb
    elif debugger == 'lldb':
        from gdbundle import commands_lldb


def init(include=None, exclude=None, additional=None):
    """
    The default entry point for gdbundle. This will load the gdbundle GDB
    commands and discover and load gdbundle plugins.

    :param include: Plugin names to load. All others will be ignored.
    :param exclude: Plugin names to not load.

    .. note:: The plugin names passed into this function should not include `gdbundle_`.
              e.g. If a gdbundle plugin was installed using `pip install gdbundle_example`,
              then it would be included by using `gdbundle.init(include=["example"])
    """
    load_commands()
    discover_and_load_plugins(include=include, exclude=exclude, additional=additional)
