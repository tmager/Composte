#!/usr/bin/env python3

import re
import os, sys
import inspect

def I_dont_know_what_you_want_me_to_do(*args):
    sys.stderr.write("Unknown function requested\n")

def show_help(callbacks):
            fnames = callbacks.keys()
            print(
"""help

Type `help command` for specific help.

The following commands are available:

Stop-REPL""")
            for fname in fnames: print(fname)

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

    done = False
    while not done:
        try:
            read = input(prompt())
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
        exec_ = callbacks.get(command, default_function)

        # Show docstring as help
        if command == "help" and len(args) > 0 and args[0] == "Stop-REPL":
            print("Stop-REPL\nEnd this REPL session")
            continue
        elif command == "help" and len(args) > 0 and args[0] == "help":
            show_help(callbacks)
            continue
        elif command == "help" and len(args) > 0:
            target = callbacks.get(args[0], default_function)
            doc = inspect.getdoc(target)
            print(args[0])
            print(doc)
            continue
        elif command == "help":
            show_help(callbacks)
            continue

        try:
             res = exec_(*args)
        except TypeError as e:
            fname, msg = str(e).split(" ", 1)
            print("{} {}".format(command, msg))
            continue

        if res is not None: print(res)

