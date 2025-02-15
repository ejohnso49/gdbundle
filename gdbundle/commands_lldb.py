import lldb  # type: ignore
from gdbundle import LOADED_PLUGINS
from typing import Any


def gdbundle_list(
    debugger: Any,
    command: str,
    exe_ctx: Any,
    result: Any,
    internal_dict: dict[Any, Any],
) -> None:
    for plugin in LOADED_PLUGINS:
        print(plugin.replace("gdbundle_", ""), file=result)


lldb.debugger.HandleCommand(
    "command script add -f gdbundle.commands_lldb.gdbundle_list gdbundle_list"
)
