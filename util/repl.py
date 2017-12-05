#!/usr/bin/env python3

import re
import os, sys
import inspect

def I_dont_know_what_you_want_me_to_do(*args):
    """
    Unknown command
    """
    print("Unknown command")

def stop_repl_help(*args):
    """
    Stop-REPL

    End this REPL session
    """
    pass

def last_help(*args):
    """
    last

    Show the result of the most recently run command
    """
    pass

def show_help(builtins, callbacks, fun = None, *args):
    """
    help [command]

    Display help about `command`

    External commands take precedence over builtins
    Commands prefixed with a backslash will check builtins before external
    commands
    """

    # Top level help
    if fun is None:
        fnames = callbacks.keys()
        builtins = builtins.keys()
        print(
    """help [command]

Display help about `command`. The following commands are available:

Stop-REPL""")
        for fname in fnames: print(fname)
        for builtin_name in builtins: print(builtin_name)
        return

    # Command level help

    first = callbacks
    second = builtins

    if fun[0] == "\\":
        first, second = second, first
        fun = fun[1:]

    target = first.get(fun, None)
    if target is None:
        target = second.get(fun, I_dont_know_what_you_want_me_to_do)

    doc = inspect.getdoc(target)
    print(doc)

def merge_args(args):
    """
    Merge arguments separated by escaped whitespace
    """
    new_args = []

    skip = 0
    for arg in args:
        if arg is None: return []

        if skip > 0:
            skip = skip - 1
            new_args[-1] = new_args[-1] + " " + arg
            continue

        if arg[-1] == "\\":
            skip = 1
            arg = arg[:-1]

        new_args.append(arg)

    return new_args

def the_worst_repl_you_will_ever_see(callbacks,
        default_function = I_dont_know_what_you_want_me_to_do,
        prompt = lambda : ">>> "):
    """
    Start an interactive REPL backed by callbacks
    { command-name: function-to-invoke }
    REPL commands have the form COMMAND [ARGUMENTS], splitting on whitespace
    """

    # Help is an even more builtin builtin D:
    builtins = {
        "Stop-REPL": stop_repl_help,
        "help": show_help,
        "last": last_help,
    }

    done = False
    while not done:
        try:
            read = input(prompt()).lstrip()
        except KeyboardInterrupt as e:
            print()
            break
        except EOFError as e:
            print()
            break

        components = read.split()

        if len(components) == 0:
            continue
        else:
            command, args = components[0], components[1:]

        if command == "Stop-REPL":
            done = True
            continue

        args = merge_args(args)

        # Show help
        if command == "help":
            show_help(builtins, callbacks, *args)
            continue
        elif command == "last":
            print(str(res))
            continue

        # Actually do something

        exec_ = callbacks.get(command, default_function)
        first = callbacks
        second = builtins

        if command[0] == "\\":
            first, second = second, first
            command = command[1:]

        target = first.get(command, None)
        if target is None:
            target = second.get(command, default_function)

        exec_ = target

        try:
             res = exec_(*args)
        except TypeError as e:
            fname, msg = str(e).split(" ", 1)
            print("{} {}".format(command, msg))
            continue

        if res is not None: print(str(res))

