import asyncio
import time

async def say_after1():
    while True:
        print("kk")
        await asyncio.sleep(1)

async def say_after2():
    while True:
        print("pp")
        await asyncio.sleep(1)

async def main():
    task1 = asyncio.create_task(say_after1())
    task2 = asyncio.create_task(say_after2())

    await task1
    await task2

asyncio.run(main())