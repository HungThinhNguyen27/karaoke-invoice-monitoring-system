import asyncio
from watchdog.observers import Observer
from config import (
    PRN_FOLDER_TAMTINH,
    PRN_FOLDER_THANHTOAN,
    PNG_FOLDER_TAMTINH,
    PNG_FOLDER_THANHTOAN,
)
from watcher.handlers import PRNHandler, PNGHandler
from worker import worker


async def main():
    queue = asyncio.Queue()
    loop = asyncio.get_running_loop()

    # start worker
    asyncio.create_task(worker(queue))

    # prn_tamtinh = PRNHandler(loop, queue, "tam_tinh")
    # prn_thanhtoan = PRNHandler(loop, queue, "thanh_toan")

    # --------------------------
    # Watchdog PRN tam_tinh
    prn_tamtinh = PRNHandler(loop, queue, "tam_tinh")
    observer_prn_tamtinh = Observer()
    observer_prn_tamtinh.schedule(prn_tamtinh, str(PRN_FOLDER_TAMTINH), recursive=False)
    observer_prn_tamtinh.start()

    # Watchdog PRN thanh_toan
    prn_thanhtoan = PRNHandler(loop, queue, "thanh_toan")
    observer_prn_thanhtoan = Observer()
    observer_prn_thanhtoan.schedule(
        prn_thanhtoan, str(PRN_FOLDER_THANHTOAN), recursive=False
    )
    observer_prn_thanhtoan.start()
    # --------------------------
    # Watchdog PNG tam_tinh
    png_tamtinh = PNGHandler(loop, queue, "tam_tinh")
    observer_png_tamtinh = Observer()
    observer_png_tamtinh.schedule(png_tamtinh, str(PNG_FOLDER_TAMTINH), recursive=False)
    observer_png_tamtinh.start()

    # Watchdog PNG thanh_toan
    png_thanhtoan = PNGHandler(loop, queue, "thanh_toan")
    observer_png_thanhtoan = Observer()
    observer_png_thanhtoan.schedule(
        png_thanhtoan, str(PNG_FOLDER_THANHTOAN), recursive=False
    )
    observer_png_thanhtoan.start()

    IMAGE_EXTS = (".png", ".jpg", ".jpeg")

    # scan PRN tam_tinh
    for f in PRN_FOLDER_TAMTINH.iterdir():
        if f.is_file() and f.suffix.lower() == ".prn":
            await queue.put((f, "tam_tinh"))

    # scan PRN thanh_toan
    for f in PRN_FOLDER_THANHTOAN.iterdir():
        if f.is_file() and f.suffix.lower() == ".prn":
            await queue.put((f, "thanh_toan"))

    # scan PNG tam_tinh
    for f in PNG_FOLDER_TAMTINH.iterdir():
        if f.is_file() and f.suffix.lower() in IMAGE_EXTS:
            await queue.put((f, "tam_tinh"))

    # scan PNG thanh_toan
    for f in PNG_FOLDER_THANHTOAN.iterdir():
        if f.is_file() and f.suffix.lower() in IMAGE_EXTS:
            await queue.put((f, "thanh_toan"))

    print("🟢 SYSTEM STARTED")

    try:
        while True:
            await asyncio.sleep(1)
    finally:
        observer_prn_tamtinh.stop()
        observer_prn_tamtinh.join()
        observer_prn_thanhtoan.stop()
        observer_prn_thanhtoan.join()
        # # PNG
        # observer_png_tamtinh.stop()
        # observer_png_tamtinh.join()
        # observer_png_thanhtoan.stop()
        # observer_png_thanhtoan.join()


if __name__ == "__main__":
    asyncio.run(main())
