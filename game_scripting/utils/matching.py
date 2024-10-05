import cv2
import numpy as np
import time
import matplotlib.pyplot as plt
import game_scripting

app_name = "炉石传说"
# app_name = "BlueStacks"
gw = game_scripting.GameWindow(app_name)
current_screen = gw.get_current_screenshot(to_cv=False)
current_screen.save("screenshot.jpg")
img_rgb = cv2.imread('screenshot.jpg')
template = cv2.imread('hearthstone/assets/treasure_bottom.jpg')
img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
# img_gray = img_rgb
# template = cv2.imread('hearthstone/assets/guardian.jpg')
to_gray_scale = False
if to_gray_scale:
    img = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    w, h = template.shape
else:
    img = img_rgb
    w, h = template.shape[:-1]

res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
threshold = .8
loc = np.where(res >= threshold)
for pt in zip(*loc[::-1]):  # Switch collumns and rows
    cv2.rectangle(img_rgb, pt, (pt[0] + h, pt[1] + w), (0, 0, 255), 2)
    cv2.rectangle(img_gray, pt, (pt[0] + h, pt[1] + w), (0, 0, 255), 2)

cv2.imwrite('result.jpg', img_rgb)
cv2.imwrite('result_gray.jpg', img_gray)