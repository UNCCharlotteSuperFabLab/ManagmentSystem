from users.models import SpaceUser
from PIL import Image, ImageEnhance, ImageDraw, ImageFont
import os
from django.conf import settings

TEMPLATES_DIR = os.path.join(settings.BASE_DIR, "visit_tracking", "templates")

def tpl_path(name: str) -> str:
    return os.path.join(TEMPLATES_DIR, name)


class Nametag:
    full_name: str
    certifications: list

    def __init__(self, user: SpaceUser):
        from tools_and_trainings.models import Training
        self.full_name = user.get_full_name()
        self.certifications = Training.objects.get_users_trainings(user)

    

    def is_printer_online(self, ip: str, port: int = 9100, timeout: float = 1.0) -> bool:
        import socket
        try:
            with socket.create_connection((ip, port), timeout=timeout):
                return True
        except (socket.timeout, OSError):
            return False

    def build_nametag(self):
        # Placeholder for nametag building logic
        image = Image.open(tpl_path("sfl-id-template.png"))
        max_length = 790
        size = 90
        font_path = "arial.ttf"
        draw = ImageDraw.Draw(image)
        text = self.full_name #gets user's name from user object
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
            "FDM Printing": {
                "img": "3d-printer-icon.png",
                "position": icon_3_pos
            },
            "Laser Cutter": {
                "img": "laser-cutter-icon.png",
                "position": icon_4_pos
            },
            "Resin Printing": {
                "img": "resin-printer-icon.png",
                "position": icon_5_pos
            },
            "Waterjet": {
                "img": "waterjet-icon.png",
                "position": icon_6_pos
            },
            
        }

        while True:
            font = ImageFont.load_default(size=size)
            text_length = draw.textlength(text, font=font)

            if text_length <= max_length:
                break
            size -= 1
            if size < 10:  # safety stop
                break


        draw.text((533, 250), text, fill="black", font=font, anchor="mm")

        for cert in cert_icons_list:
            if cert not in [t.category.name for t in self.certifications]:
                continue
            cert_icon = Image.open(tpl_path(cert_icons_list[cert]["img"])).resize((140,140))
            cert_icon_position = cert_icons_list[cert]["position"]
            image = image.convert("RGBA")
            cert_icon = cert_icon.convert("RGBA")
            image.paste(cert_icon, cert_icon_position, cert_icon)

        image.save("temp_nametag.png")

    def print_nametag(self):
        from brother_ql.conversion import convert
        from brother_ql.backends.helpers import send
        from brother_ql.raster import BrotherQLRaster
        im = ImageEnhance.Contrast(Image.open('temp_nametag.png')).enhance(2.0)
        im = im.convert("L")

        printer_ip = "10.147.138.174"
        if not self.is_printer_online(printer_ip):
            print("Printer is offline — skipping print job.")
            return

        target_height = 696

        # Calculate the new height to maintain aspect ratio
        aspect_ratio = im.width / im.height
        new_width = int(target_height * aspect_ratio)

        # Resize the image
        im = im.resize((new_width, target_height), Image.LANCZOS)

        if im.mode == "RGBA":
            bg = Image.new("RGB", im.size, (255, 255, 255))
            bg.paste(im, mask=im.split()[-1])  # use alpha channel as mask
            im = bg
        elif im.mode != "RGB":
            im = im.convert("RGB")
            
        im.show()
        print(im.mode)



        backend = 'network'    # 'pyusb', 'linux_kernal', 'network'
        model = 'QL-810W' # your printer model.
        printer = f"tcp://{printer_ip}"
        qlr = BrotherQLRaster(model)
        qlr.exception_on_warning = True

        instructions = convert(

                qlr=qlr, 
                images=[im],    #  Takes a list of file names or PIL objects.
                label='62x100', 
                rotate='90',    # 'auto', '0', '90', '270'
                dither=True, 
                compress=True, 
                red=False,    # Only True if using Red/Black 62 mm label tape.
                dpi_600=False, 
                hq=False,    # False for low quality.
                cut=True

        )
        try:
            send(instructions=instructions, printer_identifier=printer, backend_identifier=backend, blocking=True)
        except Exception as e:
            print("Operation took longer than 2 seconds - aborting: ", e)
