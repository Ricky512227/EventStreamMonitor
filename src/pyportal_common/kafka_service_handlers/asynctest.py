import asyncio


async def task1():
    print("Executing task1")
    await task2()
    print("Completes task1")


async def task2():
    print("Executing task2")
    await task3()
    print("Completes task2")


async def task3():
    print("Executing task3")
    print("Completes task3")


asyncio.run(task1())
