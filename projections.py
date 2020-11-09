import numpy as np
import logging
import cv2
import os

scanObj = os.scandir('Plates')
imageCount = 50
images = []
for i, item in enumerate(scanObj):
    if i < imageCount:
        images.append(cv2.imread(f'Plates/{item.name}'))

        img = images[i]
        img = cv2.resize(img, (400, 100))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (95, 95), 0)
        division = cv2.divide(gray, blur, scale=190)
        ret, thresh = cv2.threshold(division, 230, 255, cv2.THRESH_BINARY_INV)
        dilate = cv2.morphologyEx(thresh, cv2.MORPH_ELLIPSE, np.ones((3, 3), np.uint8))
        erode = cv2.morphologyEx(thresh, cv2.MORPH_ERODE, np.ones((7, 7), np.uint8))
        edge = cv2.Canny(erode, 100, 200, apertureSize=3)
        cv2.imshow('ege', edge)
        contours, hierarchy = cv2.findContours(edge, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        hull_list = []
        for i in range(len(contours)):
            hull = cv2.convexHull(contours[i])
            hull_list.append(hull)
        areas = [cv2.contourArea(c) for c in hull_list]
        max_index = np.argmax(areas)
        rect = cv2.minAreaRect(contours[max_index])
        box = np.int0(cv2.boxPoints(rect))
        pts2 = np.float32([[0, 50], [0, 0], [200, 0], [200, 50]])
        M = cv2.getPerspectiveTransform(cv2.boxPoints(rect), pts2)
        dst = cv2.warpPerspective(division, M, (200, 50))

        cv2.imshow('win', dst)
        cv2.waitKey(0)
cv2.destroyAllWindows()
