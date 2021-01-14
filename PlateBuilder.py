from PIL import Image, ImageDraw, ImageFont
import rstr
from random import choice
import re

plate_bg = [
    './plate_template/plate_original.png'
]

plate_template = [
    "^[0-9]{2}[0-9]{3}[A-Z]{3}",
    "^[0-9]{2}[A-Z]{1}[0-9]{3}[A-Z]{2}"
]

plate_types = [
    [(15, 10), (40, 10),  # stands for 01
     (80, 3),  # stands for A
     (120, 3), (152, 3), (185, 3),  # stands for 123
     (225, 3), (260, 3)],  # stands for CD

    [(15, 10), (40, 10),  # stands for 01
     (83, 3), (115, 3), (150, 3),  # stands for 123
     (190, 3), (225, 3), (260, 3)]  # stands for AAA
]
plate_color = (50, 50, 50)


class Plate(object):
    def __init__(self, bg_path, width, height):
        self.width = width
        self.height = height
        self.img = Image.open(bg_path)

    def resize_img(self, size):
        resized = self.img.resize(size)
        return resized

    def add_margin(self, top=20, right=20, bottom=20, left=20, color=(255, 255, 255)):
        width, height = self.img.size
        new_width = width + right + left
        new_height = height + top + bottom
        result = Image.new(self.img.mode, (new_width, new_height), color)
        result.paste(self.img, (left, top))
        return result

    def img_show(self):
        self.add_margin().show()

    def build_drawable_image(self):
        draw = ImageDraw.Draw(self.img)
        return draw


class Number(object):
    def __init__(self, font_path):
        self.font_path = font_path

    def build_font(self, size):
        font = ImageFont.truetype(self.font_path, size)
        return font

    def build_characters(self, draw, pos, size, text, color):
        font = self.build_font(size)
        draw.text(pos, text, font=font, fill=color)


plate_str = rstr.xeger(choice(plate_template))
num = plate_str
plate = Plate(bg_path=plate_bg[0], width=500, height=300)
drawable = plate.build_drawable_image()

car_number = Number(font_path='./plate_template/CARGO2.TTF')
p_type = plate_types[0]
not_matched = False
if re.search(plate_template[0], num):
    p_type = plate_types[1]
elif re.search(plate_template[1], num):
    p_type = plate_types[0]
else:
    not_matched = True

if not not_matched:
    for i, char in enumerate(num):
        h = 40 if i < 2 else 50
        car_number.build_characters(drawable, p_type[i], h, char, plate_color)
    plate.add_margin()
    plate.img_show()
else:
    print("Sorry! Not Match!")
