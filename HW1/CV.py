import cv2
import numpy as np
from math import inf
orig_image = cv2.imread('items2.jpg')

image = cv2.imread('items2.jpg', 0)  
adaptive_thresh_gaussian = cv2.adaptiveThreshold(image, 255, 
cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 2)

contours, hierarchy = cv2.findContours(adaptive_thresh_gaussian, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)


objects_contours = []
min_obj = []
min_area = inf
min_coords = []

max_obj = []
max_area = 0
max_coords = []

for contour in contours:    
    area = cv2.contourArea(contour)
    if(area > 1000):   
        objects_contours.append(contour)
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])  # X-координата центра масс
            cY = int(M["m01"] / M["m00"])  # Y-координата центра масс
            cv2.circle(orig_image, (cX, cY), 5, (255, 0, 0), -1)  # Рисуем кружок вокруг центр
        if (area < min_area):
            min_obj = contour
            min_area = area
            min_coords = cX, cY
        if (area > max_area):
            max_obj = contour
            max_area = area
            max_coords = cX, cY
        cv2.drawContours(orig_image, contour, -1, (0, 0, 255), 3)


font                   = cv2.FONT_HERSHEY_SIMPLEX

fontScale              = 1
fontColor              = (0,0,0)
thickness              = 2
lineType               = 2

cv2.putText(orig_image,f"num of objects: {len(objects_contours)}", 
    (10,500), 
    font, 
    fontScale,
    fontColor,
    thickness,
    lineType)

cv2.putText(orig_image,f"biggest obj coords:(yellow) {max_coords}", 
    (10,550), 
    font, 
    fontScale,
    (0, 255, 0),
    thickness,
    lineType)

cv2.putText(orig_image,f"smallest obj coords:(green) {min_coords} ",
    (10,600), 
    font, 
    fontScale,
    (0, 255, 255),
    thickness,
    lineType)

print(f"Количество обьектов: {len(objects_contours)}")
print(f"координаты центра самого большого объекта(green): {max_coords}")
cv2.circle(orig_image, (max_coords), 5, (0, 255, 0), -1)

print(f"координаты центра самого маленького объекта(yellow): {min_coords}")
cv2.circle(orig_image, (min_coords), 5, (0, 255, 255), -1)

cv2.imshow('Adaptive Thresholded Image (Gaussian)', adaptive_thresh_gaussian)
cv2.imshow('orig_image with Contours', orig_image)
cv2.waitKey(0)
cv2.destroyAllWindows()