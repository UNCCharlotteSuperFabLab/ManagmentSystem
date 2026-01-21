from PIL import Image, ImageEnhance, ImageDraw, ImageFont

image = Image.open('sfl-id-template.png')
max_length = 790
size = 90
font_path = "arial.ttf"
draw = ImageDraw.Draw(image)
text = "Bayli Wolfe"
icon_1_pos = (248, 395)
icon_2_pos = (390, 395)
icon_3_pos = (533, 395)
icon_4_pos = (676, 395)
icon_5_pos = (248, 535)
icon_6_pos = (390, 535)
icon_7_pos = (0, 0)
icon_8_pos = (0, 0)

cert_icons_list = {
    "Policies and Procedures": {
        "img": "policies-icon.png",
        "position": icon_1_pos
    },
    "Orientation": {
        "img": "orientation-icon.png",
        "position": icon_2_pos
    },
    "3D Printer": {
        "img": "3d-printer-icon.png",
        "position": icon_3_pos
    },
    "Laser Cutter": {
        "img": "laser-cutter-icon.png",
        "position": icon_4_pos
    },
    "Resin Printer": {
        "img": "resin-printer-icon.png",
        "position": icon_5_pos
    },
    "Waterjet": {
        "img": "waterjet-icon.png",
        "position": icon_6_pos
    },
    
}

while True:
    font = ImageFont.truetype(font_path, size=size)
    text_length = draw.textlength(text, font=font)

    if text_length <= max_length:
        break
    size -= 1
    if size < 10:  # safety stop
        break


draw.text((533, 250), text, fill="black", font=font, anchor="mm")

for cert in cert_icons_list:
    cert_icon = Image.open(cert_icons_list[cert]["img"]).resize((140,140))
    cert_icon_position = cert_icons_list[cert]["position"]
    image = image.convert("RGBA")
    cert_icon = cert_icon.convert("RGBA")
    image.paste(cert_icon, cert_icon_position, cert_icon)

image.save("temp_nametag.png")