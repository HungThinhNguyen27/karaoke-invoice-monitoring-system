from processor.prn_processor import process_prn
from processor.png_processor import process_png

IMAGE_EXTS = (".png", ".jpg", ".jpeg")


async def worker(queue):
    while True:
        path, loai_hd = await queue.get()
        print("🟢 WORKER GOT:", path, loai_hd)
        try:
            if path.suffix.lower() == ".prn":
                await process_prn(path, loai_hd)
            elif path.suffix.lower() in IMAGE_EXTS:
                await process_png(path, loai_hd)
        except Exception as e:
            print(f"🔥 Worker error: {e}")
        finally:
            queue.task_done()
