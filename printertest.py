from PIL import Image, ImageEnhance
from brother_ql.conversion import convert
from brother_ql.backends.helpers import send
from brother_ql.raster import BrotherQLRaster


im = ImageEnhance.Contrast(Image.open('image.png')).enhance(2.0)
# im = im.convert("L")


target_height = 696

# Calculate the new height to maintain aspect ratio
aspect_ratio = im.width / im.height
new_width = int(target_height * aspect_ratio)

# Resize the image
im = im.resize((new_width, target_height), Image.LANCZOS)

bg = Image.new("RGB", im.size, (255,255,255))
bg.paste(im, im.split()[-1])
im = bg

im.show()
print(im.mode)



backend = 'pyusb'    # 'pyusb', 'linux_kernal', 'network'
model = 'QL-810W' # your printer model.
printer = 'usb://0x04f9:0x209c'    # Get these values from the Windows usb driver filter.  Linux/Raspberry Pi uses '/dev/usb/lp0'.

qlr = BrotherQLRaster(model)
qlr.exception_on_warning = True

801256059

instructions = convert(

        qlr=qlr, 
        images=[im],    #  Takes a list of file names or PIL objects.
        label='62', 
        rotate='90',    # 'auto', '0', '90', '270'
        dither=True, 
        compress=True, 
        red=True,    # Only True if using Red/Black 62 mm label tape.
        dpi_600=False, 
        hq=False,    # False for low quality.
        cut=True

)

send(instructions=instructions, printer_identifier=printer, backend_identifier=backend, blocking=True)
