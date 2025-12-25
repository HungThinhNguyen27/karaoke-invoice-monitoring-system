import re
from PIL import Image
import pytesseract
from utils.text_utils import normalize_text


def extract_data_from_image(image_path):
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img, lang="vie")
    norm = normalize_text(text)

    loai = "Hóa đơn thanh toán" if "thanh toan" in norm else "Hóa đơn tạm tính"

    so_hd_match = re.search(r"HD\.?(\d+)", text)
    so_hd = f"HD.{so_hd_match.group(1)}" if so_hd_match else "Không tìm thấy"

    phong = "Không tìm thấy"
    m = re.search(r"phong[:\s]*([a-z]+\s*\d+)", norm)
    if m:
        phong = m.group(1).title()

    gio = re.search(r"Giờ vào[:\s]*([\d:]+).*?Giờ ra[:\s]*([\d:]+)", text, re.S)
    gio_vao, gio_ra = gio.groups() if gio else ("-", "-")

    tong_gio = "-"
    tg = re.search(r"Tổng giờ[:\s]*([^\n]+)", text)
    if tg:
        tong_gio = tg.group(1)

    tien = "-"
    t = re.search(r"Thành tiền[:\s]*([\d.,]+)", text)
    if t:
        tien = t.group(1)

    time_date = re.search(r"(\d{1,2}:\d{2})\s+(\d{2}/\d{2}/\d{4})", text)
    gio_in, ngay_in = time_date.groups() if time_date else ("-", "-")

    return {
        "loai_hoa_don": loai,
        "so_hd": so_hd,
        "phong": phong,
        "gio_vao": gio_vao,
        "gio_ra": gio_ra,
        "tong_gio": tong_gio,
        "tien": tien,
        "gio_in": gio_in,
        "ngay_in": ngay_in,
        "raw_text": text,
    }
