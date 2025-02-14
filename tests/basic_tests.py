import gdbundle

def main():

    gdbundle.init()

    debugger = gdbundle.get_debugger()

    if debugger == "gdb":
        import gdb

        gdb.execute("gdbundle")
        gdb.execute("gdbundle list")
    elif debugger == "lldb":
        import lldb

        lldb.debugger.HandleCommand("gdbundle_list")


if __name__ == "__main__":
    main()
