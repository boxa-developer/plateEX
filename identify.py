import cv2
import numpy as np
import imutils
from scipy.spatial import distance
import pytesseract

# Tesseract options, PSM=6 (horizontal text),
psm = 6
# Alphanumerical
tesseract_options = "-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 --psm {}".format(psm)


def sort_contours(cnts, method="left-to-right"):
    reverse = False
    i = 0
    if method == "right-to-left" or method == "bottom-to-top":
        reverse = True
    if method == "top-to-bottom" or method == "bottom-to-top":
        i = 1
    boundingBoxes = [cv2.boundingRect(c) for c in cnts]
    (cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes),
                                        key=lambda b: b[1][i], reverse=reverse))
    # return the list of sorted contours and bounding boxes
    return cnts, boundingBoxes


def dist(x1, y1, x2, y2):
    return round(distance.euclidean((x1, y1), (x2, y2)), 1)


def centroid(_x, _y, _w, _h):
    return _x + _w // 2, _y + _h // 2


def inside_box(cx, cy, rect):
    (_x1, _y1, _x2, _y2) = rect
    if _x1 < cx < _x2 and _y1 < cy < _y2:
        return True
    else:
        return False


img = cv2.imread('out.jpg')

img = cv2.copyMakeBorder(img, 5, 5, 5, 5, cv2.BORDER_CONSTANT, value=(0, 0, 0))

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray, (95, 95), 0)
division = cv2.divide(gray, blur, scale=200)

ret, thresh = cv2.threshold(division, 100, 255, cv2.THRESH_BINARY)
dilate = cv2.dilate(thresh, np.ones((3, 3), np.uint8))
erode = cv2.erode(dilate, np.ones((4, 4), np.uint8))
edge = cv2.Canny(erode, 50, 200, apertureSize=3)

contours, hierarchy = cv2.findContours(edge, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
hull_list = []
for i in range(len(contours)):
    hull = cv2.convexHull(contours[i])
    hull_list.append(hull)
areas = [cv2.contourArea(c) for c in hull_list]
max_index = np.argmax(areas)
rect = cv2.minAreaRect(contours[max_index])
# print(contours[max_index])
box = np.int0(cv2.boxPoints(rect))
pts2 = np.float32([[0, 50], [0, 0], [200, 0], [200, 50]])
M = cv2.getPerspectiveTransform(cv2.boxPoints(rect), pts2)
dst = cv2.warpPerspective(division, M, (200, 50))

dst = cv2.copyMakeBorder(dst, 10,10, 10,10, cv2.BORDER_CONSTANT, value=(255, 255, 255))

H, W = dst.shape[:2]
_, th = cv2.threshold(dst, 100, 255, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
contours = cv2.findContours(th, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
contours = sort_contours(imutils.grab_contours(contours))[0]
black_frame = np.zeros_like(dst)
counter = 0
rects = []
old_x = None

mask = np.zeros(shape=dst.shape, dtype=np.uint8)
for i, contour in enumerate(contours):
    (x, y, w, h) = cv2.boundingRect(contour)
    shape_filter = True if (10 < w < 100 and h > 20) else False
    area_filter = True if (120 < cv2.contourArea(contour) < 900) else False
    density_filter = True if (w * h - cv2.countNonZero(th[y:y + h, x:x + w]) > 40) else False
    cX, cY = centroid(x, y, w, h)
    if shape_filter and area_filter and density_filter:
        counter += 1
        if w / h > 0.9:
            n = int(w / h / 0.6)
            for num in range(1, n + 1):
                print(num)
                cv2.rectangle(mask, (x + w // n * (num - 1), y), (x + w // n * num, y + h), (255, 255, 255), -1)
                counter += 1
        else:
            if counter == 1:
                old_x = x + w
                cv2.rectangle(mask, (x, y), (x + w, y + h), (255, 255, 255), -1)
            else:
                old_x = x + w
                cv2.rectangle(mask, (x, y), (x + w, y + h), (255, 255, 255), -1)

fg_masked = cv2.bitwise_and(dst, mask)
bg_masked = cv2.bitwise_and(np.full(dst.shape, 255, dtype=np.uint8), cv2.bitwise_not(mask))
masked = cv2.bitwise_or(bg_masked, fg_masked)

cv2.imwrite("test/original.jpg", img)
cv2.imwrite("test/corrected.jpg", dst)
cv2.imwrite("test/masked.jpg", masked)

number = pytesseract.image_to_string(masked, lang="eng", config=tesseract_options)
print(number)

# cv2.imshow('Original', img)
# cv2.imshow('Corrected', dst)
# cv2.imshow("Masked", masked)

# cv2.waitKey(0)
# cv2.destroyAllWindows()
