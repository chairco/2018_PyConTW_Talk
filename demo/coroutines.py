# -*- coding: utf-8 -*-
# ref:
#   https://emptysqua.re/blog/links-for-how-python-coroutines-work/
#   https://github.com/ajdavis/coroutines-demo
#
# async 起手式
#   - non-blocking sockets
#   - callbacks
#   - event loop
#
# coroutines
#   - Feature
#   - generator
#   - Task

from selectors import DefaultSelector, EVENT_WRITE, EVENT_READ
import socket
import time

selector = DefaultSelector()
n_jobs = 0
c_n_jobs = 0


##### coroutines #####
class Future:

    def __init__(self):
        self.callbacks = None

    def resolve(self):
        self.callbacks()

    def __await__(self):
        yield self


class Task:

    def __init__(self, coro):
        self.coro = coro
        self.step()

    def step(self):
        try:
            f = self.coro.send(None)
        except StopIteration:
            return

        f.callbacks = self.step
        # f.callbacks.append(self.step)


async def get_coroutines(path):
    global c_n_jobs
    c_n_jobs += 1
    s = socket.socket()
    s.setblocking(False)
    try:
        s.connect(('localhost', 5000))
    except BlockingIOError:
        pass

    f = Future()
    selector.register(s.fileno(), EVENT_WRITE, data=f)
    await f
    # s is writable
    selector.unregister(s.fileno())
    request = 'GET %s HTTP/1.0\r\n\r\n' % path
    s.send(request.encode())

    chunks = []
    #callback = lambda: readable_coroutine(s, chunks)
    while True:
        f = Future()
        # non-blocking sockets
        selector.register(s.fileno(), EVENT_READ, data=f)
        await f
        selector.unregister(s.fileno())
        chunk = s.recv(1000)
        if chunk:
            chunks.append(chunk)
        else:
            break

    body = (b''.join(chunks)).decode()
    print(body.split('\n')[0])
    c_n_jobs -= 1


##### evnet loop #####
def get_eventloop(path):
    global n_jobs
    n_jobs += 1
    s = socket.socket()
    s.setblocking(False)
    try:
        s.connect(('localhost', 5000))
    except BlockingIOError:
        pass

    callback = lambda: connected_event(s, path)
    # non-blocking sockets
    selector.register(s.fileno(), EVENT_WRITE, data=callback)


def connected_event(s, path):
    selector.unregister(s.fileno())
    request = 'GET %s HTTP/1.0\r\n\r\n' % path
    s.send(request.encode())

    chunks = []
    callback = lambda: readable_event(s, chunks)
    # non-blocking sockets
    selector.register(s.fileno(), EVENT_READ, data=callback)


def readable_event(s, chunks):
    global n_jobs
    selector.unregister(s.fileno())
    chunk = s.recv(1000)
    if chunk:
        chunks.append(chunk)
        callback = lambda: readable_event(s, chunks)
        # non-blocking sockets
        selector.register(s.fileno(), EVENT_READ, data=callback)
    else:
        body = (b''.join(chunks)).decode()
        print(body.split('\n')[0])
        n_jobs -= 1


##### aync callbacks #####
def get_callback(path):
    s = socket.socket()
    s.setblocking(False)
    try:
        s.connect(('localhost', 5000))
    except BlockingIOError:
        pass

    callback = lambda: connected(s, path)
    # non-blocking sockets
    selector.register(s.fileno(), EVENT_WRITE)
    selector.select()
    callback()


def connected(s, path):
    selector.unregister(s.fileno())
    request = 'GET %s HTTP/1.0\r\n\r\n' % path
    s.send(request.encode())

    chunks = []
    callback = lambda: readable(s, chunks)
    # non-blocking sockets
    selector.register(s.fileno(), EVENT_READ)
    selector.select()
    callback()


def readable(s, chunks):
    selector.unregister(s.fileno())
    chunk = s.recv(1000)
    if chunk:
        chunks.append(chunk)
        callback = lambda: readable(s, chunks)
        # non-blocking sockets
        selector.register(s.fileno(), EVENT_READ)
        selector.select()
        callback()
    else:
        body = (b''.join(chunks)).decode()
        print(body.split('\n')[0])
        return


##### aync non-bocking ######
def get_non_blocking(path):
    s = socket.socket()
    s.setblocking(False)
    try:
        s.connect(('localhost', 5000))
    except BlockingIOError:
        pass

    # non-blocking sockets
    selector.register(s.fileno(), EVENT_WRITE)
    selector.select()
    selector.unregister(s.fileno())

    request = 'GET %s HTTP/1.0\r\n\r\n' % path
    s.send(request.encode())

    chunks = []
    while True:
        # non-blocking sockets
        selector.register(s.fileno(), EVENT_READ)
        selector.select()
        selector.unregister(s.fileno())

        chunk = s.recv(1000)
        if chunk:
            chunks.append(chunk)
        else:
            body = (b''.join(chunks)).decode()
            print(body.split('\n')[0])
            return


##### sync #####
def get(path):
    s = socket.socket()
    s.connect(('localhost', 5000))
    request = 'GET %s HTTP/1.0\r\n\r\n' % path
    s.send(request.encode())

    chunks = []
    while True:
        chunk = s.recv(1000)
        if chunk:
            chunks.append(chunk)
        else:
            body = (b''.join(chunks)).decode()
            print(body.split('\n')[0])
            return


# sync
start = time.time()
get('/foo')
get('/bar')
print('sync took %.1f sec' % (time.time() - start))

# async --nonblocking
start = time.time()
get_non_blocking('/foo')
get_non_blocking('/bar')
print('non-blocking took %.1f sec' % (time.time() - start))

# async --callback
start = time.time()
get_callback('/foo')
get_callback('/bar')
print('callback took %.1f sec' % (time.time() - start))


# async --eventloop
start = time.time()
get_eventloop('/foo')
get_eventloop('/bar')

while n_jobs:
    events = selector.select()
    # what next?
    for key, mask in events:
        cb = key.data
        cb()
print('event_loop took %.1f sec' % (time.time() - start))


# async --coroutine
start = time.time()
Task(get_coroutines('/foo'))
Task(get_coroutines('/bar'))
while c_n_jobs:
    events = selector.select()
    # what next?
    for key, mask in events:
        fut = key.data
        fut.resolve()
print('coroutines took %.1f sec' % (time.time() - start))
