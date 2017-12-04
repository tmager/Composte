#!/usr/bin/env python3

import re
import os, sys

def I_dont_know_what_you_want_me_to_do(*args):
    sys.stderr.write("Unknown function requested\n")
    return True

def merge_args(args):
    new_args = []

    skip = 0
    for arg in args:
        if arg is None: return []

        if skip > 0:
            skip = skip - 1
            new_args[-1] = new_args[-1] + arg
            continue

        if arg[-1] == "\\":
            skip = 1
            arg = arg[:-1]

        new_args.append(arg)

    return new_args

def repl(callbacks, default_function = I_dont_know_what_you_want_me_to_do):
    """
    Start an interactive REPL backed by callbacks
    { command-name: function-to-invoke }
    REPL commands have the form COMMAND [ARGUMENTS], splitting on whitespace
    """

    done = False
    while not done:
        try:
            read = input(">>> ")
        except KeyboardInterrupt as e:
            print()
            break
        except EOFError as e:
            print()
            break

        components = read.split()

        if len(components) == 0:
            continue
        elif len(components) == 1:
            command = components[0]
            args = [None]
        else:
            command, args = components[0], components[1:]

        if command == "Stop-REPL":
            done = True
            continue

        args = merge_args(args)

        exec_ = callbacks.get(command, default_function)

        try:
            # We don't want coercion to boolean here, so we can't use the
            # shorthand
            if exec_(*args) == False: done = True
        except TypeError as e:
            fname, msg = str(e).split(" ", 1)
            print("{} {}".format(command, msg))

