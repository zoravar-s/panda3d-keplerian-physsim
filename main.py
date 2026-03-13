
###
# The following code you are about to bear witness to is so unreadable, that when I wrote it, only God and I could understand what it meant.
# Now, only God can.
###
import math
from math import *
from panda3d.core import *
import sys
import os
import time
import csv
import csvhandler

confVars= """
win-size 1280 720
window-title Planetarium
show-frame-rate-meter False
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

def loadStar(self):
    self.starbase = loader.loadModel("models/sphere")
    self.starbase.setScale(1,1,1)
    self.starbase.setPos(0, 0, 0)
    self.starbase.reparentTo(render)

def raToRad(value):
    return value*((2*pi)/24)

class Planetarium(ShowBase):
    
    def __init__(self): ### MAIN INIT MAIN INIT MAIN INIT MAIN INIT MAIN INIT MAIN INIT MAIN INIT MAIN INIT MAIN INIT MAIN INIT MAIN INIT MAIN INIT MAIN INIT MAIN INIT MAIN INIT MAIN INIT ###
               
        ShowBase.__init__(self)
        self.running = 0 # Running is true (Note to future self, this variable is governed by everything instead of everything being governed by this variable FOR SOME REASON)
        self.disableMouse() # Awful name but disables default camera
        lens = base.camLens
        # lens.setNearFar(0.1,9*10^7) # Clip planes (Shit doesn't work fix later if needed)
        base.setBackgroundColor(0,0,0) # Bg colour
        self.font = loader.loadFont("fonts/charon.ttf")
        
        self.root = render.attachNewNode('root') # The entire game's root location

        self.camera.setPos(10,0,0)
        self.camera.setHpr(90,0,0)
        
        self.setupControls()
        self.releaseMouse()
                
        self.xvel = 0
        self.yvel = 0
        self.zvel = 0

        time.sleep(1)
        
        self.createUI() # Create UI

        filters = CommonFilters(base.win, base.cam)
        filters.setBloom()

        taskMgr.add(self.camUpdate, 'camUpdate')
        taskMgr.add(self.selectorUpdate, 'selectorUpdate')

        self.createSun()
        self.starGenerate()
        
        self.root.setScale(1)
        
        self.selectedObject = '' # SELECTED OBJECT VARIABLE
        
    def createSun(self): # This creates the Sun, why is this special enough for it's own function? WHO KNOWS!
        self.sun = loader.loadModel("models/sphere")
        self.sun.setScale(1,1,1)
        self.sun.setPos(0, 0, 0)
        self.sun.setName("Sun")
        tex = loader.loadTexture("planets/sun.png")
        self.sun.setTexture(tex, 0)
        # Board stuff
        
        self.board = loader.loadModel("models/board")
        self.board.setScale(8,8,8)
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
        self.runningtext = OnscreenText(text="Running", pos=(1.6, 0.8), scale=0.05, fg=(1,1,1,1), font=self.font, align=1) # Temp "pause" menu
        self.selectiontext = OnscreenText(text="", pos=(-1.6, 0.8), scale=0.07, fg=(1,1,1,1), font=self.font, align=0) # Selected obj
        self.hiptext = OnscreenText(text="", pos=(-1.6, 0.75), scale=0.05, fg=(1,1,1,1), font=self.font, align=0) # Selected obj hip number
        self.rightasctext = OnscreenText(text="", pos=(-1.6, 0.7), scale=0.05, fg=(1,1,1,1), font=self.font, align=0) # Selected obj right ascention
        self.decltext = OnscreenText(text="", pos=(-1.6, 0.65), scale=0.05, fg=(1,1,1,1), font=self.font, align=0) # Selected obj declination

    
    def selectorUpdate(self,task):
        if hasattr(self.selectedObject, 'name'): # Just make sure that there's an object selected otherwise CRASH
            pos = Point3()
            pos = (self.compute2dPosition(self.selectedObject,pos))
            if pos != False:
                self.selector.show()   
                self.selector.setPos(pos)
                if self.running == 1:
                    self.selector.setScale(((self.selectedObject.getScale())*(1.2+((sin(((time.time()))))**2)/10))*(1/(self.selectedObject.getDistance(camera))))
            else:
                self.selector.hide()
        else:
            self.selector.hide()
        return task.cont
    
    def camUpdate(self,task):


        playerMoveSpeed = 10
        movesmoothness = 1.2 # Higher = less smooth
        
        x_movement = self.xvel
        y_movement = self.yvel
        z_movement = self.zvel

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
        
        self.xvel = x_movement/movesmoothness
        self.yvel = y_movement/movesmoothness
        self.zvel = z_movement/movesmoothness


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
            scale = 0.05,
        )

        crosshair.setTransparency(TransparencyAttrib.MAlpha)

        # SELECTOR OBJECT
        
        self.selector = OnscreenImage(
            image = 'textures/select.png',
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
        self.running = 1
        self.captureMouse()
        self.selectObj()
        
    def selectObj(self):
        if self.rayQueue.getNumEntries() > 0: # Just some crap to identify the hit object
            self.rayQueue.sortEntries()
            rayHit = self.rayQueue.getEntry(0)

            hitNodePath = rayHit.getIntoNodePath() # wtf are these methods?
            hitObject = hitNodePath.getPythonTag('owner')
            self.selectedObject = hitObject
            if self.selectedObject is not None:
                if hasattr(self.selectedObject, 'name'): # Just make sure that there's an object selected otherwise CRASH
                    self.selectiontext.text = str(self.selectedObject.name)
                else:
                    self.selectiontext.text = "" # IDK when an object would be nameless, but...
                    
                if self.selectedObject.hasTag("hip"):
                    self.hiptext.text = ("HIP Number: "+str(self.selectedObject.getTag("hip")))
                else:
                    self.hiptext.text = ""
                    
                if self.selectedObject.hasTag("ra"):
                    self.rightasctext.text = ("RA: "+str(self.selectedObject.getTag("ra")))
                else:
                    self.rightasctext.text = ""
                    
                if self.selectedObject.hasTag("dec"):
                    self.decltext.text = ("DEC: "+str(self.selectedObject.getTag("dec")))
                else:
                    self.decltext.text = ""
            
        pass
        
    def captureMouse(self):

        self.cameraSwingActivated = True
            
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
    
    def starGenerate(self):
        domeData = csvhandler.read_data("hygdata.csv", 6.5) # Uses custom library to get (in order:)
        # Star Name, HIP Number, Right Ascention, Declination, Magnitude, Spectral class (letter)
        for star in domeData:
            name = (str(star[0]))
            if name == "":
               name = ("HIP "+str(star[1])) 
            starNode = render.attachNewNode(str(name))
            rightasc = raToRad(float(star[2]))
            decl = degToRad(float(star[3]))
            dist = 100
            magnitude = 2*(1/1.5**(float(star[4])))
            starNode.setPos(
                dist*(math.cos(decl))*(math.cos(rightasc)),
                dist*(math.cos(decl))*(math.sin(rightasc)),
                dist*(math.sin(decl))
            )
            starobj = loader.loadModel("models/board")
            starobj.setScale(magnitude)
            starobj.setColor(1,1,1)
            starobj.reparentTo(starNode)
            starobj.lookAt(camera)
            tex = loader.loadTexture("textures/star.png")
            starobj.setTexture(tex, 0)
            starobj.setTransparency(TransparencyAttrib.MAlpha)
            starclass = (star[5]).lower()
            if starclass == "o":
                starobj.setColor(.4,.4,1)
            elif starclass == "b":
                starobj.setColor(.7,.7,1)
            elif starclass == "a":
                starobj.setColor(.9,.9,1)
            elif starclass == "f":
                starobj.setColor(1,1,1)
            elif starclass == "g":
                starobj.setColor(1,1,.9)
            elif starclass == "k":
                starobj.setColor(1,1,.7)
            elif starclass == "m":
                starobj.setColor(1,1,.4) # This is stupid, I don't care
            starSolid = CollisionBox((-1,-1,-1), (1,1,1))
            starCol = CollisionNode('sun-collision')
            starCol.addSolid(starSolid)
            collider = starNode.attachNewNode(starCol)
            collider.setPythonTag('owner', starNode)
            if star[1]:
                starNode.setTag("hip", str(star[1]))
            starNode.setTag("ra", str(star[2]))
            starNode.setTag("dec", str(star[3]))

app = Planetarium()
app.run()
