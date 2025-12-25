import asyncio
from processor.prn_processor import process_prn
from processor.png_processor import process_png


async def worker(queue: asyncio.Queue):
    while True:
        path = await queue.get()
        try:
            if path.suffix.lower() == ".prn":
                await process_prn(path)
            elif path.suffix.lower() == ".png":
                await process_png(path)
        finally:
            queue.task_done()
