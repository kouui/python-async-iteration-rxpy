
## reference:
#  - 寿司で理解する Python asyncio
#    https://qiita.com/pn11/items/c6c49a1a50009e373fc6

def run_reference_():

    import asyncio
    import datetime
    import time
    import sys


    async def cook_sushi():
        """sushiを握るのには sushi_cook_time 秒かかる"""
        print_with_time('sushi職人「sushi一丁！」')
        await asyncio.sleep(sushi_cook_time)
        print_with_time('sushi職人「sushiお待ち！」')
        return 'sushi'


    async def cook_miso():
        """misoは1秒でできる"""
        print_with_time('sushi職人「miso一丁！」')
        await asyncio.sleep(1)
        print_with_time('sushi職人「misoお待ち！」')
        return 'miso'


    def eat(dish):
        print_with_time(f"客「{dish}うまあ😋」")


    def print_with_time(str):
        print(f"{datetime.datetime.now().strftime('%H:%M:%S')} {str}")


    async def case1():
        """Case1: 寿司も味噌汁も頼んでおとなしく待ち、来た順に食う"""
        for future in asyncio.as_completed([cook_sushi(), cook_miso()]):
            result = await future
            eat(result)
        return None


    async def case2():
        """Case2: 寿司を頼んでから5秒かかっても来なかったら店を出る"""
        try:
            result = await asyncio.wait_for(cook_sushi(), timeout=5.0)
            eat(result)
        except asyncio.TimeoutError:
            print_with_time('客「sushiが来ないなら帰らせて頂く」')
        return None


    async def case3():
        """Case3: 寿司を頼んでから5秒かかっても来なかったら味噌汁を頼む"""
        for future in asyncio.as_completed([cook_sushi(), asyncio.sleep(5)]):
            result = await future
            if result == 'sushi':
                eat(result)
                break
            else:
                # sushi が来なかった場合 (asyncio.sleep(5)の戻り値は None)
                result = await cook_miso()
                eat(result)
        return None


    sushi_cook_time = int(sys.argv[1])

    print(case1.__doc__)
    time.sleep(1)
    asyncio.run(case1())
    print('')

    print(case2.__doc__)
    time.sleep(1)
    asyncio.run(case2())
    print('')

    print(case3.__doc__)
    time.sleep(1)
    asyncio.run(case3())

    return 0

import asyncio
import aiohttp

async def fetch_data_async_(session:aiohttp.ClientSession, url:str):
    async with session.get(url) as response:
        return await response.json()
    
async def scrape_async_(urls:list[str]):

    tasks : list[asyncio.Task] = []
    async with aiohttp.ClientSession() as session:
        for url in urls:
            task = asyncio.create_task(fetch_data_async_(session, url))
            tasks.append(task)

        for task in asyncio.as_completed(tasks):
            data:dict = await task
            post_process_(data)


def post_process_(data:dict):
    ssbk = data.get('ssbk')
    if ssbk is not None:
        print(ssbk[0]['SECUCODE'])
    
def test_async_iter_(n:int=3):
    print("test async with iteration")
    tscodes = ["000012.SZ","000014.SZ"] * n
    codeslist = [ts_code.split(".") for ts_code in tscodes]
    urls = [f"http://emweb.securities.eastmoney.com/PC_HSF10/CoreConception/PageAjax?code={codes[1].upper() + codes[0]}" 
            for codes in codeslist]
    asyncio.run(scrape_async_(urls))

import functools
import reactivex as rx
from rx.scheduler.eventloop import AsyncIOScheduler
from rx.disposable import Disposable

def from_aiter(iter, loop):
    def on_subscribe(observer, scheduler):
        async def _aio_sub():
            try:
                async for i in iter:
                    observer.on_next(i)
                loop.call_soon(
                    observer.on_completed)
            except Exception as e:
                loop.call_soon(
                    functools.partial(observer.on_error, e))

        task = asyncio.ensure_future(_aio_sub(), loop=loop)
        return Disposable(lambda: task.cancel())

    return rx.create(on_subscribe)

async def scrape_async_generator_(urls:list[str]):

    tasks : list[asyncio.Task] = []
    async with aiohttp.ClientSession() as session:
        for url in urls:
            task = asyncio.create_task(fetch_data_async_(session, url))
            tasks.append(task)

        for task in asyncio.as_completed(tasks):
            data:dict = await task
            yield data

def test_async_rxpy_(n:int=3):
    print("test async with iteration + rxpy")
    tscodes = ["000012.SZ","000014.SZ"] * n
    codeslist = [ts_code.split(".") for ts_code in tscodes]
    urls = [f"http://emweb.securities.eastmoney.com/PC_HSF10/CoreConception/PageAjax?code={codes[1].upper() + codes[0]}" 
            for codes in codeslist]
    
    async def wrapper_(loop):
        done = asyncio.Future()

        def on_completed():
            print("completed")
            done.set_result(True)
        def on_error():
            print("error")
            done.set_result(False)
    
        disposable = from_aiter(scrape_async_generator_(urls), loop).subscribe(
            on_next=lambda data: post_process_(data),
            on_error=on_error,
            on_completed=on_completed,
        )

        await done
        disposable.dispose()
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    loop.run_until_complete(wrapper_(loop))

if __name__ == "__main__":
    #run_reference_()
    if False: 
        test_async_iter_()
    else:
        test_async_rxpy_()
        test_async_iter_()

    ## in this order will create 
    #  [event loop not found error]
    #  in test_async_rxpy()
    #  reason : 
    #       The issue is that asyncio.run creates an event loop, 
    #       runs your coroutine, and then closes the event loop.
    test_async_iter_()
    test_async_rxpy_()