import streamlit as st
import qrcode
import io
from PIL import Image, ImageDraw

st.set_page_config(page_title="QR Code Generator", layout="centered")
st.title("QR Code Generator")

COLORS_GRADIENT = {
    "Black": ["#000000", "#000000", "#000000", "#000000", "#000000"],
    "Blue": ["#00c6ff", "#0072ff", "#0048ff", "#001f7f", "#00004d"],
    "Green": ["#a8ff78", "#78ffd6", "#48ffbb", "#00b386", "#004d40"],
    "Orange": ["#ffd194", "#ffba6f","#ff8f43", "#d95c00", "#7f3300"],
    "Purple": ["#d4a4ff", "#a766ff", "#7733ff", "#4d00b3", "#2a005d"],
    "Pink": ["#ffc0cb", "#ff99b6", "#ff6699", "#e60073", "#99004d"],
    "Red": ["#ff7f7f", "#ff4c4c", "#e60000", "#990000", "#4d0000"],
    "Instagram": ["#f09433", "#e6683c", "#dc2743", "#cc2366", "#bc1888"],
}

# Function to convert hex color to RGB
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# Function to create a diagonal smooth gradient image
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
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("L")
    colors_rgb = [hex_to_rgb(c) for c in colors_hex] # 2. Color Gradient Instagram Style
    gradient = diagonal_gradient(qr_img.size, colors_rgb)
    mask = Image.eval(qr_img, lambda x: 255 - x) # Invert the QR code for masking
    colored_qr = Image.composite(gradient, Image.new("RGB", qr_img.size, "white"), mask) # 3. Combine QR and Gradient
    return colored_qr, gradient

# Input URL or text for QR code generation
url = st.text_input("Enter URL or text to generate QR code:")
color_choice = st.selectbox("Choose QR Code color", list(COLORS_GRADIENT.keys()))

if url:
    qr_image, gradient_image = generate_qr_color_gradient(url, COLORS_GRADIENT[color_choice])
    
    # Display QR code
    img_col1, img_col2, img_col3 = st.columns([1, 2, 1])
    with img_col2:
        st.image(qr_image, use_container_width=True)
    
    # Save QR code to a buffer
    buffer = io.BytesIO()
    qr_image.save(buffer, format="PNG")
    buffer.seek(0)
    
    # Provide download link
    btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])
    with btn_col2:
        st.download_button(
            label = "Download QR Code",
            data = buffer,
            file_name = "qr_code.png",
            mime = "image/png",
            use_container_width=True
        )