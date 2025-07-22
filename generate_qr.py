import qrcode.constants
import streamlit as st
import qrcode
import io
import os
import cairosvg
from PIL import Image, ImageDraw
from urllib.parse import urlparse

st.set_page_config(page_title="QR Code Generator", layout="centered")
st.title("QR Code Generator")

pallets = {
    "Black": ["#000000", "#000000", "#000000", "#000000", "#000000"],
    "Blue": ["#00c6ff", "#0072ff", "#0048ff", "#001f7f", "#00004d"],
    "Green": ["#a8ff78", "#78ffd6", "#48ffbb", "#00b386", "#004d40"],
    "Orange": ["#ffd194", "#ffba6f","#ff8f43", "#d95c00", "#7f3300"],
    "Purple": ["#d4a4ff", "#a766ff", "#7733ff", "#4d00b3", "#2a005d"],
    "Pink": ["#ffc0cb", "#ff99b6", "#ff6699", "#e60073", "#99004d"],
    "Red": ["#ff7f7f", "#ff4c4c", "#e60000", "#990000", "#4d0000"]
}

NO_COLORIZE = {"github", "instagram", "gmail"}

# Function to convert hex color to RGB
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# Function to create a vertical smooth gradient image
def diagonal_gradient(size, colors):
    width, height = size
    gradient = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(gradient)
    
    n = len(colors) - 1
    
    for y in range(height):
        for x in range(width):
            dist = ((x + y) / (width + height)) * n
            segment = int(dist)
            if segment >= n:
                segment = n - 1
            ratio = dist - segment
            c1 = colors[segment]
            c2 = colors[segment + 1]
            r = int(c1[0] + (c2[0] - c1[0]) * ratio)
            g = int(c1[1] + (c2[1] - c1[1]) * ratio)
            b = int(c1[2] + (c2[2] - c1[2]) * ratio)
            draw.point((x, y), fill=(r, g, b))

    return gradient

# QR color Instagram Style
def generate_qr_color_gradient(url, colors_hex):
    # 1. Black & White QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("L")
    
    # 2. Color Gradient Instagram Style
    colors_rgb = [hex_to_rgb(c) for c in colors_hex]
    gradient = diagonal_gradient(qr_img.size, colors_rgb)
    
    # Invert the QR code for masking
    mask = Image.eval(qr_img, lambda x: 255 - x)
    
    # 3. Combine QR and Gradient
    colored_qr = Image.composite(gradient, Image.new("RGB", qr_img.size, "white"), mask)
    
    return colored_qr, gradient

def extract_domain(text):
    if not text:
        return ""
    if "@" in text:
        return text.split("@")[-1].lower()
    try:
        parsed_url = urlparse(text)
        domain = parsed_url.netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except:
        return ""

def get_logo_image(domain, size=120):
    if not domain:
        return None
    filename = domain.split(".")[0]
    logo_path = os.path.join("logos", f"{filename}.svg")
    if os.path.exists(logo_path):
        try:
            with open(logo_path, 'rb') as svg_file:
                svg_data = svg_file.read()
                png_data = cairosvg.svg2png(bytestring=svg_data, output_width=size, output_height=size)
                return Image.open(io.BytesIO(png_data)).convert("RGBA")
        except Exception as e:
            print(f"Error loading logo from {logo_path}: {e}")
    return None     

def colorize_logo(logo_img, rgb_color):
    r, g, b = rgb_color[:3]
    colored = Image.new("RGBA", logo_img.size)
    for x in range(logo_img.width):
        for y in range(logo_img.height):
            pixel = logo_img.getpixel((x, y))
            alpha = pixel[3]
            if alpha == 0:
                colored.putpixel((x, y), (0, 0, 0, 0))  # Transparent pixel
            else:
                r_adj = max(0, int(r * 0.9))
                g_adj = max(0, int(g * 0.9))
                b_adj = max(0, int(b * 0.9))
                colored.putpixel((x, y), (r_adj, g_adj, b_adj, alpha))
    return colored

def force_black_logo(logo_img):
    black = (0, 0, 0)
    colored = Image.new("RGBA", logo_img.size)
    for x in range(logo_img.width):
        for y in range(logo_img.height):
            pixel = logo_img.getpixel((x, y))
            alpha = pixel[3]
            if alpha == 0:
                colored.putpixel((x, y), (0, 0, 0, 0))
            else:
                colored.putpixel((x, y), (*black, alpha))
    return colored

def add_logo_with_border(qr_img, logo_img, factor=8, border_factor=1.3):
    # Ensure the QR code image is in RGBA mode
    if qr_img.mode != "RGBA":
        qr_img = qr_img.convert("RGBA")
    
    qr_width, qr_height = qr_img.size
    logo_size = qr_width // factor
    
    # Resize logo
    logo_img = logo_img.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
    if logo_img.mode != "RGBA":
        logo_img = logo_img.convert("RGBA")
    
    # Create a border around the logo
    border_size = int(logo_size * border_factor)
    border_img = Image.new("RGBA", (border_size, border_size), (0, 0, 0, 0))
    
    # Draw a white circle as border
    draw = ImageDraw.Draw(border_img)
    draw.ellipse((0, 0, border_size, border_size), fill=(255, 255, 255, 255))
    
    pos_logo = ((border_size - logo_size) // 2, (border_size - logo_size) // 2)
    border_img.paste(logo_img, pos_logo, logo_img)
    
    # Paste the logo onto the border
    pos_qr = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)
    qr_img.paste(border_img, pos_qr, border_img)
    
    return qr_img

# Input URL or text for QR code generation
url = st.text_input("Enter URL or text to generate QR code:")

if url:
    
    # Extract domain for logo
    domain = extract_domain(url)
    domain_name = domain.split(".")[0].lower()
    
    names = list(pallets.keys())
    
    if domain_name in NO_COLORIZE:
        idx = names.index("Black")
        current_pallets_name = st.selectbox(
            "Choose QR Code Color", 
            names,
            index=idx, 
            disabled=True)
    
    else:
        current_pallets_name = st.selectbox("Choose QR Code Color", names)
    current_pallets = pallets[current_pallets_name]
    
    # Génération QR + logo
    if domain_name in NO_COLORIZE:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=2,
        )
        qr.add_data(url)
        qr.make(fit=True)
        qr_image = qr.make_image(fill_color="black", back_color="white").convert("RGBA")

        logo_img = get_logo_image(domain_name)
        if logo_img:
            logo_img = force_black_logo(logo_img)
            qr_image = add_logo_with_border(qr_image, logo_img, factor=8, border_factor=1.3)
    else:
        qr_image, gradient = generate_qr_color_gradient(url, current_pallets)
        qr_image = qr_image.convert("RGBA")
        logo_img = get_logo_image(domain)
        if logo_img:
            center_color = qr_image.getpixel((qr_image.width // 2, qr_image.height // 2))[:3]
            logo_img = colorize_logo(logo_img, center_color)
            qr_image = add_logo_with_border(qr_image, logo_img, factor=8, border_factor=1.3)
    
    # Display QR code
    img_col1, img_col2, img_col3 = st.columns([1, 2, 1])
    with img_col2:
        st.image(qr_image, use_container_width=True)
    
    # Save QR code to a buffer
    buf = io.BytesIO()
    qr_image.save(buf, format="PNG")
    buf.seek(0)
    
    # Provide download link
    btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])
    with btn_col2:
        st.download_button(
            label = "Download QR Code",
            data = buf,
            file_name = "qr_code.png",
            mime = "image/png",
            use_container_width=True
        )