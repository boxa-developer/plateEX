import cv2
import numpy as np
from cv2 import dnn_superres

# Create an SR object
sr = dnn_superres.DnnSuperResImpl_create()

# Read the desired model
path = "upscaling/ESPCN_x4.pb"
sr.readModel(path)

# Set the desired model and scale to get correct pre- and post-processing
sr.setModel("espcn", 4)

img = cv2.imread('Plates/102_592590.jpg')

img = sr.upsample(img)
cv2.imwrite("test/upsampled.jpg", img)

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

thresh = 120
ret,thresh_img = cv2.threshold(gray, thresh, 255, cv2.THRESH_BINARY)
thresh_img = cv2.copyMakeBorder(thresh_img, 5, 5, 5, 5, cv2.BORDER_CONSTANT, value=255)
cv2.imwrite("test/thresh.jpg", thresh_img)


blur = cv2.GaussianBlur(thresh_img, (7, 7), 0.5)
edge = cv2.Canny(blur, 0, 50, 3)

cv2.imwrite("test/edge.jpg", edge)

h, w = edge.shape[:2]

cnts = cv2.findContours(edge, cv2.RETR_LIST,  
                    cv2.CHAIN_APPROX_SIMPLE)[-2] 

# mask = np.full(edge.shape, 0, dtype=np.uint8)

# for cnt in cnts:
#     approx = cv2.approxPolyDP(cnt,  
#                                 0.009 * cv2.arcLength(cnt, True), True)
#     # print(approx)
#     xmin = np.min(approx[:, :, 0])
#     xmax = np.max(approx[:, :, 0])

#     ymin = np.min(approx[:, :, 1])
#     ymax = np.max(approx[:, :, 1])

#     # cv2.drawContours(clean_img, [approx], -1, 0, 3)

#     # print(xmin, xmax, ymin, ymax)
#     if not (xmin<=5 or xmax>=w-11 or ymin<=5 or ymax>=h-11):
#         cv2.fillPoly(mask, [approx], 255)


# fg_masked = cv2.bitwise_and(thresh_img, mask)
# bg_masked = cv2.bitwise_and(np.full(thresh_img.shape, 255, dtype=np.uint8), cv2.bitwise_not(mask))
# masked = cv2.bitwise_or(bg_masked, fg_masked)

# do connected components processing
nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(255-thresh_img, None, None, None, 8, cv2.CV_32S)

#get CC_STAT_AREA component as stats[label, COLUMN] 
areas = stats[1:,cv2.CC_STAT_AREA]
left = stats[1:, cv2.CC_STAT_LEFT]
top = stats[1:, cv2.CC_STAT_TOP]
right = left + stats[1:, cv2.CC_STAT_WIDTH]
down = top + stats[1:, cv2.CC_STAT_HEIGHT]


result = np.full((labels.shape), 255, np.uint8)
h, w = result.shape

for i in range(0, nlabels - 1):
    if areas[i] >= 150 and left[i]>5 and right[i]<w-11 and top[i]>5 and down[i]<h-11:   #keep
        result[labels == i + 1] = 0

cv2.imwrite("test/clean.jpg", result)
