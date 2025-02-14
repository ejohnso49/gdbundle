import subprocess


def test_gdb():
    subprocess.run(["gdb", "--command", "tests/gdbinit", "--batch"], check=True)


def test_lldb():
    import sys
    env = {
        "PYTHONPATH": ":".join(sys.path[1:])
    }
    subprocess.run(["lldb", "-s", "tests/lldbinit", "--batch"], check=True, env=env)
