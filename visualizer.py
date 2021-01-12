import imutils
import cv2
import numpy as np
import re
from PIL import ImageFont, ImageDraw, Image
import cv2

img = cv2.imread('plate_template/plate_UZB_5.png')
fontpath = 'plate_template/CARGO2.TTF'
font_small = ImageFont.truetype(fontpath, 50)
font_large = ImageFont.truetype(fontpath, 65)
space = ' '


def part1(text, color=(0, 0, 0), pos=(25, 20)):
    global img
    img_pil = Image.fromarray(img)
    draw = ImageDraw.Draw(img_pil)
    draw.text(pos, text, font=font_small, fill=color)
    img = np.array(img_pil)
    # cv2.putText(img, text, pos, cv2.FORMATTER_FMT_PYTHON, 2.3, color, 3)


def part2(text, color=(0, 0, 0), pos=(120, 10)):
    global img
    img_pil = Image.fromarray(img)
    draw = ImageDraw.Draw(img_pil)
    print(text)
    draw.text(pos, text, font=font_large, fill=color)
    img = np.array(img_pil)


def setBg(file):
    global img
    img = cv2.imread(file)
    img = imutils.resize(img, width=500)


line = "01A899KP"
if re.search("^[0-9]{2}[A-Z]{1}[0-9]{3}[A-Z]{2}", line):
    setBg('plate_template/plate_original.png')
    part1(line[:2])
    part2(f'{line[2]}_{line[3:6]}_{line[6:]}')
elif re.search("^[0-9]{2}[0-9]{4}[A-Z]{2}", line):
    setBg('plate_template/plate_UZB_1.png')
    temp = line
    part1(temp[:2])
    part2(str(temp[2:6]) + " " + str(temp[6:]))
elif re.search("^[A-Z]{1}[0-9]{6}", line):
    setBg('plate_template/plate_UZB_2.png')
    temp = line
    part1(str(temp[:1]) + " " + str(temp[1:]))
elif re.search("^[A-Z]{3}[0-9]{2}[0-9]{2}", line):
    setBg('plate_template/plate_UZB_3.png')
    temp = line
    part1(str(temp[:3]) + " " + str(temp[3:5]) + "-" + str(temp[5:7]))
elif re.search("^[0-9]{2}[T]{1}[0-9]{6}", line) or re.search("^[0-9]{2}[M]{1}[0-9]{6}", line):
    setBg('plate_template/plate_UZB_4.png')
    temp = line
    part1(str(temp[:2]))
    part2(str(temp[2]) + " " + str(temp[3:]))
elif re.search("^[0-9]{2}[H]{1}[0-9]{6}", line):
    setBg('plate_template/plate_UZB_5.png')
    temp = line
    part1(str(temp[:2]))
    part2(str(temp[2]) + " " + str(temp[3:]))
elif re.search("[A-Z]{2}[0-9]{4}", line):
    setBg('plate_template/plate_UZB_5.png')
    temp = line
    part1("     " + str(temp[:2]) + " " + str(temp[2:]))
else:
    part1('No Plate Match')

cv2.imshow('plate', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
