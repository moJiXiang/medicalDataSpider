
import asyncio


async def async_generator():
    for i in range(3):
        await asyncio.sleep(1)
        yield i*i


async def main():
    async for i in async_generator():
        print(i)


loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(main())
finally:
    # see: https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.loop.shutdown_asyncgens
    loop.run_until_complete(loop.shutdown_asyncgens())
    loop.close()
