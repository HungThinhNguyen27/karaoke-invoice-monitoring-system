import asyncio
from watchdog.observers import Observer

from config import PRN_FOLDER, PNG_FOLDER
from worker import worker
from watcher.handlers import PRNHandler, PNGHandler


async def main():
    queue = asyncio.Queue()
    loop = asyncio.get_running_loop()

    asyncio.create_task(worker(queue))

    observer_prn = Observer()
    observer_png = Observer()

    observer_prn.schedule(PRNHandler(loop, queue), str(PRN_FOLDER))
    observer_png.schedule(PNGHandler(loop, queue, PNG_FOLDER), str(PNG_FOLDER))

    observer_prn.start()
    observer_png.start()

    for f in PRN_FOLDER.iterdir():
        if f.suffix.lower() == ".prn":
            await queue.put(f)

    for f in PNG_FOLDER.iterdir():
        if f.suffix.lower() == ".png":
            await queue.put(f)

    print("🟢 SYSTEM STARTED")

    try:
        while True:
            await asyncio.sleep(1)
    finally:
        observer_prn.stop()
        observer_png.stop()
        observer_prn.join()
        observer_png.join()


if __name__ == "__main__":
    asyncio.run(main())
