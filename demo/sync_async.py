import asyncio
import time
import concurrent.futures

from asgiref.sync import sync_to_async


async def async_get_chat_id(name):
    start = time.time()
    print('hello async, %.1f sec' % (time.time() - start))
    await asyncio.sleep(3)
    print('hello async, %.1f sec' % (time.time() - start))
    return "chat-%s" % name


async def async_main():
    id_coroutine = async_get_chat_id("django")
    result = await id_coroutine
    print(result)


def get_chat_id(name):
    start = time.time()
    print('hello block, %.1f sec' % (time.time() - start))
    time.sleep(3)
    print('hello block, %.1f sec' % (time.time() - start))
    return "chat-%s" % name


async def main():
    result = get_chat_id("django")


async def main_sync_to_async():
    result = await sync_to_async(get_chat_id)("django")


async def thread_main():
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(executor, get_chat_id, "django")


# example of Sync from Asyc
def noblock():
    loop = asyncio.get_event_loop()
    tasks = [async_main(), async_main()]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()


def block():
    loop = asyncio.get_event_loop()
    tasks = [main(), main()]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()


def block_add_sync_to_aync():
    loop = asyncio.get_event_loop()
    tasks = [main_sync_to_async(), main_sync_to_async()]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()


def block_to_thread():
    loop = asyncio.get_event_loop()
    tasks = [thread_main(), thread_main()]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()


# noblock()
# block()
# block_to_thread()
# block_add_sync_to_aync()

