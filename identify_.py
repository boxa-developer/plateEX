import imutils
import pytesseract
from scipy.spatial import distance
from crop import crop_img
import numpy as np
import cv2


class Extractor(object):
    def __init__(self):
        psm = 6
        self.tesseract_options = "-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 --psm {}".format(psm)

    def character_filter(self, img):
        dst = crop_img(img)
        cv2.imshow('crop', dst)
        cv2.imshow('orig', img)

        H, W = dst.shape[:2]
        contours = cv2.findContours(dst, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = self.sort_contours(imutils.grab_contours(contours))[0]
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
            cX, cY = self.centroid(x, y, w, h)

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

        number = pytesseract.image_to_string(masked, lang="eng", config=self.tesseract_options)
        print(number)
        cv2.imshow(f"NUMBER: {number}", masked)
        cv2.waitKey(0)

    @staticmethod
    def sort_contours(cnts, method="left-to-right"):
        reverse = False
        key = 0
        if method == "right-to-left" or method == "bottom-to-top":
            reverse = True
        if method == "top-to-bottom" or method == "bottom-to-top":
            key = 1
        boundingBoxes = [cv2.boundingRect(c) for c in cnts]
        (cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes),
                                            key=lambda b: b[1][key], reverse=reverse))
        return cnts, boundingBoxes

    @staticmethod
    def inside_box(cx, cy, rect):
        (x1, y1, x2, y2) = rect
        is_inside = x1 < cx < x2 and y1 < cy < y2
        return True if is_inside else False

    @staticmethod
    def dist(x1, y1, x2, y2):
        return round(distance.euclidean((x1, y1), (x2, y2)), 1)

    @staticmethod
    def centroid(x, y, w, h):
        return x + w // 2, y + h // 2


if __name__ == '__main__':
    import os

    path = "Plates"
    scanObj = os.scandir(path)
    images = [cv2.imread(os.path.join(path, item.name)) for item in scanObj]
    ex_machine = Extractor()

    for image in images:
        ex_machine.character_filter(image)
