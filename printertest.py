from PIL import Image, ImageEnhance, ImageDraw, ImageFont
from brother_ql.conversion import convert
from brother_ql.backends.helpers import send
from brother_ql.raster import BrotherQLRaster


im = ImageEnhance.Contrast(Image.open('temp_nametag.png')).enhance(2.0)
im = im.convert("L")

printer_ip = "10.147.138.174"

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

send(instructions=instructions, printer_identifier=printer, backend_identifier=backend, blocking=True)
