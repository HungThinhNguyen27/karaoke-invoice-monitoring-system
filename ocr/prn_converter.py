import numpy as np
from PIL import Image
from pathlib import Path


def convert_prn_to_png(prn_path: Path, png_path: Path) -> bool:
    try:
        data = prn_path.read_bytes()
    except Exception:
        return False

    bitmap_rows = []
    i = 0

    while i + 7 < len(data):
        if data[i : i + 3] == b"\x1d\x76\x30":
            xL, xH, yL, yH = data[i + 4 : i + 8]
            w = xL + (xH << 8)
            h = yL + (yH << 8)
            size = w * h
            start = i + 8
            end = start + size
            bitmap_rows.append((data[start:end], w, h))
            i = end
        else:
            i += 1

    if not bitmap_rows:
        return False

    rows = []
    for buf, w, h in bitmap_rows:
        bits = np.unpackbits(np.frombuffer(buf, dtype=np.uint8))
        rows.append(bits.reshape((h, w * 8)))

    img = Image.fromarray((1 - np.vstack(rows)) * 255).convert("RGB")
    img.save(png_path)

    try:
        prn_path.unlink()
    except Exception:
        pass

    return True
