#!/app/bin/python3

import django
from django.core import management
from prometheus_client import start_http_server, Gauge
import time
import sys
import os
import re


management_daemon_command_start = Gauge(
    'management_daemon_command_start',
    'Management Command start time',
    ['job', 'instance'])
management_daemon_command_start = Gauge(
    'management_daemon_command_finish',
    'Management Command finish time',
    ['job', 'instance'])
management_daemon_command_duration = Gauge(
    'management_daemon_command_duration',
    'Management Command curation',
    ['job', 'instance'])


loop_delay = 15
command = None
options = []
our_arg = True


def abort(reason):
    print("{}: {}".format(sys.argv[0].split('/')[-1], reason), file=sys.stderr)
    sys.exit(1)


# parse our args before the command's
for arg in sys.argv[1:]:
    if our_arg:
        if not loop_delay:
            if not re.match('^[1-9][0-9]*$', arg):
                abort('invalid loop delay')
            loop_delay = int(arg)
        elif arg == '--delay':
            loop_delay = None
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
    

if not command:
    abort('missing command')

# open metrics endpoint
start_http_server(int(os.getenv('PORT', '8000')))

release_id = os.getenv('RELEASE_ID', None)
if not release_id:
    m = re.match(r'(.+?)-daemon-.+$', os.getenv('HOSTNAME', ''))
    release_id = m.group(1) if m else 'default'

# init django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

# run provided management command in a loop
while True:
    start = time.time()

    management.call_command(command, *options)

    finish = time.time()
    management_daemon_command_start.labels(
        command, release_id).set(start)
    management_daemon_command_finish.labels(
        command, release_id).set(finish)
    management_daemon_command_duration.labels(
        command, release_id).set(finish - start)

    time.sleep(loop_delay)
