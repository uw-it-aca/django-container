#!/usr/bin/env python

import django
from django.core import management
from prometheus_client import Counter, push_to_gateway
from datetime import datetime
import time
import sys
import signal
import os
import re
import gc


#
# Run django management command on a continuous loop
# delaying "--delay <seconds>" between each invocation,
# and gracefully exiting on termination signal
#
def main():
    signals = [signal.SIGHUP, signal.SIGINT, signal.SIGQUIT,
               signal.SIGTERM, signal.SIGWINCH]
    finish_signal = None
    command = None
    options = []
    our_arg = True

    def report(message, error=False):
        print("management command daemon: {}: {}".format(
            command if command else sys.argv[1:], message),
              file=sys.stderr if error else sys.stdout)

    def abort(reason):
        report(reason, error=True)
        sys.exit(-1)

    def handler(signum, frame):
        nonlocal finish_signal

        if signum in signals:
            finish_signal = signum
        else:
            report("signal {}".format(signum), error=True)

    # prepare to exit gracefully
    for signum in signals:
        signal.signal(signum, handler)

    # prepare metrics
    management_command_start = Gauge(
        'management_command_start',
        'Management Command start time',
        ['job', 'instance'])
    management_command_finish = Gauge(
        'management_command_finish',
        'Management Command finish time',
        ['job', 'instance'])
    management_command_duration = Gauge(
        'management_command_duration',
        'Management Command duration',
        ['job', 'instance'])
    management_command_exit = Gauge(
        'management_command_exit',
        'Management Command return value',
        ['job', 'instance'])

    # parse our args from command's
    for arg in sys.argv[1:]:
        if not command:
            command = arg
        else:
            options.append(arg)

    if command is None:
        abort('missing command')

    release_id = os.getenv('RELEASE_ID', None)
    if not release_id:
        m = re.match(r'(.+?)-daemon-.+$', os.getenv('HOSTNAME', ''))
        release_id = m.group(1) if m else 'default'

    # initialize django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
    django.setup()

    # run provided management command
    start = time.time()
    rv = -1
    try:
        rv = management.call_command(command, *options)
    except SystemExit as ex:
        rv = int(str(ex))
    except Exception as ex:
        rv = -1
        report("exception: {}".format(ex), error=True)

    finish = time.time()
    duration = finish - start

    pushgateway = os.getenv('PUSHGATEWAY')
    if pushgateway:
        management_command_exit.labels(
            command, release_id).set(rv if rv and isinstance(rv, int) else 0)
        management_command_start.labels(
            command, release_id).set(start)
        management_command_finish.labels(
            command, release_id).set(finish)
        management_command_duration.labels(
            command, release_id).set(duration)

        push_to_gateway('{}:9091'.format(pushgateway), job=command)


if __name__ == '__main__':
    main()
