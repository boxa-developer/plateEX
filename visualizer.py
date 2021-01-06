import cv2
import numpy as np
import re

img = np.zeros([120, 550, 3], dtype=np.uint8)
img.fill(255)


def part1(text):
    cv2.putText(img, text, (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 2.3, (0, 255, 0), 2)


def part2(text):
    cv2.putText(img, text, (120, 100), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 0, 0), 2)


line = "M11s1111"
if re.search("^[0-9]{2}[A-Z]{1}[0-9]{3}[A-Z]{2}", line):
    part1(line[:2])
    part2(str(line[2]) + str(line[3:6]) + str(line[6:]))
elif re.search("^[0-9]{2}[0-9]{4}[A-Z]{2}", line):
    temp = line
    part1(temp[:2])
    part2(str(temp[2:6]) + " " + str(temp[6:]))
elif re.search("^[A-Z]{1}[0-9]{6}", line):
    temp = line
    part1(str(temp[:1]) + " " + str(temp[1:]))
elif re.search("^[A-Z]{3}[0-9]{2}[0-9]{2}",line):
    temp = line
    part1(str(temp[:3])+" "+str(temp[3:5])+"-"+str(temp[5:7]))
elif re.search("^[0-9]{2}[T]{1}[0-9]{6}",line) or re.search("^[0-9]{2}[M]{1}[0-9]{6}",line):
    temp = line
    part1(str(temp[:2]))
    part2(str(temp[2])+" "+str(temp[3:]))
elif re.search("^[0-9]{2}[H]{1}[0-9]{6}",line):
    temp = line
    part1(str(temp[:2]))
    part2(str(temp[2])+" "+str(temp[3:]))
elif re.search("[A-Z]{2}[0-9]{4}",line):
    temp = line
    part1("     "+str(temp[:2])+" "+str(temp[2:]))
else:
    part1('   No Plate Match')


cv2.imshow('plate', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
