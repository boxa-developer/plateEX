from scipy.spatial import distance
from crop import crop_img
import numpy as np
import pytesseract
import imutils
import cv2, os

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


scanObj = os.scandir('Plates')
images = [cv2.imread(os.path.join('Plates', item.name)) for item in scanObj]
# img = cv2.imread('Plates/100_6733.jpg')
for img in images:
    dst = crop_img(img)
    cv2.imshow('crop', dst)
    cv2.imshow('orig', img)

    H, W = dst.shape[:2]
    contours = cv2.findContours(dst, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sort_contours(imutils.grab_contours(contours))[0]
    black_frame = np.zeros_like(dst)
    counter = 0
    rects = []
    old_x = None

    mask = np.zeros(shape=dst.shape, dtype=np.uint8)
    for i, contour in enumerate(contours):
        (x, y, w, h) = cv2.boundingRect(contour)
        shape_filter = True if (80 > w > 10 and h > 20) else False
        area_filter = True if (100 < cv2.contourArea(contour)) else False
        density_filter = True if (w * h - cv2.countNonZero(dst[y:y + h, x:x + w]) > 100) else False
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

    cv2.imshow('fg', fg_masked)

    # kernel = np.ones((4, 4), np.uint8)
    # masked = cv2.erode(masked, kernel, iterations=1)
    number = pytesseract.image_to_string(masked, lang="eng", config=tesseract_options)
    print(number)
    cv2.imshow(f"NUMBER: {number}", masked)

    cv2.waitKey(0)
cv2.destroyAllWindows()
