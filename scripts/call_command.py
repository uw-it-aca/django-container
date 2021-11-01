# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import django
from django.core import management
from prometheus_client import (
    start_http_server, push_to_gateway, Gauge, REGISTRY)
from croniter import croniter
from datetime import datetime
import logging
import signal
import time
import sys
import os
import gc
import re


logger = logging.getLogger(__name__)


class CallCommand:
    """Invoke Django management command
    """
    def __init__(self, *args, **kwargs):
        self.command = self.valid_command(kwargs.get('command'))
        self.options = kwargs.get('options')
        self.is_daemon = kwargs.get('is_daemon', False)
        if self.is_daemon:
            self.cron_spec, self.loop_delay = self.valid_loop_values(
                kwargs.get('cron_spec'), kwargs.get('loop_delay'))

        metric_name_prefix = 'management{}_command_'.format(
            '_daemon' if self.is_daemon else '')
        metrics = {
            'start': {'name': metric_name_prefix + 'start',
                      'description': 'Management Command start time'},
            'finish': {'name': metric_name_prefix + 'finish',
                       'description': 'Management Command finish time'},
            'duration': {'name': metric_name_prefix + 'duration',
                         'description': 'Management Command duration'},
            'exit': {'name': metric_name_prefix + 'exit',
                     'description': 'Management Command return value'}
        }

        self.metrics = Metrics(
            metrics=metrics, command=self.command, is_daemon=self.is_daemon)

        self.signals = Signals()

        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
        django.setup()

    def valid_command(self, command):
        if self.null_value(command):
            self.abort('missing command')

        return command

    def valid_loop_values(self, cron_spec, loop_delay):
        if self.null_value(cron_spec):
            if self.null_value(loop_delay):
                self.abort('missing cron specification')
            elif not re.match('^[0-9]+$', loop_delay):
                self.abort('non-integer loop delay')

            return (None, int(loop_delay))
        elif not self.null_value(loop_delay):
            self.abort("must define either delay or cron, not both")
        elif not croniter.is_valid(cron_spec):
            self.abort("invalid cron specification")

        return (cron_spec, None)

    def null_value(self, value):
        return not (value is not None and (isinstance(value, int)
                    or (isinstance(value, str) and len(value) > 0)))

    def abort(self, reason):
        logger.error(reason)
        sys.exit(-1)

    def finish_on_signal(self):
        logger.info("exit on signal ({})".format(self.signals.finish))
        sys.exit(0)

    def pause(self, lastrun_utc):
        delay = 0
        if self.cron_spec:
            c = croniter(
                self.cron_spec, datetime.utcfromtimestamp(lastrun_utc + 1))
            delay = int(c.get_next() - lastrun_utc)
        else:
            delay = self.loop_delay - int(time.time() - lastrun_utc)

        if delay > 0 and not self.signals.finish:
            gc.collect()
            time.sleep(delay)

    def run(self):
        if self.is_daemon:
            self.pause(time.time())

        while True:
            if self.signals.finish:
                self.finish_on_signal()
        
            start = time.time()
            rv = -1
            try:
                rv = management.call_command(self.command, *self.options)
            except SystemExit as ex:
                rv = int(str(ex))
            except Exception as ex:
                rv = -1
                logger.error("exception: {}".format(ex))
        
            finish = time.time()
            duration = finish - start
        
            self.metrics.collect([
                ('start', start),
                ('finish', finish),
                ('duration', duration),
                ('exit', rv if rv and isinstance(rv, int) else 0)])

            if self.is_daemon:
                self.pause(start)
            else:
                self.metrics.flush()
                break


class Signals:
    """Catch and expose signals
    """
    signals = [signal.SIGHUP, signal.SIGINT, signal.SIGQUIT,
               signal.SIGTERM, signal.SIGWINCH]
    _finish_signal = None

    def __init__(self, *args, **kwargs):
        for signum in self.signals:
            signal.signal(signum, self.handler)

    def handler(self, signum, frame):
        if signum in self.signals:
            self._finish_signal = signum
        else:
            logger.error("signal {}".format(signum))

    @property
    def finish(self):
        return self._finish_signal


class Metrics:
    """Record and expose prometheus metrics

       NOTE: only sets Guages
    """
    def __init__(self, *args, **kwargs):
        self.command = kwargs.get('command')
        self.release_id = os.getenv('RELEASE_ID')
        if not self.release_id:
            m = re.match(r'(.+?)-daemon-.+$', os.getenv('HOSTNAME', ''))
            self.release_id = m.group(1) if m else 'default'

        self.metrics = {}
        for key, metrics in kwargs.get('metrics', []).items():
            self.metrics[key] = Gauge(
                metrics['name'], metrics['description'], ['job', 'instance'])

        if kwargs.get('is_daemon', False):
            start_http_server(9100)

    def collect(self, metrics):
        for key, value in metrics:
            try:
                self.metrics[
                    key].labels(self.command, self.release_id).set(value)
            except KeyError:
                logger.error('unknown metric: {}'.format(key))

    def flush(self):
        pushgateway = os.getenv('PUSHGATEWAY')
        if pushgateway:
            push_to_gateway('{}:9091'.format(pushgateway),
                            job=self.command, registry=REGISTRY)
