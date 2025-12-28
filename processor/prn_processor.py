import time
from pathlib import Path

from config import bot, CHAT_ID, PNG_FOLDER_TAMTINH, PNG_FOLDER_THANHTOAN
from ocr.prn_converter import convert_prn_to_png
from ocr.ocr_extractor import extract_data_from_image
from telegram_bot.sender import send_photo
from processor.violation_checker import check_vi_pham, check_vi_pham_item_gia_re
from utils.text_utils import safe_int_from_currency
from state import TEMP_STORAGE, state_lock, processed_file_set, in_progress_file_set


async def process_prn(prn_path: Path, loai_hd: str):
    prn_abs = str(prn_path.resolve())

    with state_lock:
        if prn_abs in processed_file_set or prn_abs in in_progress_file_set:
            return
        in_progress_file_set.add(prn_abs)

    png_folder = PNG_FOLDER_TAMTINH if loai_hd == "tam_tinh" else PNG_FOLDER_THANHTOAN
    png_path = png_folder / f"{prn_path.stem}_{int(time.time())}.png"
    png_abs = str(png_path.resolve())

    try:
        if not convert_prn_to_png(prn_path, png_path):
            return

        data = extract_data_from_image(png_path)
        print("data", data)
        so_hd = data["so_hd"]

        tien_moi = safe_int_from_currency(data["tien"])
        tien_fmt = f"{tien_moi:,}" if tien_moi else data["tien"]
        printed_at = f"{data.get('ngay_in')} {data.get('gio_in')}"

        # -----------------------------
        # Init storage + history
        with state_lock:
            invoice_store = TEMP_STORAGE.setdefault(so_hd, {})
            loai_store = invoice_store.setdefault(loai_hd, {})
            history = loai_store.setdefault("history", [])

            history.append(
                {
                    "printed_at": printed_at,
                    "tien": tien_moi,
                    "raw_tien": data["tien"],
                }
            )

            lan_in = len(history)

        # -----------------------------
        # Quyết định gửi Telegram
        send_telegram = True

        if loai_hd == "tam_tinh" and lan_in >= 2:
            tien_cu = history[-2]["tien"]
            if tien_cu == tien_moi:
                send_telegram = False
        # -----------------------------
        # Gửi Telegram
        if send_telegram:
            msg = (
                f"📄 *HÓA ĐƠN {'TẠM TÍNH' if loai_hd=='tam_tinh' else 'THANH TOÁN'}*\n"
                f"Số HĐ: `{so_hd}`\n"
                f"🏷 Phòng: *{data.get('phong')}*\n"
                f"⏰ *Giờ Vào:* {data.get('gio_vao')} → *Giờ ra:* {data.get('gio_ra')}\n"
                f"⏳ *Tổng giờ:* {data.get('tong_gio')}\n"
                f"💰 *Thành tiền:* *{tien_fmt} VNĐ*\n"
                f"📅 *In lúc*: {printed_at}"
            )

            if loai_hd == "tam_tinh":
                msg += f"\n🖨 *Lần in:* {lan_in}"

            await send_photo(bot, CHAT_ID, png_path.read_bytes(), msg)

        # ✅ CHỈ CHECK VI PHẠM KHI THANH TOÁN
        if loai_hd == "thanh_toan":
            await check_vi_pham(so_hd)
            await check_vi_pham_item_gia_re(so_hd, data.get("items", []))

    finally:
        with state_lock:
            processed_file_set.update({prn_abs, png_abs})
            in_progress_file_set.discard(prn_abs)
            in_progress_file_set.discard(png_abs)

        if prn_path.exists():
            prn_path.unlink()

        if png_path.exists():
            png_path.unlink()
