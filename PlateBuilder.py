from PIL import Image, ImageDraw, ImageFont

plate_bg = [
    './plate_template/plate_original.png'
]


class Plate(object):
    def __init__(self, bg_path, width, height):
        self.width = width
        self.height = height
        self.img = Image.open(bg_path)

    def resize_img(self, size):
        resized = self.img.resize(size)
        return resized

    def img_show(self):
        self.img.show()

    def build_drawable_image(self):
        draw = ImageDraw.Draw(self.img)
        return draw


class Number(object):
    def __init__(self, font_path):
        self.font_path = font_path

    def build_font(self, size):
        font = ImageFont.truetype(self.font_path, size)
        return font

    def build_characters(self, draw, pos, scale, text, color):
        size = scale * 60
        font = self.build_font(size)
        draw.text(pos, text, font=font, fill=color)


plate = Plate(bg_path=plate_bg[0], width=500, height=300)
drawable = plate.build_drawable_image()

