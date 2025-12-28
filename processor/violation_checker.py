from utils.text_utils import safe_int_from_currency
from telegram_bot.sender import send_message
from config import bot, CHAT_ID
from state import TEMP_STORAGE, state_lock


async def check_vi_pham(so_hd):
    with state_lock:
        hd = TEMP_STORAGE.get(so_hd)

    if not hd:
        return

    tam_tinh_list = hd.get("tam_tinh", {}).get("history", [])
    thanh_toan_list = hd.get("thanh_toan", {}).get("history", [])

    if not tam_tinh_list or not thanh_toan_list:
        return

    # Lấy tiền
    tien_tam_tinh = [x["tien"] for x in tam_tinh_list if x["tien"]]
    tien_thanh_toan = thanh_toan_list[-1]["tien"]

    if not tien_tam_tinh or not tien_thanh_toan:
        return

    max_tam_tinh = max(tien_tam_tinh)

    if max_tam_tinh > tien_thanh_toan:
        sorted_tt = sorted(tien_tam_tinh, reverse=True)

        msg = (
            f"⚠️ *PHÁT HIỆN Hoá Đơn VI PHẠM*\n"
            f"HĐ: `{so_hd}`\n\n"
            f"💰 *Hoá Đơn Thanh toán:* {tien_thanh_toan:,} VNĐ\n"
            f"📄 *Các lần in Hoá Đơn tạm tính:*\n"
        )

        for i, t in enumerate(sorted_tt, 1):
            msg += f"{i}. {t:,} VNĐ\n"

        msg += f"\n❗ *Chênh lệch:* {max_tam_tinh - tien_thanh_toan:,} VNĐ"

        await send_message(bot, CHAT_ID, msg)


async def check_vi_pham_item_gia_re(so_hd: str, items: list):
    """
    Check các mặt hàng có thành tiền < 10.000
    Nếu có -> gửi báo cáo vi phạm Telegram
    """

    if not items:
        return

    vi_pham = [item for item in items if item.get("thanh_tien", 0) < 10_000]

    if not vi_pham:
        return

    # -----------------------------
    # Build message
    msg_lines = [
        "🚨 *Bấm Sai GIÁ TRỊ MẶT HÀNG*",
        f"Số HĐ: `{so_hd}`",
        "",
        "❗ *Mặt hàng có GIÁ TRỊ SAI:*",
    ]

    for i, item in enumerate(vi_pham, 1):
        msg_lines.append(
            f"{i}. *{item['ten']}* — SL: {item['so_luong']} — 💰Thành Tiền {item['thanh_tien']:,} VNĐ"
        )

    msg = "\n".join(msg_lines)

    await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="Markdown")
