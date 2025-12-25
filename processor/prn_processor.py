import time
from pathlib import Path

from config import bot, CHAT_ID, PNG_FOLDER
from state import (
    TEMP_STORAGE,
    processed_file_set,
    in_progress_file_set,
    state_lock,
)
from ocr.prn_converter import convert_prn_to_png
from ocr.ocr_extractor import extract_data_from_image
from utils.text_utils import safe_int_from_currency
from telegram_bot.sender import send_photo
from processor.violation_checker import check_vi_pham


async def process_prn(prn_path: Path):
    prn_abs = str(prn_path.resolve())

    with state_lock:
        if prn_abs in processed_file_set or prn_abs in in_progress_file_set:
            return
        in_progress_file_set.add(prn_abs)

    timestamp = int(time.time() * 1000)
    png_path = PNG_FOLDER / f"{prn_path.stem}_{timestamp}.png"
    png_abs = str(png_path.resolve())

    try:
        if not convert_prn_to_png(prn_path, png_path):
            return

        with state_lock:
            in_progress_file_set.add(png_abs)

        data = extract_data_from_image(png_path)
        so_hd = data.get("so_hd", "Không tìm thấy")
        loai = data.get("loai_hoa_don", "")

        with state_lock:
            TEMP_STORAGE.setdefault(so_hd, {})
            if "tạm tính" in loai.lower():
                TEMP_STORAGE[so_hd]["tam_tinh"] = {"data": data}
            else:
                TEMP_STORAGE[so_hd]["thanh_toan"] = {"data": data}

        tien_raw = data.get("tien")
        tien_int = safe_int_from_currency(tien_raw)
        tien_fmt = f"{tien_int:,}".replace(",", ".") if tien_int else tien_raw

        msg = (
            f"📄 *{loai.upper()}*\n"
            f"Số HĐ: `{so_hd}`\n"
            f"🏷 Phòng: *{data.get('phong')}*\n"
            f"⏰ *Giờ Vào:* {data.get('gio_vao')} → *Giờ ra:* {data.get('gio_ra')}\n"
            f"⏳ *Tổng giờ:* {data.get('tong_gio')}\n"
            f"💰 *Thành tiền:* *{tien_fmt} VNĐ*\n"
            f"📅 *In lúc*: {data.get('ngay_in')} {data.get('gio_in')}"
        )

        await send_photo(bot, CHAT_ID, png_path.read_bytes(), msg)
        await check_vi_pham(so_hd)

    finally:
        try:
            if png_path.exists():
                png_path.unlink()
        except Exception:
            pass

        with state_lock:
            processed_file_set.update({prn_abs, png_abs})
            in_progress_file_set.difference_update({prn_abs, png_abs})
