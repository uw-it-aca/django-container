# Gunicorn configuration file.

# Server socket

bind = 'unix:/var/run/gunicorn/gunicorn.sock'
backlog = 2048

# Worker processes

workers = 3
worker_class = 'sync'
max_requests = 1000
max_requests_jitter = 30
worker_tmp_dir = '/dev/shm'
timeout = 30
keepalive = 3

# Debug

check_config = False
spew = False

# Server mechanics

daemon = False
raw_env = []
pidfile = None
umask = 0
user = 'acait'
group = 'acait'
chdir = '/app'

# Logging

errorlog = '-'
loglevel = 'info'
capture_output = True
accesslog = None

# Server hooks

def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def pre_fork(server, worker):
    pass

def pre_exec(server):
    server.log.info("Forked child, re-executing.")

def when_ready(server):
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    worker.log.info("worker received INT or QUIT signal")

    ## get traceback info
    import threading, sys, traceback
    id2name = {th.ident: th.name for th in threading.enumerate()}
    code = []
    for threadId, stack in sys._current_frames().items():
        code.append("\n# Thread: %s(%d)" % (id2name.get(threadId,""),
            threadId))
        for filename, lineno, name, line in traceback.extract_stack(stack):
            code.append('File: "%s", line %d, in %s' % (filename,
                lineno, name))
            if line:
                code.append("  %s" % (line.strip()))
    worker.log.debug("\n".join(code))

def worker_abort(worker):
    worker.log.info("worker received SIGABRT signal")

