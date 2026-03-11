
###
# The following code you are about to bear witness to is so unreadable, that when I wrote it, only God and I could understand what it meant.
# Now, only God can.
###

from math import *
from panda3d.core import *
import sys
import os
import time
import csv

confVars= """
win-size 1280 720
window-title Planetarium
show-frame-rate-meter True
"""

loadPrcFileData("",confVars)

from direct.showbase.ShowBase import *
from direct.interval.IntervalGlobal import *
from direct.gui.OnscreenText import *
from direct.filter.CommonFilters import CommonFilters
from direct.gui.OnscreenImage import *

def degToRad(degrees):
    return degrees * (pi / 180.0)

def createText(object, disp):
    textObject = OnscreenText(text=disp, pos=(-0.5, 0.5), scale=0.2)
    textObject.fg=(1,1,1,1)
    textObject.reparentTo(object)
    return textObject

class Planetarium(ShowBase):
    
    def __init__(self): ### MAIN INIT MAIN INIT MAIN INIT MAIN INIT MAIN INIT MAIN INIT MAIN INIT MAIN INIT MAIN INIT MAIN INIT MAIN INIT MAIN INIT MAIN INIT MAIN INIT MAIN INIT MAIN INIT ###
               
        ShowBase.__init__(self)
        self.disableMouse() # Awful name but disables default camera
        lens = base.camLens
        # lens.setNearFar(0.1,9*10^7) # Clip planes (Shit doesn't work fix later if needed)
        base.setBackgroundColor(0,0,0) # Bg colour
        
        self.root = render.attachNewNode('root') # The entire game's root location

        self.setupControls()
        self.captureMouse()

        self.running = 1 # Running is true (Note to future self, this variable is governed by everything instead of everything being governed by this variable FOR SOME REASON)
        
        self.createUI() # Create UI

        filters = CommonFilters(base.win, base.cam)
        filters.setBloom()

        taskMgr.add(self.camUpdate, 'camUpdate')
        taskMgr.add(self.selectorUpdate, 'selectorUpdate')

        self.createSun()
        
        self.root.setScale(1)

        self.selectedObject = '' # SELECTED OBJECT VARIABLE

    def createSun(self): # This creates the Sun, why is this special enough for it's own function? WHO KNOWS!
        self.sun = loader.loadModel("models/sphere")
        self.sun.setScale(1,1,1)
        self.sun.setPos(0, 0, 0)
        self.sun.setName("Sun")
        # Board stuff
        
        self.board = loader.loadModel("models/board")
        self.board.setScale(5,5,5)
        self.board.setPos(0, 0, 0)
        self.board.setName("SunFlair")
        self.board.setBillboardPointWorld()

        # Texture Board
        
        self.sun_tex = loader.loadTexture("textures/star.png")
        self.board.setTexture(self.sun_tex, 0)
        self.board.setTransparency(TransparencyAttrib.MAlpha)
        self.board.reparentTo(self.sun)
        
        sunNode = self.root.attachNewNode('Sun')
        sunSolid = CollisionBox((-1,-1,-1), (1,1,1))
        sunCol = CollisionNode('sun-collision')
        sunCol.addSolid(sunSolid)
        collider = sunNode.attachNewNode(sunCol)
        collider.setPythonTag('owner', sunNode)
        self.sun.instanceTo(sunNode)

    def createUI(self):
        self.runningtext = OnscreenText(text="Running", pos=(-1.4, 0.8), scale=0.07, fg=(1,1,1,1)) # Temp "pause" menu
        self.selectiontext = OnscreenText(text="Test", pos=(-1.4, 0.7), scale=0.07, fg=(1,1,1,1)) # Selected obj

    
    def selectorUpdate(self,task):
        if hasattr(self.selectedObject, 'name'): # Just make sure that there's an object selected otherwise CRASH
            self.selector.show()
            self.selector.setScale(0.2+(sin(((time.time()))))**2/10)
            pos = Point3()
            pos = (self.compute2dPosition(self.selectedObject,pos))
            if pos != False:
                self.selector.setPos(pos)
        else:
            self.selector.hide()
        return task.cont
    
    def camUpdate(self,task):


        playerMoveSpeed = 10

        x_movement = 0
        y_movement = 0
        z_movement = 0

        # TEMP REMOVE REMOVE 

        #self.disp.text = str(self.root.getDistance(camera))
        #self.disp.scale = self.disp.getDistance(camera)*0.1
        #self.root.setScale(1/(0.01+(self.root.getDistance(camera))))

        # TEMP REMOVE REMOVE 
        
        dt = globalClock.getDt() # Gives update speed (tick period)

        if self.running == 1:
            self.runningtext.text = "Running"
        else:
            self.runningtext.text = "Paused"


        if self.keyMap['forward']:
            x_movement -= dt * playerMoveSpeed * sin(degToRad(camera.getH())) * cos(degToRad(camera.getP()));
            y_movement += dt * playerMoveSpeed * cos(degToRad(camera.getH())) * cos(degToRad(camera.getP()));
            z_movement += dt * playerMoveSpeed * sin(degToRad(camera.getP()));
        if self.keyMap['backward']:
            x_movement += dt * playerMoveSpeed * sin(degToRad(camera.getH())) * cos(degToRad(camera.getP()));
            y_movement -= dt * playerMoveSpeed * cos(degToRad(camera.getH())) * cos(degToRad(camera.getP()));
            z_movement -= dt * playerMoveSpeed * sin(degToRad(camera.getP()));
        if self.keyMap['left']:
            x_movement -= dt * playerMoveSpeed * cos(degToRad(camera.getH()))
            y_movement -= dt * playerMoveSpeed * sin(degToRad(camera.getH()))
        if self.keyMap['right']:
            x_movement += dt * playerMoveSpeed * cos(degToRad(camera.getH()))
            y_movement += dt * playerMoveSpeed * sin(degToRad(camera.getH()))

        # What the fuck is this piece of shit?

        self.root.setPos(
            self.root.getX() - x_movement,
            self.root.getY() - y_movement,
            self.root.getZ() - z_movement,
        )

        if self.cameraSwingActivated == True:
            md = self.win.getPointer(0)
            
            mouseX = md.getX()
            mouseY = md.getY()

            mouseChangeX = mouseX - self.lastMouseX
            mouseChangeY = mouseY - self.lastMouseY

            self.cameraSwingFactor = 10

            currentH = self.camera.getH()
            currentP = self.camera.getP()

            self.camera.setHpr(
                currentH - mouseChangeX * dt * self.cameraSwingFactor,
                min(90, max(-90, currentP - mouseChangeY * dt * self.cameraSwingFactor)),
                0
            )

            self.lastMouseX = mouseX
            self.lastMouseY = mouseY # Mouse stuff

        return task.cont
    
    
    
    def setupControls(self):

        crosshair = OnscreenImage(
            image = 'textures/crosshair.png',
            pos = (0,0,0),
            scale = 0.1,
        )

        crosshair.setTransparency(TransparencyAttrib.MAlpha)

        # SELECTOR OBJECT
        
        self.selector = OnscreenImage(
            image = 'textures/crosshair.png',
            pos = (0,0,0),
            scale = 0.5,
        )
        self.selector.setTransparency(TransparencyAttrib.MAlpha)

        # CAM SETUP
        
        self.keyMap = {
            "forward": False,
            "backward": False,
            "left": False,
            "right": False,
        }

        self.cTrav = CollisionTraverser() # Raycast setup stuff
        ray = CollisionRay()
        ray.setFromLens(self.camNode, (0,0))
        rayNode = CollisionNode('line-of-sight')
        rayNode.addSolid(ray)
        rayNodePath = self.camera.attachNewNode(rayNode)
        self.rayQueue = CollisionHandlerQueue()
        self.cTrav.addCollider(rayNodePath, self.rayQueue)
        
        self.accept('escape', self.releaseMouse)
        self.accept('mouse1', self.handleLeftClick)

        self.accept('w', self.updateKeyMap, ['forward', True])
        self.accept('w-up', self.updateKeyMap, ['forward', False])
        self.accept('a', self.updateKeyMap, ['left', True])
        self.accept('a-up', self.updateKeyMap, ['left', False])
        self.accept('s', self.updateKeyMap, ['backward', True])
        self.accept('s-up', self.updateKeyMap, ['backward', False])
        self.accept('d', self.updateKeyMap, ['right', True])
        self.accept('d-up', self.updateKeyMap, ['right', False])
        
    def updateKeyMap(self, key, value):
        self.keyMap[key] = value

    def handleLeftClick(self):
        self.captureMouse()
        self.selectObj()
        
    def selectObj(self):
        if self.rayQueue.getNumEntries() > 0: # Just some crap to identify the hit object
            self.rayQueue.sortEntries()
            rayHit = self.rayQueue.getEntry(0)

            hitNodePath = rayHit.getIntoNodePath() # wtf are these methods?
            hitObject = hitNodePath.getPythonTag('owner')
            self.selectedObject = hitObject
            if hasattr(self.selectedObject, 'name'): # Just make sure that there's an object selected otherwise CRASH
                self.selectiontext.text = str(self.selectedObject.name)               
            
        pass
        
    def captureMouse(self):

        self.cameraSwingActivated = True

        self.running = 1
        
        md = self.win.getPointer(0)
        self.lastMouseX = md.getX()
        self.lastMouseY = md.getY()
        
        properties = WindowProperties()
        properties.setCursorHidden(True)
        properties.setMouseMode(WindowProperties.M_relative)
        self.win.requestProperties(properties)
        
    def releaseMouse(self):

        self.cameraSwingActivated = False

        self.running = 0
        
        properties = WindowProperties()
        properties.setCursorHidden(False)
        properties.setMouseMode(WindowProperties.M_absolute)
        self.win.requestProperties(properties)

    def compute2dPosition(self, node, point):
        p3 = base.cam.getRelativePoint(node, point) # Gets coords in terms of camera
        # Convert it through the lens to render2d coordinates
        p2 = Point2() 
        if not base.camLens.project(p3, p2): 
            return False
        r2d = Point3(p2[0], 0, p2[1]) 
        # convert to aspect2d
        a2d = aspect2d.getRelativePoint(render2d, r2d) 
        return a2d	



app = Planetarium()
app.run()
