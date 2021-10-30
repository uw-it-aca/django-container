#!/usr/bin/env python

# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from call_command import CallCommand
import sys


#
# Run django management command on a continuous loop
# delaying "--delay <seconds>" between each invocation,
# and gracefully exiting on termination signal
#
def main():
    loop_delay = 15
    cron_spec = None
    command = None
    options = []
    our_arg = True

    # sift daemon from management command arguments
    for arg in sys.argv[1:]:
        if our_arg:
            if not loop_delay:
                loop_delay = arg
            elif cron_spec is not None and len(cron_spec) == 0:
                cron_spec = arg
            elif arg == '--delay':
                loop_delay = None
            elif arg == '--cron':
                cron_spec = ""
            elif arg == '--':
                our_arg = False
            else:
                command = arg
                our_arg = False
        elif not command:
            command = arg
            our_arg = False
        else:
            options.append(arg)

    CallCommand(is_daemon=True, command=command, options=options,
                cron_spec=cron_spec, loop_delay=loop_delay).run()


if __name__ == '__main__':
    main()
