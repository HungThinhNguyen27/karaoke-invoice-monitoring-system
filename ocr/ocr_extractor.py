import re
from PIL import Image
import pytesseract
from utils.text_utils import normalize_text


def extract_data_from_image(image_path):
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img, lang="vie")
    norm = normalize_text(text)
    print("norm", norm)
    items = extract_items_from_norm(norm)
    # loai = "Hóa đơn thanh toán" if "thanh toan" in norm else "Hóa đơn tạm tính"

    so_hd_match = re.search(r"HD\.?(\d+)", text)
    so_hd = f"HD.{so_hd_match.group(1)}" if so_hd_match else "Không tìm thấy"

    # ===== 1. PHÒNG =====
    matches = list(re.finditer(r"phong[:\s]*([a-z]+\s*\d+)", norm))
    phong = "Không tìm thấy"
    for m in matches:
        before = norm[max(0, m.start() - 15) : m.start()]
        if "loai" not in before:
            phong = m.group(1).title()
            break

    # ===== 2. GIỜ VÀO / GIỜ RA =====
    tg = re.search(r"Giờ vào[:\s]*([\d:]+).*?Giờ ra[:\s]*([\d:]+)", text, re.DOTALL)
    gio_vao = tg.group(1) if tg else "-"
    gio_ra = tg.group(2) if tg else "-"

    # ===== 3. TỔNG GIỜ =====
    tong_gio = "-"
    m2 = re.search(r"Tổng giờ[:\s]*([^\n\r]+)", text, re.IGNORECASE)
    if m2:
        tong_gio = m2.group(1).strip()

    # ===== 4. Thành tiền =====
    tt = re.search(r"Thành tiền[:\s]*([\d\.,]+)", text)
    thanhtien = tt.group(1) if tt else "-"

    # ===== 5. thời gian in =====
    time_date = re.search(r"(\d{1,2}:\d{2})\s+(\d{2}/\d{2}/\d{4})", text)
    gio_in, ngay_in = time_date.groups() if time_date else ("-", "-")

    return {
        "so_hd": so_hd,
        "phong": phong,
        "gio_vao": gio_vao,
        "gio_ra": gio_ra,
        "tong_gio": tong_gio,
        "tien": thanhtien,
        "gio_in": gio_in,
        "ngay_in": ngay_in,
        "items": items,
    }


def extract_items_from_norm(norm_text: str):
    """
    Parse danh sách mặt hàng từ norm text (đã normalize)
    Return:
    [
        {
            "ten": str,
            "so_luong": int,
            "thanh_tien": int
        }
    ]
    """

    items = []
    lines = [l.strip() for l in norm_text.splitlines() if l.strip()]

    # Các dòng KHÔNG phải item
    skip_keywords = (
        "tong tien",
        "thanh tien",
        "tien gio",
        "bang chu",
        "xin cam on",
        "thu ngan",
        "gio vao",
        "gio ra",
        "tong gio",
        "loai phong",
        "so hd",
        "mat hang",
    )

    for line in lines:
        # Skip các dòng tổng hợp
        if any(k in line for k in skip_keywords):
            continue

        # Regex: tên + số lượng + (bỏ qua đơn giá) + thành tiền (cuối dòng)
        m = re.search(
            r"""
            ^([a-z\s]+?)              # tên mặt hàng
            \s+(\d{1,4})              # số lượng
            (?:                       # --- nhóm OPTIONAL cho thành tiền ---
                .*?                   # bỏ qua đơn giá
                (\d{1,7}(?:[.,]\d{3})*)   # thành tiền: 8 | 100 | 1.000 | 180.000
            )?$                        # <-- OPTIONAL
            """,
            line,
            re.VERBOSE,
        )

        if not m:
            continue

        ten = m.group(1).strip().title()
        so_luong = int(m.group(2))

        thanh_tien_raw = m.group(3)
        thanh_tien = int(thanh_tien_raw.replace(".", "").replace(",", ""))

        items.append(
            {
                "ten": ten,
                "so_luong": so_luong,
                "thanh_tien": thanh_tien,
            }
        )

    return items
