from PIL import Image, ImageFilter
from pynput.mouse import Controller, Button
from PIL import Image, ImageFilter, UnidentifiedImageError 
import time
import sys
import requests
from io import BytesIO
import math

mouse = Controller()

class DrawBot:
    def __init__(self, desiredWidth, desiredHeight, startPosition, ignoreSoloPixels, dither, speed, pixelInterval, url, colors, coordinates):
        self.colorCoordinates = coordinates
        self.colors = colors
        self.speed = self.convertSpeed(speed)
        self.speedByPixel = self.convertSpeedByPixel(speed)
        self.startPosition = startPosition
        self.setUpColorPalettes(colors)
        self.setUpImageToDraw(url, dither, desiredWidth, desiredHeight)
        self.pixelLinesToDraw = self.extractPixelLinesToDraw(pixelInterval, ignoreSoloPixels)
    
    def setUpImageToDraw(self, url, dither, desiredWidth, desiredHeight):
        response = requests.get(url)
        self.img = Image.open(BytesIO(response.content))
        fillColor = (255,255,255)
        self.img = self.img.convert("RGBA")
        if self.img.mode in ('RGBA', 'LA'):
            background = Image.new(self.img.mode[:-1], self.img.size, fillColor)
            background.paste(self.img, self.img.split()[-1])
            self.img = background
        self.img = self.img.convert("RGB").quantize(palette=self.palette, dither=dither)
        maxSize = (desiredWidth, desiredHeight)
        self.img.thumbnail(maxSize, Image.ANTIALIAS)
        self.width, self.height = self.img.size
        self.img = self.img.convert("RGB")

    def setUpColorPalettes(self, colors):
        paletteColors = colors
        for i in range(768-len(colors)):
            paletteColors.append(0)
        self.palette = Image.new("P", (16, 16))
        self.palette.putpalette(paletteColors)
    
    def changeColor(self, r, g, b):
        found = False
        for i in range(0, len(self.colors), 3):
            if r == self.colors[i] and g == self.colors[i+1] and b == self.colors[i+2]:
                mouse.position = self.colorCoordinates[int(i/3)]
                found = True
                break
        if found:
            self.click()

    def extractPixelLinesToDraw(self, pixelInterval, ignoreSoloPixels):
        drawVerticallyLines, nbLinesVertical = self.extractLinesToDraw(True, pixelInterval, ignoreSoloPixels)
        drawHorizontallyLines, nbLinesHorizontal = self.extractLinesToDraw(False, pixelInterval, ignoreSoloPixels)
        if nbLinesHorizontal <= nbLinesVertical:
            return drawHorizontallyLines
        return drawVerticallyLines
    
    def extractLinesToDraw(self, vertically, pixelInterval, ignoreSoloPixels):
        '''Get the lines to draw vertically or horizontally'''
        if not vertically:
            bound1 = self.height
            bound2 = self.width
        else:
            bound1 = self.width
            bound2 = self.height
        lines = {}
        nbLinesToDraw = 0
        for i in range(0, bound1, pixelInterval):
            lineColor = None
            for j in range(0, bound2, pixelInterval):
                if not vertically:
                    r, g, b = self.img.getpixel((j, i))
                else:
                    r, g, b = self.img.getpixel((i, j))
                if not vertically:
                    currentPosition = (j+self.startPosition[0], i+self.startPosition[1])
                else:
                    currentPosition = (i+self.startPosition[0], j+self.startPosition[1])
                if lineColor == None:
                    lineColor = (r, g, b)
                    lineStart = currentPosition
                elif lineColor != (r, g, b):
                    if lineColor not in lines:
                        lines[lineColor] = []
                    if (ignoreSoloPixels and lineStart != lineEnd) or not ignoreSoloPixels:
                        lines[lineColor].append([lineStart, lineEnd])
                    if lineColor != (255,255,255):
                        nbLinesToDraw += 1
                    lineColor = (r, g, b)
                    lineStart = currentPosition
                lineEnd = currentPosition
            if lineColor not in lines:
                lines[lineColor] = []
            if (ignoreSoloPixels and lineStart != lineEnd) or not ignoreSoloPixels:
                lines[lineColor].append([lineStart, lineEnd])
            if lineColor != (255,255,255):
                nbLinesToDraw += 1
            lineColor = None
        return [lines, nbLinesToDraw]
    
    def draw(self, exit_event):
        for key, value in self.pixelLinesToDraw.items():
            if key != (255,255,255) and key != (0,0,0):
                self.changeColor(key[0], key[1], key[2])
                for j in value:
                    if exit_event.is_set():
                        break
                    self.drawLine(j)
            if self.speed == 0.1 or self.speed == 0.00001:
                time.sleep(0.1)
        if (0,0,0) in self.pixelLinesToDraw:
            self.changeColor(0, 0, 0)
            for j in self.pixelLinesToDraw[(0,0,0)]:
                for i in j:
                    if exit_event.is_set():
                        break
                    self.drawLine(j)

    def drawLine(self, coordinates):
        mouse.position = coordinates[0]
        mouse.press(Button.left)
        mouse.move(abs(coordinates[1][0] - coordinates[0][0]), abs(coordinates[1][1] - coordinates[0][1]))
        if (abs(coordinates[1][0] - coordinates[0][0]) > 0 or abs(coordinates[1][1] - coordinates[0][1]) > 0):
            time.sleep(self.speed)
        else:
            time.sleep(self.speedByPixel)
        mouse.release(Button.left)

    def convertSpeed(self, speed):
        if speed == 1:
            return 0.1
        if speed == 2:
            return 0.00001
        if speed == 3:
            return 0.000000001
        if speed == 4:
            return 0.0000000000000001
        
    def convertSpeedByPixel(self, speed):
        if speed == 1:
            return 0.00001
        if speed == 2:
            return 0.000000001
        if speed == 3:
            return 0.0000000000000001
        if speed == 4:
            return 0.0000000000000001

    
    def click(self):
        mouse.press(Button.left)
        mouse.release(Button.left)
