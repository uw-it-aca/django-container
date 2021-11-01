#!/usr/bin/env python

# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

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
