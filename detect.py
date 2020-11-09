import numpy as np
import imutils
import cv2
import os
import matplotlib.pyplot as plt


def unsharp_mask(image, kernel_size=(5, 5), sigma=1.5, amount=2.0, threshold=0):
    blurred = cv2.GaussianBlur(image, kernel_size, sigma)
    sharpened = float(amount + 1) * image - float(amount) * blurred
    sharpened = np.maximum(sharpened, np.zeros(sharpened.shape))
    sharpened = np.minimum(sharpened, 255 * np.ones(sharpened.shape))
    sharpened = sharpened.round().astype(np.uint8)
    if threshold > 0:
        low_contrast_mask = np.absolute(image - blurred) < threshold
        np.copyto(sharpened, image, where=low_contrast_mask)
    return sharpened


def rotate_image(image, angle):
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
    return result


def centroid(_x, _y, _w, _h):
    return _x + _w // 2, _y + _h // 2


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


scanObj = os.scandir('Plates')
imageCount = 2000
images = []

for i, item in enumerate(scanObj):
    if i < imageCount:
        X, Y, H = [], [], []
        images.append(cv2.imread(f'Plates/{item.name}'))
        img = images[i]
        img = cv2.resize(img, (400, 100))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (95, 95), 0)
        division = cv2.divide(gray, blur, scale=190)
        blur = cv2.medianBlur(division, 9)
        sh = unsharp_mask(blur)
        ret, thresh = cv2.threshold(sh, 150, 255, cv2.THRESH_BINARY)
        edges = cv2.Canny(thresh, 50, 200)
        contours = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = sort_contours(imutils.grab_contours(contours))[0]
        for k, contour in enumerate(contours):
            (x, y, w, h) = cv2.boundingRect(contour)
            shape_filter = True if (10 < w < 60 and 20 < h < 70) else False
            area_filter = True if (120 < cv2.contourArea(contour) < 900) else False
            density_filter = True if (w * h - cv2.countNonZero(thresh[y:y + h, x:x + w]) > 40) else False
            if shape_filter and w < 1.3 * h:
                X.append(centroid(x, y, w, h)[0])
                Y.append(centroid(x, y, w, h)[1])
                H.append(h)
        best_fit_line = np.poly1d(np.polyfit(Y, X, 1))(Y)
        angle = np.arctan(best_fit_line[-1] - best_fit_line[0] / len(best_fit_line))
        mean = np.median(Y, axis=0)
        rt = rotate_image(division, (-1) * (angle + 1))
        pts1 = np.float32([[0, mean + np.average(H) // 2 + 10],
                           [0, mean - np.average(H) // 2 - 15],
                           [400, mean - np.average(H) // 2 - 15],
                           [400, mean + np.average(H) // 2 + 10]])
        pts2 = np.float32([[0, 50], [0, 0], [400, 0], [400, 50]])
        M = cv2.getPerspectiveTransform(pts1, pts2)
        dst = cv2.warpPerspective(rt, M, (400, 50))
        # dst = cv2.copyMakeBorder(dst, 10, 10, 0, 0, cv2.BORDER_CONSTANT, value=(255, 255, 255))
        cv2.rectangle(dst, (0, 0), (dst.shape[:2][::-1]), (0,0,0), 10)
        _, thresh = cv2.threshold(dst, 170, 255, cv2.THRESH_BINARY)
        cv2.imshow('iw', thresh)
        cv2.waitKey(0)
