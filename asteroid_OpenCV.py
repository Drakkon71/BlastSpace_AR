from __future__ import division
# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Face Recognizer App
#
__author__ = "Oscar Castell"
__copyright__ = "Copyright 2017, Research Work"
__credits__ = ["Oscar Castell"]
__license__ = "GPL"
__version__ = "v3.0"
__maintainer__ = "Oscar Castell"
__email__ = "ocastell@xtec.cat"
__status__ = "Production"
#
# Libreries
#
import cv2
import numpy as np
import imutils
import collections
import random
import math

class Target:
    """ Class representing the target """

    def __init__(self, x, y, angle, delta_angle, dimx, dimy):
        self.x = x
        self.y = y
        self.r = 0
        self.dimx = dimx
        self.dimy = dimy
        self.width = 0
        self.height = 0
        self.centerX = 0
        self.centerY = 0
        self.speed = random.uniform(5, 15)
        self.angle = angle
        self.delta_angle = delta_angle
        self.alpha_speed = random.uniform(0, 2 * math.pi)
        self.active = True

    def getDimensions(self):
        return (self.x, self.y, self.angle, self.width, self.height, self.r)

    def getVelocity(self):
        return (self.alpha_speed)

    def getDistance(self):
        self.r = math.sqrt((self.centerX) ** 2 + (self.centerY) ** 2)
        return (self.r)

    def centerOrigin(self):
        self.centerX = int(self.x + int(self.width / 2))
        self.centerY = int(self.y + int(self.height / 2))
        return (self.centerX, self.centerY)

    def update(self):
        #
        # Translate
        #
        delta_x = int(self.speed * math.cos(self.alpha_speed))
        delta_y = int(self.speed * math.sin(self.alpha_speed))
        self.x = self.x + delta_x
        self.y = self.y - delta_y
        self.centerX, self.centerY = self.centerOrigin()
        self.r = self.getDistance()
        if self.y <= 0:
            if self.alpha_speed > 0 and self.alpha_speed < math.pi / 2:
                self.alpha_speed = - self.alpha_speed + 2 * math.pi
            if self.alpha_speed < math.pi and self.alpha_speed > math.pi / 2:
                self.alpha_speed = - self.alpha_speed + 2 * math.pi
        if self.y >= self.dimy - self.height:
            if self.alpha_speed > math.pi and self.alpha_speed < 3 * math.pi / 2:
                self.alpha_speed = - self.alpha_speed + 2 * math.pi
            if self.alpha_speed < 2 * math.pi and self.alpha_speed > 3 * math.pi / 2:
                self.alpha_speed = - self.alpha_speed + 2 * math.pi
        if self.x <= 0:
            if self.alpha_speed > math.pi and self.alpha_speed < 3 * math.pi / 2:
                self.alpha_speed = - self.alpha_speed + math.pi
            if self.alpha_speed < math.pi and self.alpha_speed > math.pi / 2:
                self.alpha_speed = - self.alpha_speed + math.pi
        if self.x >= self.dimx - self.width:
            if self.alpha_speed > 0 and self.alpha_speed < math.pi / 2:
                self.alpha_speed = - self.alpha_speed + 3 * math.pi
            if self.alpha_speed < 2 * math.pi and self.alpha_speed > 3 * math.pi / 2:
                self.alpha_speed = - self.alpha_speed + math.pi
        if self.alpha_speed < 0:
            self.alpha_speed = 2 * math.pi + self.alpha_speed
        if self.alpha_speed > 2 * math.pi:
            self.alpha_speed = - 2 * math.pi + self.alpha_speed
        #
        # rotate
        #
        self.angle = self.angle + self.delta_angle
        if self.angle == 360:
            self.angle = 0


