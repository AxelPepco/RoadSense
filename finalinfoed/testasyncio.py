
import asyncio
import cv2

async def count(word):
    print(word)
    await asyncio.sleep(1)
    print(word + " 2")

async def func():
    c=0
    while True:
        c+=1
        print(c)
        cv2.waitKey(100)

list = [count("negrotei"), count("mare"), count("frumos")]

async def main():
    await asyncio.gather(list)

if __name__ == "__main__":
    asyncio.run(main())