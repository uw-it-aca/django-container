#!/usr/bin/env python

from call_command import CallCommand
import sys


#
# Run django management command
#
def main():
    command = None
    options = []

    for arg in sys.argv[1:]:
        if not command:
            command = arg
        else:
            options.append(arg)

    CallCommand(command=command, options=options).run()


if __name__ == '__main__':
    main()
