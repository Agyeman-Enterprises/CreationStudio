import os
import io
import datetime
import zipfile
import subprocess
import tempfile
from PIL import Image

OUT_DIR = os.path.expanduser("~/CreationStudio/outputs/logos")


def _ensure_dir():
    os.makedirs(OUT_DIR, exist_ok=True)


def export_png(image, scale=1):
    """Export as PNG with optional scale multiplier."""
    if image is None:
        return None
    _ensure_dir()
    if scale != 1:
        w, h = image.size
        image = image.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(OUT_DIR, f"logo_{ts}_{scale}x.png")
    image.save(path, "PNG")
    return path


def export_jpg(image, quality=95):
    """Export as JPG."""
    if image is None:
        return None
    _ensure_dir()
    rgb = image.convert("RGB")
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(OUT_DIR, f"logo_{ts}.jpg")
    rgb.save(path, "JPEG", quality=quality)
    return path


def export_svg(image):
    """Export as SVG using potrace (raster-to-vector)."""
    if image is None:
        return None
    _ensure_dir()
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Convert to BMP for potrace
    bw = image.convert("L").point(lambda x: 0 if x < 128 else 255, "1")
    with tempfile.NamedTemporaryFile(suffix=".bmp", delete=False) as tmp:
        bw.save(tmp.name, "BMP")
        bmp_path = tmp.name

    svg_path = os.path.join(OUT_DIR, f"logo_{ts}.svg")

    try:
        subprocess.run(
            ["potrace", bmp_path, "-s", "-o", svg_path],
            check=True, capture_output=True
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        # Fallback: create simple SVG with embedded image
        print("[LogoExport] potrace not found, creating embedded SVG")
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        import base64
        b64 = base64.b64encode(buf.getvalue()).decode()
        w, h = image.size
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}">
  <image width="{w}" height="{h}" xlink:href="data:image/png;base64,{b64}"/>
</svg>'''
        with open(svg_path, "w") as f:
            f.write(svg_content)
    finally:
        os.unlink(bmp_path)

    return svg_path


def export_pdf(image):
    """Export as PDF."""
    if image is None:
        return None
    _ensure_dir()
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_path = os.path.join(OUT_DIR, f"logo_{ts}.pdf")

    try:
        import img2pdf
        rgb = image.convert("RGB")
        buf = io.BytesIO()
        rgb.save(buf, format="PNG")
        buf.seek(0)
        with open(pdf_path, "wb") as f:
            f.write(img2pdf.convert(buf))
    except ImportError:
        # Fallback using Pillow
        rgb = image.convert("RGB")
        rgb.save(pdf_path, "PDF")

    return pdf_path


def export_logo_pack(image):
    """Export complete logo pack as ZIP with all formats + sizes."""
    if image is None:
        return None
    _ensure_dir()
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_path = os.path.join(OUT_DIR, f"logo_pack_{ts}.zip")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # PNG at multiple scales
        for scale in [1, 2, 4]:
            w, h = image.size
            scaled = image.resize((w * scale, h * scale), Image.LANCZOS)
            buf = io.BytesIO()
            scaled.save(buf, "PNG")
            zf.writestr(f"png/logo_{scale}x.png", buf.getvalue())

        # JPG
        rgb = image.convert("RGB")
        buf = io.BytesIO()
        rgb.save(buf, "JPEG", quality=95)
        zf.writestr("jpg/logo.jpg", buf.getvalue())

        # SVG
        svg_path = export_svg(image)
        if svg_path and os.path.exists(svg_path):
            zf.write(svg_path, "svg/logo.svg")
            os.unlink(svg_path)

        # PDF
        pdf_path = export_pdf(image)
        if pdf_path and os.path.exists(pdf_path):
            zf.write(pdf_path, "pdf/logo.pdf")
            os.unlink(pdf_path)

    print(f"[LogoExport] Logo pack saved to {zip_path}")
    return zip_path


def export_image(image, fmt="PNG"):
    """Export image in specified format. Returns file path."""
    fmt = fmt.upper()
    if fmt == "SVG":
        return export_svg(image)
    elif fmt == "PDF":
        return export_pdf(image)
    elif fmt == "JPG" or fmt == "JPEG":
        return export_jpg(image)
    else:
        return export_png(image)
