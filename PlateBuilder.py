from PIL import Image, ImageDraw, ImageFont

plate_bg = [
    './plate_template/plate_original.png'
]

plate_types = [
    [(15, 10), (40, 10), (80, 3), (125, 3), (155, 3), (185, 3), (225, 3), (260, 3)]
]

# (15, 10), 40, '0', plate_color)
# car_number.build_characters(drawable, (40, 10), 40, '1', plate_color)
# car_number.build_characters(drawable, (80, 3), 50, 'A', plate_color)
# car_number.build_characters(drawable, (125, 3), 50, '5', plate_color)
# car_number.build_characters(drawable, (155, 3), 50, '5', plate_color)
# car_number.build_characters(drawable, (185, 3), 50, '5', plate_color)
# car_number.build_characters(drawable, (225, 3), 50, 'A', plate_color)
# car_number.build_characters(drawable, (260, 3), 50, 'B', plate_color)
plate_color = (50, 50, 50)


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

    def build_characters(self, draw, pos, size, text, color):
        font = self.build_font(size)
        draw.text(pos, text, font=font, fill=color)


num = '01A123CD'
plate = Plate(bg_path=plate_bg[0], width=500, height=300)
drawable = plate.build_drawable_image()

car_number = Number(font_path='./plate_template/CARGO2.TTF')

for i, char in enumerate(num):
    h = 40 if i < 2 else 50
    car_number.build_characters(drawable, plate_types[0][i], h, char, plate_color)

plate.img_show()
