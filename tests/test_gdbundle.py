import gdbundle
import pytest


@pytest.fixture
def get_debugger(mocker):
    return mocker.patch("gdbundle.get_debugger")


@pytest.fixture
def find_spec(mocker):
    return mocker.patch("gdbundle.importlib.util.find_spec")


@pytest.fixture
def import_module(mocker):
    return mocker.patch("gdbundle.importlib.import_module")


@pytest.fixture
def iter_modules(mocker):
    iter_modules = mocker.patch("gdbundle.pkgutil.iter_modules")
    iter_modules.return_value.__iter__.return_value = [
        (None, "gdbundle_test_1", None),
        (None, "bundle_test_2", None),
        (None, "gdbundle_test_2", None),
    ]
    return iter_modules


@pytest.fixture
def load_plugin(mocker):
    return mocker.patch("gdbundle.load_plugin")


@pytest.fixture
def load_module(mocker):
    return mocker.patch("gdbundle.load_module")


def test_debugger_gdb(find_spec):
    find_spec.return_value = True
    assert "gdb" == gdbundle.get_debugger()


def test_debugger_lldb(find_spec):
    # We have to clear the cache to allow the mocked function calls to return the side effect values
    gdbundle.get_debugger.cache_clear()
    find_spec.side_effect = [None, True]
    assert "lldb" == gdbundle.get_debugger()


def test_load_module(get_debugger, import_module):
    before_count = len(gdbundle.LOADED_PLUGINS)
    gdbundle.load_module("test")
    assert before_count + 1 == len(gdbundle.LOADED_PLUGINS)
    assert "test" in gdbundle.LOADED_PLUGINS


def test_load_module_missing_import(get_debugger):
    get_debugger.return_value = "gdb"
    import_module.side_effect = Exception("Failed to load module")

    before_count = len(gdbundle.LOADED_PLUGINS)
    gdbundle.load_module("test")

    assert before_count == len(gdbundle.LOADED_PLUGINS)


def test_load_module_missing_hook(get_debugger, import_module):
    del import_module.return_value.gdbundle_load

    before_count = len(gdbundle.LOADED_PLUGINS)
    gdbundle.load_module("test_1")

    assert before_count == len(gdbundle.LOADED_PLUGINS)


def test_load_plugin(load_module):
    gdbundle.load_plugin("test")
    load_module.assert_called_with(gdbundle.PLUGIN_PREFIX + "test")


def test_discover_available_plugins(mocker, iter_modules, load_plugin):
    gdbundle.discover_and_load_plugins()
    load_plugin.assert_has_calls([mocker.call("test_1"), mocker.call("test_2")])


def test_discover_include_plugins(iter_modules, load_plugin):
    gdbundle.discover_and_load_plugins(include=["test_1"])
    load_plugin.assert_called_once_with("test_1")


def test_discover_exclude_plugins(iter_modules, load_plugin):
    gdbundle.discover_and_load_plugins(exclude=["test_1"])
    load_plugin.assert_called_once_with("test_2")


def test_discover_additional_plugins(iter_modules, load_module):
    gdbundle.discover_and_load_plugins(exclude=["test_1", "test_2"], additional=["bundle_test_2"])
    load_module.assert_called_once_with("bundle_test_2")


def test_load_commands_gdb(import_module, get_debugger):
    get_debugger.return_value = "gdb"
    gdbundle.load_commands()

    import_module.assert_called_once_with(".commands_gdb", "gdbundle")


def test_load_commands_lldb(import_module, get_debugger):
    get_debugger.return_value = "lldb"
    gdbundle.load_commands()

    import_module.assert_called_once_with(".commands_lldb", "gdbundle")


def test_init(mocker):
    load_commands = mocker.patch("gdbundle.load_commands")
    discover = mocker.patch("gdbundle.discover_and_load_plugins")

    include = ["test_1", "test_2"]
    exclude = ["test_3"]
    additional = ["test_4"]

    gdbundle.init(include, exclude, additional)

    load_commands.assert_called_once()
    discover.assert_called_once_with(include=include, exclude=exclude, additional=additional)