#
# End of Class Target
#
def overlay_image_alpha(img, img_overlay, pos, angle, alpha_mask, item):
    """Overlay img_overlay on top of img at the position specified by
    pos and blend using alpha_mask.
    Rotate image angle
    Alpha mask must contain values within the range [0, 1] and be the
    same size as img_overlay.
    """

    x, y = pos
    img_rotate = img_overlay

    # Image ranges
    y1, y2 = max(0, y), min(img.shape[0], y + img_overlay.shape[0])
    x1, x2 = max(0, x), min(img.shape[1], x + img_overlay.shape[1])

    # Overlay ranges
    y1o, y2o = max(0, -y), min(img_overlay.shape[0], img.shape[0] - y)
    x1o, x2o = max(0, -x), min(img_overlay.shape[1], img.shape[1] - x)

    # Exit if nothing to do
    if y1 >= y2 or x1 >= x2 or y1o >= y2o or x1o >= x2o:
        return

    channels = img.shape[2]

    alpha = alpha_mask[y1o:y2o, x1o:x2o]
    alpha_inv = 1.0 - alpha

    img_overlay = imutils.rotate(img_rotate, angle)
    for c in range(channels):
        img[y1:y2, x1:x2, c] = (alpha * img_overlay[y1o:y2o, x1o:x2o, c] +
                                alpha_inv * img[y1:y2, x1:x2, c])
    cv2.circle(img, (item.centerX, item.centerY), 5, (0, 255, 0), -1)


def create_blank_image(width, height, rgb_color=(0, 0, 0)):
    """Create new image(numpy array) filled with certain color in RGB"""
    # Create black blank image
    image = np.zeros((height, width, 3), np.uint8)
    # Since OpenCV uses BGR, convert the color first
    color = tuple(reversed(rgb_color))
    # Fill image with color
    image[:] = color
    return image


def create_targets(dimx, dimy, angle, delta_angle, image, count):
    targets = list()
    for i in range(count):
        height, width = image.shape[:2]
        x = random.randint(0, dimx - width)
        y = random.randint(0, dimy - height)
        tgt = Target(x, y, angle, delta_angle, dimx, dimy)
        tgt.height, tgt.width = image.shape[:2]
        targets.append(tgt)
    return targets


def collisions(targets_list, w, h):
    #
    # collisions between asteroids
    #
    list1 = list(targets_list)
    list2 = list(targets_list)
    del list1[len(targets_list) - 1]
    del list2[0]
    for item1 in list1:
        for item2 in list2:
            distance = int(math.sqrt((item1.centerX - item2.centerX) ** 2 + (item1.centerY - item2.centerY) ** 2))
            if distance <= w or distance <= h:
                # print "collision!!"
                alpha_speed_intercanvi = item1.alpha_speed
                item1.alpha_speed = item2.alpha_speed
                item2.alpha_speed = alpha_speed_intercanvi
                speed_intercanvi = item1.speed
                item1.speed = item2.speed
                item2.speed = speed_intercanvi
        if len(list2) > 0:
            del list2[0]


#
# Iniciar variables
#

image_ovni = "ovni.png"
ovni = cv2.imread(image_ovni, -1)
image_asteroid = "asteroid_blend.png"
asteroid = cv2.imread(image_asteroid, -1)
camera = cv2.VideoCapture(0)
valid, frame = camera.read()
if valid:
    dimy, dimx = frame.shape[:2]
    num_ovnis = 0
    angle = 0
    delta_angle = 0
    list_ovnis = create_targets(dimx, dimy, angle, delta_angle, ovni, num_ovnis)
    num_asteroids = 10
    angle = 0
    delta_angle = 15
    list_asteroids = create_targets(dimx, dimy, angle, delta_angle, asteroid, num_asteroids)
else:
    exit()

# Iniciar camara

camera = cv2.VideoCapture(0)
while (1):
    valid, frame = camera.read()
    if valid:
        frame = imutils.resize(frame, width=640)
        for ovni_item in list_ovnis:
            if ovni_item.active:
                x, y, angle, width, height, r = ovni_item.getDimensions()
                overlay_image_alpha(frame, ovni[:, :, 0:3], (x, y), angle, ovni[:, :, 3] / 255.0, ovni_item)
                ovni_item.update()
        for asteroid_item in list_asteroids:
            if asteroid_item.active:
                x, y, angle, width, height, r = asteroid_item.getDimensions()
                overlay_image_alpha(frame, asteroid[:, :, 0:3], (x, y), angle, asteroid[:, :, 3] / 255.0, asteroid_item)
                asteroid_item.update()
        collisions(list_asteroids, width, height)
        cv2.imshow('Camara', frame)
        tecla = cv2.waitKey(5) & 0xFF
        if tecla == 27 or tecla == ord("q"):
            break
camera.release()
cv2.destroyAllWindows()
