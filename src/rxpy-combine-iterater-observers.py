## reference :
#  - Create a ReactiveX Observable from an Asynchronous generator in Python
#    https://heretse.medium.com/create-a-reactivex-observable-from-an-asynchronous-generator-in-python-adb9e1ebb59a

import asyncio
import functools
import reactivex as rx
from reactivex.disposable import Disposable
from reactivex import create

class ObservableHelper:
    def __init__(self, loop):
        self.loop = loop

    def from_aiter(self, iter):
        def on_subscribe(observer, scheduler):
            async def _aio_sub():
                try:
                    async for i in iter:
                        observer.on_next(i)
                    self.loop.call_soon(observer.on_completed)
                except Exception as e:
                    self.loop.call_soon(functools.partial(observer.on_error, e))

            task = asyncio.ensure_future(_aio_sub(), loop=self.loop)
            return Disposable(lambda: task.cancel())

        return create(on_subscribe)
    
import asyncio
import inspect
import random
import reactivex as rx

delay_array = [.5, 1.0, 1.5, 2.0]

async def ticker(start, delay=.5):
    for i in range(start-1, -1, -1):
        yield i
        await asyncio.sleep(delay)

async def main():
    observable_helper = ObservableHelper(asyncio.get_running_loop())

    observables = []
    for i in range(random.randrange(5)):
        observables.append(observable_helper.from_aiter(ticker(start=random.randrange(15), delay=delay_array[random.randrange(len(delay_array))])))

    done = asyncio.Future()

    def on_error(e):
        print("error: {}".format(e))
        done.set_result(False)

    def on_completed():
        print("completed")
        done.set_result(True)

    disposable = rx.combine_latest(*observables).subscribe(
        on_next=lambda i: print("next: {}".format(i)),
        on_error=lambda e: on_error,
        on_completed=on_completed
    )

    await done
    disposable.dispose()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    if not loop:
        loop = asyncio.new_event_loop()

    try:
        task = loop.create_task(main())
        loop.run_until_complete(task)
    except KeyboardInterrupt:
        print('Got signal: SIGINT, shutting down.')
    loop.close()
    assert False
    tasks = asyncio.all_tasks(loop=loop)
    for task in tasks:
        task.cancel()
    group = asyncio.gather(*tasks, return_exceptions=True)
    loop.run_until_complete(group)
    loop.close()