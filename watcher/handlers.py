import asyncio
from pathlib import Path
from watchdog.events import FileSystemEventHandler
from state import processed_file_set, in_progress_file_set, state_lock


class PRNHandler(FileSystemEventHandler):
    def __init__(self, loop, queue):
        self.loop = loop
        self.queue = queue

    def on_created(self, event):
        p = Path(event.src_path)
        if p.suffix.lower() == ".prn":
            self.loop.call_soon_threadsafe(asyncio.create_task, self._enqueue(p))

    async def _enqueue(self, p):
        await asyncio.sleep(0.2)
        with state_lock:
            if str(p.resolve()) in processed_file_set:
                return
        await self.queue.put(p)


class PNGHandler(FileSystemEventHandler):
    def __init__(self, loop, queue, folder):
        self.loop = loop
        self.queue = queue
        self.folder = folder

    def on_created(self, event):
        p = Path(event.src_path)
        if p.suffix.lower() == ".png":
            self.loop.call_soon_threadsafe(asyncio.create_task, self._enqueue(p))

    async def _enqueue(self, p):
        await asyncio.sleep(0.2)
        with state_lock:
            if str(p.resolve()) in processed_file_set:
                return
        await self.queue.put(p)
