import cv2
import numpy as np

img = cv2.imread('./train_images/pk/train/01E332AB_8.jpg')
img = cv2.resize(img, (600, 200))
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
cv2.imshow('gray', gray)
blur = cv2.GaussianBlur(gray, (75, 75), 0)
division = cv2.divide(gray, blur, scale=200)
thresh = cv2.threshold(division, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
detected_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
cnts = cv2.findContours(detected_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = cnts[0] if len(cnts) == 2 else cnts[1]
mult = 1.2
for c in cnts:
    rect = cv2.minAreaRect(c)
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    print(box, '----')
    cv2.drawContours(img, [box], 0, (0, 255, 0), 2)
    W = rect[1][0]
    H = rect[1][1]

    Xs = [i[0] for i in box]
    Ys = [i[1] for i in box]
    x1 = min(Xs)
    x2 = max(Xs)
    y1 = min(Ys)
    y2 = max(Ys)

    rotated = False
    angle = rect[2]

    if angle < -45:
        angle += 90
        rotated = True

    center = (int((x1 + x2) / 2), int((y1 + y2) / 2))
    size = (int(mult * (x2 - x1)), int(mult * (y2 - y1)))
    cv2.circle(img, center, 5, (0, 255, 255), -1)  # again this was mostly for debugging purposes
    # cv2.drawContours(img, [c], -1, (0, 0, 255), 1)

cv2.imshow('Plate', img)
cv2.imshow('th', detected_lines)
cv2.waitKey(0)
cv2.destroyAllWindows()
