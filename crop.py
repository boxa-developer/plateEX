from utils import *
import numpy as np
import imutils
import cv2
import os


def cleaning(th_image):
    nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(255 - th_image, None, None, None, 8,
                                                                         cv2.CV_32S)

    areas = stats[1:, cv2.CC_STAT_AREA]
    left = stats[1:, cv2.CC_STAT_LEFT]
    top = stats[1:, cv2.CC_STAT_TOP]
    right = left + stats[1:, cv2.CC_STAT_WIDTH]
    down = top + stats[1:, cv2.CC_STAT_HEIGHT]

    result = np.full(labels.shape, 255, np.uint8)
    h, w = result.shape

    for i in range(0, nlabels - 1):
        if areas[i] >= 150 and left[i] > 5 and right[i] < w - 20 and top[i] > 5 and down[i] < h - 11:  # keep
            result[labels == i + 1] = 0
    return result


baseDir = './Plates'
scanObj = os.scandir(baseDir)
imageCount = 2000
images = [cv2.imread(f'{baseDir}/{item.name}') for item in scanObj]


# img = cv2.imread('plates/p1.jpg')

# for img in images:
def crop_img(img):
    X, Y, H = [], [], []  # Declaring Char Lists

    img = cv2.resize(img, (400, 100))
    # Remove Shadows
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (75, 75), 0)
    division = cv2.divide(gray, blur, scale=200)
    thresh = cv2.threshold(division, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))

    detected_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=1)
    cnts = cv2.findContours(detected_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        cv2.drawContours(division, [c], -1, (120, 120, 120), -1)
    repair_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 3))
    result = 255 - cv2.morphologyEx(255 - division, cv2.MORPH_CLOSE, repair_kernel, iterations=1)

    # _, result_th = cv2.threshold(result, 180, 255, cv2.THRESH_BINARY_INV)
    # cv2.imshow('division', division)
    # Apply Filters
    # blur = cv2.medianBlur(division, 7)
    ret, thresh = cv2.threshold(division, 170, 255, cv2.THRESH_BINARY)
    x_thresh = cleaning(thresh)
    edges = cv2.Canny(x_thresh, 0, 100, 3)
    cv2.imshow('edges', x_thresh)
    # Grab Contours
    contours = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sort_contours(imutils.grab_contours(contours))[0]

    for k, contour in enumerate(contours):
        (x, y, w, h) = cv2.boundingRect(contour)
        # Character Filters
        shape_filter = True if (10 < w < 60 and 20 < h < 70) else False

        if shape_filter and w < 1.3 * h:
            X.append(centroid(x, y, w, h)[0])
            # cv2.circle(division, centroid(x, y, w, h), 4, (0,0,0), -1)
            Y.append(centroid(x, y, w, h)[1])
            H.append(h)

    # Approximation
    best_fit_line = np.poly1d(np.polyfit(Y, X, 1))(Y)

    # Angle between best_fit_line and X axis
    angle = np.arctan(best_fit_line[-1] - best_fit_line[0] / len(best_fit_line))
    # The mean is the average of the numbers
    mean = np.median(Y, axis=0)

    # Rotate the image
    rt = rotate_image(x_thresh, (-1) * (angle + 1))

    # Apply Perspective Transform
    APPROX_HEIGHT = (np.max(H) + np.min(H) + np.average(H)) // 3
    pts1 = np.float32([[0, mean + APPROX_HEIGHT],
                       [0, mean - APPROX_HEIGHT],
                       [400, mean - APPROX_HEIGHT],
                       [400, mean + APPROX_HEIGHT]])
    pts2 = np.float32([[0, 60], [0, 0], [400, 0], [400, 60]])
    M = cv2.getPerspectiveTransform(pts1, pts2)

    dst = cv2.warpPerspective(gray, M, (400, 60))
    cv2.imshow('dst_', dst)
    _, thresh2 = cv2.threshold(dst, 120, 255, cv2.THRESH_BINARY)
    kernel = np.ones((3, 3), np.uint8)
    result = cv2.erode(thresh2, kernel, iterations=1)

    # return result
    # cv2.imshow('Img2', thresh2)
    return result
