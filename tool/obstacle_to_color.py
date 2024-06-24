import cv2
import numpy as np

img = cv2.imread('image.png')

lower_obstacle = np.array([0, 0, 0])  # 黑色的下限
upper_obstacle = np.array([50, 50, 50])  # 黑色的上限

# find place of obstacles
mask = cv2.inRange(img, lower_obstacle, upper_obstacle)

# reset obstacle regions to red 
img[mask == 0] = [0, 0, 255] # red

cv2.imwrite('qq_modified.png', img)
