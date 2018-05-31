# [Python & Async Simplified](https://www.aeracode.org/2018/02/19/python-async-simplified/)

*ARTICLE / 19TH FEB 2018*

```
**NOTE**
This post focuses on Python 3.5 and higher, and the native async def and await support, and won't touch on the older approaches like @asyncio.coroutine.
```


As some of you may be aware, I have spent many of the last months [rewriting Channels](https://www.aeracode.org/2018/02/02/channels-20/) to be entirely based on Python 3 and its asynchronous features (`asyncio`).

Python's async framework is actually relatively simple when you treat it at face value, but a lot of tutorials and documentation discuss it in minute implementation detail, so I wanted to make a higher-level overview that deliberately ignores some of the small facts and focuses on the practicalities of writing projects that mix both kinds of code.


## Two Worlds


That first part is the most critical thing to understand - Python code can now basically run in one of two "worlds", either synchronous or asynchronous. You should think of them as relatively separate, having different libraries and calling styles but sharing variables and syntax.

You can't use a synchronous database library like `mysql-python` directly from async code; similarly, you can't use an async Redis library like `aioredis` directly from sync code. There are ways to do both, but you need to explicitly cross into the other world to run code from it.

In the synchronous world, the Python that's been around for decades, you call functions directly and everything gets processed as it's written on screen. Your only built-in option for running code in parallel in the same process is threads.

In the asynchronous world, things change around a bit. Everything runs on a central event loop, which is a bit of core code that lets you run several coroutines at once. Coroutines run synchronously until they hit an await and then they pause, give up control to the event loop, and something else can happen.

This means that synchronous and asynchronous functions/callables are *different types* - you can't just mix and match them. Try to `await` a sync function and you'll see Python complain, forget to `await` an async function and you'll get back a coroutine object rather than the result you wanted.

You actually don't need to know the fine details of how it all works to use it - just know that coroutines have to explicitly give up control via an `await`. This is different to threads or greenlets, which can context-switch at any time.

If you block a coroutine synchronously - maybe you use `time.sleep(10)` rather than `await asyncio.sleep(10)` - you don't return control to the event loop, and you'll hold up the entire process and nothing else can happen. On the plus side, nothing else can run while your code is moving through from one `await` call to the next, making race conditions harder.

This is called *cooperative multitasking*, and while it has many upsides, this silent failure mode is its main design issue. If you use a blocking synchronous call by mistake, nothing will explicitly fail, but things will just run mysteriously slowly. Python has a debug mode that will warn you about things blocking for too long, along with other common errors, but be aware of one thing - writing explicitly asynchronous code is harder than writing synchronous code.

This is one of the reasons Channels [gives you the choice](https://channels.readthedocs.io/en/latest/topics/consumers.html), rather than forcing you into always writing async; sync code is easier to write, generally safer, and has many more libraries to choose from.

You should think of your codebase as comprised of pieces of either sync code or async code - anything inside an `async def` is async code, anything else (including the main body of a Python file or class) is synchronous code. Notably, `__init__` must always be synchronous even if all the class' methods are asynchronous.


## Function Calls

So, now we have looked at the two different worlds, let's look at the main thing that can bridge between them - function calls. Inside of an async or sync function, you can write basic code as normal, but as soon as you call a function, you have the potential to switch over.

There are four cases:

+ Calling sync code from sync code. This is just a normal function call - like time.sleep(10). Nothing risky or special about this.
+ Calling async code from async code. You have to use await here, so you would do await asyncio.sleep(10)
+ Calling sync code from async code. You can do this, but as I said above, it will block the whole process and make things mysteriously slow, and you shouldn't. Instead, you need to give the sync code its own thread.
+ Calling async code from sync code. Trying to even use await inside a synchronous function is a syntax error in Python, so to do this you need to make an event loop for the code to run inside.

Let's dive deeper into each of the cases and what is actually happening.


## Sync From Sync

This is standard Python - you call an object, Python blocks and moves into the called code, runs it, and then returns the result to the caller and unblocks it.


## Async From Async

Now, things start to get interesting. When you have an asynchronous function (coroutine) in Python, you declare it with `async def`, which changes how its call behaves.

In particular, calling it will immediately return a *coroutine object*, which basically says "I can run the coroutine with the arguments you called with and return a result when you await me".

The code in the target function isn't called yet - this is merely a `promise` that the code will run and you'll get a result back, but you need to give it to the event loop to do that.

Luckily, Python has a built in statement to give a coroutine to the event loop and get the result back - `await`. That means that when you say `await asyncio.sleep(10)`, you are making a promise that the sleep function will run, and then passing it up to the event loop and waiting for the result. Let's look at an example:


```
async def get_chat_id(name):
    await asyncio.sleep(3)
    return "chat-%s" % name

async def main():
    result = await get_chat_id("django")
```

```
NOTE
This example has a deliberate sleep in it to represent a blocking operation - like talking to a database.
```


When you call `await`, the function you're in gets suspended while whatever you asked to wait on happens, and then when it's finished, the event loop will wake the function up again and resume it from the `await` call, passing any result out. In the example here, the `main()` function pauses and gives back control to the event loop, which sees that `get_chat_id` needs to run, calls it, and then that calls `await` and gets suspended with a marker to resume it in three seconds. Once it resumes, `get_chat_id` completes, returns a result, and then that makes main ready to run again and the event loop resumes it with the returned value.

Of course, this is Python, so `await` is not just some magical statement that only works on functions - it takes anything awaitable. What's actually happening is that when you call an asynchronous function, it returns a coroutine object, and then you can pass that to await to sleep your current coroutine until the one you asked to wait on exits with a result, like this:

```
async def get_chat_id(name):
    await asyncio.sleep(3)
    return "chat-%s" % name

async def main():
    id_coroutine = get_chat_id("django")
    result = await id_coroutine
```

This is how async code can have so many things happening at once - anything that's blocking calls `await`, and gets put onto the event loop's list of paused coroutines so something else can run. Everything that's paused has an associated trigger that will wake it up again - some are time-based, some are network-based, and most of them are like the example above and waiting for a result from another coroutine.

It's those operations that aren't waiting on other coroutines that allows true async, though, thanks to the event loop - there are some things it can natively do without having a Python coroutine having to manage them, like waiting for a time period to pass, or waiting for bytes to appear on a network socket.

If you ask to wait on one of these low-level operations, all of your Python coroutines are suspended while the event loop does its magic and listens to all the sockets and timers at once, thanks to some clever system calls and other programming that makes my head hurt. The event loop is really what makes everything possible, and without it, async Python would just be a super weird control flow with no actual speed benefits.

## Sync From Async

Remember when I said this was dangerous a few sections ago? I meant it. Because await is just a Python statement that you can pass a coroutine to and get the result back, it means you're free to ignore it and just call a good, old, synchronous function directly, like this:

```
def get_chat_id(name):
    time.sleep(3)
    return "chat-%s" % name

async def main():
    result = get_chat_id("django")
```

Do that, and you don't give the event loop any chance to run - you haven't paused the current coroutine and given the event loop control using `await`. That means every other coroutine that might want to run - maybe one has some bytes waiting for it on a socket, or another one was sleeping for a few seconds - don't even get a chance, and your coroutine just ignores them all and keeps running synchronous code. The event loop doesn't have some special power inside Python to interrupt you, it needs you to yield control back to it.

Now, there's a subtle distinction here between blocking and non-blocking calls. It's not going to ruin your day if you call a non-blocking synchronous function, like this:

```
def get_chat_id(name):
    return "chat-%s" % name

async def main():
    result = get_chat_id("django")
```

However, if you call a blocking function, like the Django ORM, the code inside the async function will look identical, but now it's dangerous code that might block the entire event loop as it's not `await`ing:

```
def get_chat_id(name):
    return Chat.objects.get(name=name).id

async def main():
    result = get_chat_id("django")
```

You can see how it's easy to have a non-blocking function that "accidentally" becomes blocking if a programmer is not super-aware of everything that calls it. This is why I recommend you never call anything synchronous from an async function without doing it safely, or without knowing beforehand it's a non-blocking standard library function, like `os.path.join`.

But what *is* safe? In the sync world, threading is our only built-in option for concurrency, so what we can do is spin up a new thread, get the sync function running inside it, and then have our coroutine pause and give back control to the event loop until its thread is finished and there's a result.

Python has a slightly verbose way of doing this built-in, in the form of executors:

```
def get_chat_id(name):
    return Chat.objects.get(name=name).id

async def main():
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(executor, get_chat_id, "django")
```

This is nice low-level logic if you need it, but I wanted a simpler way for Channels users, and so in the `asgiref.sync` package, which provides all of the low-level ASGI helpers, there's [two very handy functions](https://github.com/django/asgiref/blob/master/asgiref/sync.py) - `sync_to_async` and async_to_sync.

We'll get to `async_to_sync` later, but here's how you call a sync function with `sync_to_async`:

We'll get to `async_to_sync` later, but here's how you call a sync function with `sync_to_async`:

```
def get_chat_id(name):
    return Chat.objects.get(name=name).id

async def main():
    result = await sync_to_async(get_chat_id)("django")
```

You can also use it as a decorator:

```
@sync_to_async
def get_chat_id(name):
    return Chat.objects.get(name=name).id

async def main():
    result = await get_chat_id("django")
```

It encapsulates exception propagation, result handling and threading for you into a simple interface that works a a function decorator, method decorator and a direct wrapper. It's quite a simplistic wrapper, unlike `async_to_sync`, but it still reduces a few lines down to one and makes it much harder to screw up accidentally.


## Async From Sync

Here's where things get tricky. Async functions, by their very nature, need to run inside an event loop - something has to be there to handle their `await` calls, and service things like sockets and timers. If you're in a synchronous context, though, you can't `await`. Just try it:

```
async def get_chat_id(name):
    await asyncio.sleep(3)
    return "chat-%s" % name

def main():
    result = await get_chat_id("django")

# Try even loading this file and you'll get:
    result = await get_chat_id("django")
                             ^
SyntaxError: invalid syntax
```

Any of the async keywords - `await`, `async with`, and many other things, are actual `SyntaxErrors` if you declare them inside a synchronous function, class body, or file.

So, what do we do? Well, we need an event loop, so we have to make one. The secret behind Python's async support is that it's just an event loop running on top of good, old, synchronous Python. Here's how to run an async function like the above:

```
async def get_chat_id(name):
    await asyncio.sleep(3)
    return "chat-%s" % name

def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(get_chat_id("django"))
```

The `run_until_complete` method on a loop is a bit like the synchronous version of `await` - it will take a coroutine, let the event loop do its thing, and then return when it's finished. We have to call `set_event_loop` as there's global state inside asyncio that tracks what the current loop is, so when you call `asyncio.sleep()` you don't have to pass it a `loop=` argument every time.

You'll see a pattern like the above in a lot of online examples, and it's a decent way of just running a one-shot async program from a script. Even better, Python 3.7 will wrap the above inside of a helper called `asyncio.run`!

But what if you're writing a complex application, and you need to call async code from your sync code which is already inside other async code? (Cue the Inception horn sound effect!)

If you're inside sync code running inside async code, then you are, hopefully, in a thread as we discussed above. That means that you need to jump out of the thread, find the main event loop, and run something there, while blocking the thread until the async task you sent to the event loop finishes. Yes, that is as complex to program as it sounds.

The other thing you could do is make a new event loop. See, asyncio event loops are global per-thread - that means you can, in theory, run a small event loop inside your thread just to service the one async function you need, and then close it out again. I prefer not to do this, as having too many event loops running at once makes my head hurt and I'm not sure it's even a good idea.

Thus, we have `asgiref.sync.async_to_sync`. This handy wrapper will do all of the above, plus exception and return value propagation, plus detecting if you do something stupid (like trying to use it from a thread that already has an event loop running in it). All you need to do is wrap the function and pass any arguments:

```
async def get_chat_id(name):
    await asyncio.sleep(3)
    return "chat-%s" % name

def main():
    result = async_to_sync(get_chat_id)("django")
```

It also works as a decorator:

```
@async_to_sync
async def get_chat_id(name):
    await asyncio.sleep(3)
    return "chat-%s" % name

def main():
    result = get_chat_id("django")
```

The internals of `async_to_sync` are a bit more complicated than `sync_to_async`, but the key thing is that it's a single wrapper/decorator you can use in almost all contexts and it will do the Right Thing, and try and keep just one event loop going in your process.


## Await Is Your Friend

At this point, hopefully you have an understanding of how the two kinds of functions work. Async functions need to run on an event loop, and while they can call synchronous functions, it's dangerous. Sync functions just run on bare Python, and to have them call to asynchronous functions you need to either find or make an event loop to run the code in.

The framework or program file you are running inside determines what the "main mode" of your program is. Many will run synchronous by default, and so if you want to do something async (say, fetch ten URLs in parallel) you'll need to drop into async and spin up an event loop for that small section of code. Some newer ones will have an event loop running in the main thread and running everything as async by default - as Channels does - so when you want to talk to a synchronous API you need to then spin up a thread and call it.

When you are writing async code - in Channels or elsewhere - the thing you really need to consider is "am I calling synchronous code here by mistake?". It can be things other than obvious function calls - remember, context managers call `__enter__` and `__exit__` methods, and for loops call `__iter__` methods. Iterating over a Django `QuerySet` in an async function is going to do blocking synchronous operations and block your event loop!

Most of these have asynchronous equivalents in Python 3.5/3.6 - for example, there's `async with` for asynchronous context managers, and `async for` for asynchronous iterators - but they require the objects you're using them on to have provided asynchronous implementations of those operations (like defining an `__aiter__` method).

As with the story from the beginning, this is just highlighting that synchronous and asynchronous APIs are different, incompatible implementations. One library can provide both, but it means writing two entirely separate code paths and often two separate internal networking mechanisms, which is why you often see different libraries for sync versus async.

There is, however, another way. Several core parts of Channels only provide asynchronous APIs - most notably the [channel layers](http://channels.readthedocs.io/en/latest/topics/consumers.html) - and we rely on the presence of `async_to_sync` to let anyone write synchronous code call them easily. This could also be applied to other code as well - in fact, some libraries already have this sort of functionality internally.

Unfortunately, without this being a core Python concept, you'd have to pull in `asgiref` as a dependency to use these functions, but it's a deliberately lightweight package and I encourage you to use it if you're a library maintainer. The key thing I suggest is writing the base implementation in an async fashion, and then using `async_to_sync` to provide synchronous versions of the API where needed.

It's also these sorts of wrappers that could, in theory, let us start rewriting parts of a large framework like Django to be natively async but still allow backwards-compatibility. I don't have any real plans for that yet, but it's definitely something I think about sometimes; I don't want us to have to fracture the Python world into two, the sync world and the async world, when one of our main strengths is the breath and depth of libraries and bindings available.


## Looking Deeper

There's a whole lot of technical details I haven't dived into here - about how event loops are actually based on generators, or how to use `Tasks` and `Futures` - but I wanted to just try and get the basic idea of what's happening across, and the way I try to think about these problems (which is especially helpful when you're trying to debug async code). Just be aware that there are things other than coroutines that are awaitable - much like there are things other than functions in Python that are callable!

Python 3.7 will bring some improvements that help with this - most notably `asyncio.run` - but it's still limited and doesn't solve the entire issue. I'm not sure if the approach I've taken for Channels - and the `sync_to_async` and `async_to_sync` helpers that came from it - will work for Python programs and libraries in general, but so far I haven't found a reason they wouldn't.

I would also encourage you to develop your applications with `PYTHONASYNCIODEBUG` turned on - it will detect blocked coroutines, coroutines you forgot to `await`, and several other edge cases that it can be hard to catch otherwise.

Hopefully you have found this approach to Python's async functionality helpful, and if this has got you excited and you want to write some web code asynchronously, I encourage you to check out [Channels](https://channels.readthedocs.org/). If you're a library or framework author and want to chat about what it means to live in both worlds - sync and async - please poke me, I am always happy to chat about these sorts of issues!