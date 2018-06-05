import asyncio
import time
import concurrent.futures

from asgiref.sync import sync_to_async, async_to_sync


# async get_chat_id
async def async_get_chat_id(name):
    start = time.time()
    print('hello async_get_chat_id, %.1f sec' % (time.time() - start))
    await asyncio.sleep(3)
    print('hello async_get_chat_id, %.1f sec' % (time.time() - start))
    return "chat-%s" % name


# sync get_chat_id
def get_chat_id(name):
    start = time.time()
    print('hello get_chat_id, %.1f sec' % (time.time() - start))
    time.sleep(3)
    print('hello get_chat_id, %.1f sec' % (time.time() - start))
    return "chat-%s" % name


##### async to aysnc #####
async def async_async_main():
    id_coroutine = async_get_chat_id("django")
    result = await id_coroutine
    print(result)


##### sync to aysnc #####
async def sync_async_main():
    result = get_chat_id("django")


##### using asgiref#####
async def asgiref_sync_to_async_main():
    result = await sync_to_async(get_chat_id)("django")


##### using thread #####
async def thread_main():
    #executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)
    loop = asyncio.get_event_loop()
    #result = await loop.run_in_executor(executor, get_chat_id, "django")
    
    # 'None' default run ThreadPoolExecutor 
    result = await loop.run_in_executor(None, get_chat_id, "django")


##### main async to async #####
def call_async_async():
    loop = asyncio.get_event_loop()
    tasks = [async_async_main(), async_async_main()]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()


##### main sync to async #####
def call_sync_to_async():
    loop = asyncio.get_event_loop()
    tasks = [sync_async_main(), sync_async_main()]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()


def call_thread():
    loop = asyncio.get_event_loop()
    tasks = [thread_main(), thread_main()]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()


def call_asgiref_sync_to_aync():
    loop = asyncio.get_event_loop()
    tasks = [asgiref_sync_to_async_main(), asgiref_sync_to_async_main()]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()


##### main async to sync #####
def call_createventloop_async_to_sync():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(async_get_chat_id("django"))
    #result = async_to_sync(get_chat_id)("django")


def call_asgiref_async_to_sync():
    result = async_to_sync(async_get_chat_id)("django")


# call_async_async()

# call_sync_to_async()  # <-- has block
# call_thread()
# call_asgiref_sync_to_aync()

# call_createventloop_async_to_sync()
# call_asgiref_async_to_sync()
