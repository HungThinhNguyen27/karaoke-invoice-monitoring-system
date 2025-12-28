import asyncio
from pathlib import Path
from watchdog.events import FileSystemEventHandler
from state import processed_file_set, in_progress_file_set, state_lock


class PRNHandler(FileSystemEventHandler):
    def __init__(self, loop, queue, loai_hd):
        self.loop = loop
        self.queue = queue
        self.loai_hd = loai_hd

    def on_created(self, event):
        if event.is_directory:
            return

        path = Path(event.src_path)

        if path.suffix.lower() != ".prn":
            return

        print("🟡 PRN EVENT:", path)

        asyncio.run_coroutine_threadsafe(
            self.queue.put((path, self.loai_hd)), self.loop
        )

    async def _enqueue(self, p):
        await asyncio.sleep(0.2)
        with state_lock:
            if str(p.resolve()) in processed_file_set:
                return
        await self.queue.put(p)


IMAGE_EXTS = (".png", ".jpg", ".jpeg")


class PNGHandler(FileSystemEventHandler):
    def __init__(self, loop, queue, loai_hd):
        self.loop = loop
        self.queue = queue
        self.loai_hd = loai_hd

    def on_created(self, event):
        if event.is_directory:
            return

        path = Path(event.src_path)

        if path.suffix.lower() not in IMAGE_EXTS:
            return

        print("🟡 PNG EVENT:", path)

        asyncio.run_coroutine_threadsafe(
            self.queue.put((path, self.loai_hd)), self.loop
        )

    async def _enqueue(self, p):
        await asyncio.sleep(0.2)
        with state_lock:
            if str(p.resolve()) in processed_file_set:
                return
        await self.queue.put(p)
