from utils import *
import numpy as np
import imutils
import cv2
import os

scanObj = os.scandir('./Plates')
imageCount = 2000
images = []

for i, item in enumerate(scanObj):
    if i < imageCount:
        X, Y, H = [], [], []  # Declaring Char Lists

        # Load images
        images.append(cv2.imread(f'Plates/{item.name}'))
        img = images[i]
        img = cv2.resize(img, (400, 100))

        # Remove Shadows
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (95, 95), 0)
        division = cv2.divide(gray, blur, scale=190)

        # Apply Filters
        blur = cv2.medianBlur(division, 9)
        sh = unsharp_mask(blur)
        ret, thresh = cv2.threshold(sh, 150, 255, cv2.THRESH_BINARY)
        edges = cv2.Canny(thresh, 50, 200)

        # Grab Contours
        contours = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = sort_contours(imutils.grab_contours(contours))[0]

        for k, contour in enumerate(contours):
            (x, y, w, h) = cv2.boundingRect(contour)
            # Character Filters
            shape_filter = True if (10 < w < 60 and 20 < h < 70) else False
            area_filter = True if (120 < cv2.contourArea(contour) < 900) else False
            density_filter = True if (w * h - cv2.countNonZero(thresh[y:y + h, x:x + w]) > 40) else False

            if shape_filter and w < 1.3 * h:
                X.append(centroid(x, y, w, h)[0])
                Y.append(centroid(x, y, w, h)[1])
                H.append(h)

        # Approximation
        best_fit_line = np.poly1d(np.polyfit(Y, X, 1))(Y)

        # Angle between best_fit_line and X axis
        angle = np.arctan(best_fit_line[-1] - best_fit_line[0] / len(best_fit_line))
        # The mean is the average of the numbers
        mean = np.median(Y, axis=0)

        # Rotate the image
        rt = rotate_image(division, (-1) * (angle + 1))

        # Apply Perspective Transform
        pts1 = np.float32([[0, mean + np.average(H) // 2 + 10],
                           [0, mean - np.average(H) // 2 - 15],
                           [400, mean - np.average(H) // 2 - 15],
                           [400, mean + np.average(H) // 2 + 10]])
        pts2 = np.float32([[0, 50], [0, 0], [400, 0], [400, 50]])
        M = cv2.getPerspectiveTransform(pts1, pts2)
        dst = cv2.warpPerspective(rt, M, (400, 50))

        # Cropping the plate
        new_dst = dst[0:dst.shape[0], 40:dst.shape[1] - 40]
        cv2.imshow("new_dst", new_dst)
        cv2.waitKey(0)

        # dst = cv2.copyMakeBorder(dst, 10, 10, 0, 0, cv2.BORDER_CONSTANT, value=(255, 255, 255))
        # _, thresh = cv2.threshold(dst, 50, 255, cv2.THRESH_BINARY)
        # cv2.imshow('iw', thresh)
