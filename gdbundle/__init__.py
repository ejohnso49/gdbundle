import importlib.util
import logging
import pkgutil
import functools

logger = logging.getLogger(__name__)

DEBUGGER = None
PLUGIN_PREFIX = "gdbundle_"
LOADED_PLUGINS = []


@functools.cache
def get_debugger() -> str:
    """
    Test importing each debuggers Python module to figure out which
    one we are in.
    """
    try:
        if importlib.util.find_spec("gdb"):
            return "gdb"
    except Exception:
        pass

    try:
        if importlib.util.find_spec("lldb"):
            return "lldb"
    except Exception:
        pass

    raise Exception("Could not detect debugger used")


def load_module(module_name: str) -> None:
    """
    Attempt to load the module with the name given.

    :param module_name: Explicit module to load. Can be called directly to load plugins
                        that don't being with `gdbundle_`.
    """
    try:
        loader_name = "{}.{}_loader".format(module_name, get_debugger())
        plugin_loader = importlib.import_module(loader_name)
    except Exception:
        logging.warning(
            "Failed to import gdbundle module: {}".format(module_name), exc_info=True
        )
        return

    # Get the GDB scripts from the module
    try:
        plugin_loader.gdbundle_load()
    except Exception:
        logging.warning(
            "gdbundle_load() failed in gdbundle module: {}".format(module_name),
            exc_info=True,
        )
        return

    LOADED_PLUGINS.append(module_name)


def load_plugin(name: str) -> None:
    """
    Attempt to load the plugin with the name given.

    :param module_name: Explicit plugin to load.
    """
    load_module(PLUGIN_PREFIX + name)


def discover_and_load_plugins(
    include: list[str] | None = None,
    exclude: list[str] | None = None,
    additional: list[str] | None = None,
) -> None:
    """
    This will load the gdbundle GDB commands and discover and load gdbundle
    plugins.
    """

    # Pull out all possible plugins matching the prefix
    plugins = [
        name.replace(PLUGIN_PREFIX, "").lower()
        for _, name, _ in pkgutil.iter_modules()
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
            load_module(name)


def load_commands() -> None:
    """
    Load the GDB commands for gdbundle
    """
    debugger = get_debugger()
    if debugger == "gdb":
        importlib.import_module(".commands_gdb", __package__)
    elif debugger == "lldb":
        importlib.import_module(".commands_lldb", __package__)


def init(
    include: list[str] | None = None,
    exclude: list[str] | None = None,
    additional: list[str] | None = None,
) -> None:
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
