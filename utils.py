from pynput.mouse import Controller, Button, Listener
from pynput import keyboard
from queue import Queue
import os

mouse = Controller()
queue = Queue()
clicked = 0
start = 0

def getPalette(app):
    if app == 0:
        app = "gartic"
    elif app == 1:
        app = "skribbl"
    else:
        app = "paint"
    coordinatesFile = os.path.dirname(os.path.abspath(__file__)) + "\\colorPalettes\\" + app + "Coordinates.txt"
    colorFiles = os.path.dirname(os.path.abspath(__file__)) + "\\colorPalettes\\" + app + "Colors.txt"
    coordinates = [tuple(int(i) for i in t.strip('()').split(',')) for t in open(coordinatesFile).read().split()]
    colors = [int(t) for t in open(colorFiles).read().split()]
    return [colors, coordinates]


def getMouseCoordinatesOnce(x, y, button, pressed):
    if not pressed:
        return False
    queue.put((x,y))

def getMouseCoordinatesTwice(x, y, button, pressed):
    global clicked
    global start
    if pressed and button == Button.left:
        clicked += 1
        if clicked == 1 :
            start = (x,y)
        elif clicked == 2:
            clicked = 0
            queue.put([start, (x,y)])
            return False


def getNextMouseClickPositionCoordinates():
    listener = Listener(on_click=getMouseCoordinatesOnce)
    listener.start()
    return queue.get()

def getBounds():
    listener = Listener(on_click=getMouseCoordinatesTwice)
    listener.start()
    return queue.get()
        