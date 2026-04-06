
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
import planetcsvhandler

import planethandler

confVars= """
win-size 640 480
window-title Planetarium
show-frame-rate-meter False
"""

from pathlib import Path # To avoid weird buggy executions
parent_dir = Path(__file__).resolve().parent
os.chdir(parent_dir)


loadPrcFileData("",confVars)

from direct.showbase.ShowBase import *
from direct.interval.IntervalGlobal import *
from direct.gui.OnscreenText import *
from direct.filter.CommonFilters import CommonFilters
from direct.gui.OnscreenImage import *
from direct.showbase.DirectObject import DirectObject

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
        
        self.font = loader.loadFont("fonts/arial.ttf") # Font importing
        self.lightfont = loader.loadFont("fonts/arial_light.ttf")
        base.setBackgroundColor(0,0,0) # Bg colour
        
        self.select = loader.loadSfx("sounds/select.wav")
        self.display = loader.loadSfx("sounds/display.mp3")
        self.display.setVolume(0.3)
        
        loadingText = OnscreenText(text="Loading...", pos=(0,-0.205), scale=0.1, fg=(0.8,0.8,1,1), font=self.font, align=2, parent=base.a2dTopCenter)
        
        image = OnscreenImage(image='splash.png', parent=render2d)
        
        for i in range(4):
            base.graphicsEngine.renderFrame() # Render loading screen
        
        self.running = 0 # Running is true (Note to future self, this variable is governed by everything instead of everything being governed by this variable FOR SOME REASON)
        self.disableMouse() # Awful name but disables default camera
        lens = base.camLens
        lens.setNearFar(0.005,1e4) # Clip planes (Shit doesn't work fix later if needed)
        render.clear_clip_plane()
        
        self.root = render.attachNewNode('root') # The entire game's root location
        self.localroot = render.attachNewNode('localroot') # This is the "root" of the focused object which is being linked to a place closer to the camera (floating point workaround)

        self.camera.setPos(0,0,0)
        self.camera.setHpr(90,0,0)

        self.speed = 0.01
        
        self.scenetype = "solar"
        self.focusplanet = False # These are for initialising the scenetype variables. For planetary and solar-scale seamless nodes adjustment
        self.localpos = LVecBase3f(0,0,0)
        self.globalpos = LVecBase3f(0,0,0)
        self.setupControls()
        self.releaseMouse()
                
        self.xvel = 0
        self.yvel = 0
        self.zvel = 0

        self.scale = 3000
        
        self.currenttime = 2454525.0

        self.orbits = True
        
        self.createUI() # Create UI
        filters = CommonFilters(base.win, base.cam)
        filters.setBloom()

        self.selectedObject = False
        taskMgr.add(self.camUpdate, 'camUpdate')
        taskMgr.add(self.selectorUpdate, 'selectorUpdate')

        self.createSun()
        self.starGenerate()
        
        self.createPlanetNode()
        
        # self.root.setScale(1)

        # name, body, parentobj, radius, a, e, i, Omega, omega, M0, period, rotperiod, W0, jd_epoch, atm, atmlevel
        self.selectedObject = '' # SELECTED OBJECT VARIABLE       
        self.generatePlanets()
        
        self.root.setPos(-(self.root.find("planets").find("Earth").getPos(render))+LVecBase3f(0.5,0.5,0))
        camera.lookAt(self.root.find("planets").find("Earth"))
        
        self.generateOrbits() # Orbits
        self.toggleOrbits()
        
        # Change to game screen size
        loadingText.removeNode()
        image.removeNode()
        properties = WindowProperties()
        properties.setSize(1280, 720) # Or 1920, 1080
        properties.setOrigin(-2, -2)
        properties.set_icon_filename("icon.ico")
        # properties.setFullscreen(True) # Optional: toggle fullscreen
        base.graphicsEngine.renderFrame()
        base.win.requestProperties(properties)

        ### MUSIC! ###

        music = loader.loadSfx("sounds/music/i.mp3")
        music.set_loop(True)
        music.play()
        
        ###
        
        taskMgr.add(self.orbitUpdate, ('orbitUpdate'))
        
    def createSun(self): # This creates the Sun, why is this special enough for it's own function? WHO KNOWS!
        sunNode = self.root.attachNewNode('Sun')
        self.sun = NodePath(sunNode)
        sun = loader.loadModel("models/sphere")
        sun.setScale(1,1,1)
        sun.setPos(0, 0, 0)
        sun.setName("Sun")
        tex = loader.loadTexture("planets/sun.png")
        sun.setTexture(tex, 0)
        # Board stuff
        
        board = loader.loadModel("models/board")
        board.setScale(8,8,8)
        board.setPos(0, 0, 0)
        board.setName("SunFlair")
        board.setBillboardPointWorld()

        # Texture Board
        
        sun_tex = loader.loadTexture("textures/star.png")
        board.setTexture(sun_tex, 0)
        board.setTransparency(TransparencyAttrib.MAlpha)
        board.reparentTo(sun)
        
        plight = PointLight('plight')
        plight.setColor((1, 1, 1, 1))
        plnp = sunNode.attachNewNode(plight)
        plnp.setPos(0, 0, 0)
        render.setLight(plnp)
        
        sunSolid = CollisionBox((-1,-1,-1), (1,1,1))
        sunCol = CollisionNode('sun-collision')
        sunCol.addSolid(sunSolid)
        collider = sunNode.attachNewNode(sunCol)
        collider.setPythonTag('owner', sunNode)
        collider.setScale(0.1)
        sun.reparentTo(sunNode)
        sunNode.setScale(planethandler.kmToUnits(1.3927e6, self.scale))
        taskMgr.doMethodLater(0.1, self.sunHitboxUpdate, ('hitboxUpdateSun'), extraArgs=[collider.getX(self.root),collider.getY(self.root),collider.getZ(self.root),collider,planethandler.kmToUnits(1.3927e6, self.scale)], appendTask=True)
        taskMgr.add(self.sunGlare, ('glareUpdateSun'), extraArgs=[board.getX(self.root),board.getY(self.root),board.getZ(self.root),board], appendTask=True)        
        sunNode.setLightOff()
        
    def createPlanetNode(self):
        self.root.attachNewNode('planets')
        orbits = render.attachNewNode('orbits')
        orbits.set_bin("fixed", 0);
        orbits.set_depth_test(False);
        orbits.set_depth_write(False)

    # "name","body","parentobj","radius_km","a_AU","e","i_deg","Omega_deg","omega_deg","M0_deg","orbitalperiod_days","rotperiod_days","W0_deg","jd_epoch"
    def generateOrbits(self):
        self.orbitcache = []
        planetData = planetcsvhandler.read_data("planetdata.csv") # Uses custom library to get (in order:)
        for planet in planetData:
            self.writeOrbit(planet[0],planet[1],planet[2],float(planet[3]),float(planet[4]),float(planet[5]),float(planet[6]),
                           float(planet[7]),float(planet[8]),float(planet[9]),float(planet[10]),float(planet[11]),float(planet[12]),float(planet[13]),int(planet[14]),float(planet[15]))

                           
    def generatePlanets(self):
        planetData = planetcsvhandler.read_data("planetdata.csv") # Uses custom library to get (in order:)
        for planet in planetData:
            self.createPlanet(planet[0],planet[1],planet[2],float(planet[3]),float(planet[4]),float(planet[5]),float(planet[6]),
                           float(planet[7]),float(planet[8]),float(planet[9]),float(planet[10]),float(planet[11]),float(planet[12]),float(planet[13]),int(planet[14]),float(planet[15]))
    def drawOrbit(self):
        
        planets = self.root.find("planets")
        tempNode = planets.attachNewNode("tempnode")
        
        camerapos = camera.getPos(self.root)
        
        lines = LineSegs()
        lines.setThickness(1)
        lines.setColor( Vec4(0,0,0.5,1) )
        
        for i in self.orbitcache:
            tempNode.setPos(self.root, LPoint3f(i[0][0])+self.root.getPos())
            
            distance = tempNode.getDistance(render)
            x2 = tempNode.getX(self.root)
            y2 = tempNode.getY(self.root)
            z2 = tempNode.getZ(self.root)
            if distance > 1000:
                tempNode.setPos(self.root, ((1000*((x2)/distance)),(1000*((y2)/distance)),(1000*((z2)/distance))))
                
            lines.moveTo(tempNode.getPos())
            
            for j in i:
                tempNode.setPos(self.root, LPoint3f(j[0])+self.root.getPos())
                lines.setColor(j[1])
                
                distance = camera.getDistance(tempNode)
                x2 = tempNode.getX(self.root)
                y2 = tempNode.getY(self.root)
                z2 = tempNode.getZ(self.root)
                if distance > 1000:
                    tempNode.setPos(self.root, ((1000*((x2)/distance)),(1000*((y2)/distance)),(1000*((z2)/distance))))
                    
                lines.drawTo(tempNode.getPos())

        tempNode.removeNode()
        node = lines.create()
        np = NodePath(node)
        np.reparentTo(render.find("orbits"))
        np.setLightOff()
        
    def orbitUpdate(self, task):
        render.find('orbits').removeNode()
        render.attachNewNode('orbits')
        if self.orbits == True:
            self.drawOrbit()
        return task.again
    
    def writeOrbit(self, name, body, parentobj, radius, a, e, i, Omega, omega, M0, period, rotperiod, W0, jd_epoch, atm, atmlevel): # Some of the arguments aren't even used but we want consistency

        resolution = 25
        temporary = []
        
        planets = self.root.find("planets")
        parentNode = planets.find(parentobj)
        planetNode = planets.attachNewNode(str(name))
        if parentobj == "Sun":
            parentNode = self.sun            
        
        julian = self.currenttime
        
        # jd,
        # jd_epoch,
        # a,
        # e,
        # i,
        # Omega,
        # omega,
        # M0,
        # period
        
            
        location = planethandler.orbitalCalc(julian, jd_epoch, a, e, i, Omega, omega, M0, period)
        planet_pos = LVecBase3f(location[0],location[1],location[2])
        planetNode.setPos(self.root, parentNode.getPos()+planet_pos*self.scale) # 1000 units = 1 AU
        
        distance = camera.getDistance(planetNode)
        x2 = planetNode.getX(render)
        y2 = planetNode.getY(render)
        z2 = planetNode.getZ(render)

        temporary.append([planetNode.getPos(),Vec4(0,0,0.5,1)])
        
        if distance > 1000:
            planetNode.setPos(render, ((1000*((x2)/distance)),(1000*((y2)/distance)),(1000*((z2)/distance))))
            
        for m in range(resolution):
            color = Vec4(0,0,0.2+(m/resolution)/2,1)
            julian = julian+(period/resolution)
            location = planethandler.orbitalCalc(julian, jd_epoch, a, e, i, Omega, omega, M0, period)
            planet_pos = LVecBase3f(location[0],location[1],location[2])
            planetNode.setPos(self.root, parentNode.getPos()+planet_pos*self.scale)
            
            temporary.append([planetNode.getPos(self.root),color])
            
            distance = camera.getDistance(planetNode)
            x2 = planetNode.getX(render)
            y2 = planetNode.getY(render)
            z2 = planetNode.getZ(render)
            
            if distance > 1000:
                planetNode.setPos(render, ((1000*((x2)/distance)),(1000*((y2)/distance)),(1000*((z2)/distance))))
            
        julian = self.currenttime   
        location = planethandler.orbitalCalc(julian, jd_epoch, a, e, i, Omega, omega, M0, period)
        planet_pos = LVecBase3f(location[0],location[1],location[2])
        planetNode.setPos(self.root, parentNode.getPos()+planet_pos*self.scale)

        temporary.append([planetNode.getPos(),Vec4(0,0,0.2,1)])
        
        distance = camera.getDistance(planetNode)
        x2 = planetNode.getX(render)
        y2 = planetNode.getY(render)
        z2 = planetNode.getZ(render)
        if distance > 1000:
            planetNode.setPos(render, ((1000*((x2)/distance)),(1000*((y2)/distance)),(1000*((z2)/distance))))

        planetNode.removeNode()

        self.orbitcache.append(temporary)
  
    def createPlanet(self, name, body, parentobj, radius, a, e, i, Omega, omega, M0, period, rotperiod, W0, jd_epoch, atm, atmlevel): # This creates a planet given the following:

        # body type
        # radius
        # name
        # semi major axis (au)
        # eccentricity
        # inclination
        # longitude of ascending node
        # argument of peripasis
        # mean anomaly at epoch
        # orbital period
        
        size = planethandler.kmToUnits(radius*2, self.scale)
        planets = self.root.find("planets")
        planetNode = planets.attachNewNode(str(name))
        
        planet = loader.loadModel("models/sphere")
        planet.setScale(self.root, 1)
        parentNode = planets.find(parentobj)
        if parentobj == "Sun":
            parentNode = self.sun
        else:
            planetNode.reparentTo(parentNode)
        julian = self.currenttime
        location = planethandler.orbitalCalc(julian, jd_epoch, a, e, i, Omega, omega, M0, period)

        # Rotational Characteristics

        planet.setH(((planethandler.rotationalCalc(julian,jd_epoch,rotperiod,W0))-90)+parentNode.getH())
        
        # Orbital calculations

        planet_pos = LVecBase3f(location[0],location[1],location[2])
        planetNode.setPos(self.root, parentNode.getPos()+planet_pos*self.scale) # 1000 units = 1 AU
        planet.setName(str(name))
        tex = loader.loadTexture("planets/"+(name.lower())+".png")
        planet.setTexture(tex, 0)
        
        Solid = CollisionBox((-1,-1,-1), (1,1,1))
        planetCol = CollisionNode('planet-collision')
        planetCol.addSolid(Solid)
        collider = planetNode.attachNewNode(planetCol)
        collider.setPythonTag('owner', planetNode)
        collider.setPos(planet.getPos())
        
        planetNode.setScale(self.root, size)
        collider.setScale(self.root, planet.getScale(self.root)*1.5)

        board = loader.loadModel("models/board")
        board.setPos(planet.getPos())
        board.setName("PlanetFlair")
        board.setBillboardPointWorld()
        
        planet_tex = loader.loadTexture("textures/star.png")
        board.setTexture(planet_tex, 0)
        board.setTransparency(TransparencyAttrib.MAlpha)
        board.reparentTo(planetNode)
        board.setLightOff()
        
        # Atmosphere start
        if atm == 1:
            if name == "Earth":
                atmshader = Shader.load(Shader.SL_GLSL, vertex="atmosphere.vert.glsl", fragment="atmosphereEmission.frag.glsl")
                planet.setShaderInput("planetTex", tex)
                texEmission = loader.loadTexture("planets/emission/"+(name.lower())+".png")
                planet.setShaderInput("emissionTex", texEmission)
                planet.setShaderInput("intensity", 1.2)
                planet.setShaderInput("level", atmlevel)
                planet.setShaderInput("atmosphereColor", LVecBase3f(0.5, 0.7, 1.0))
            else:
                atmshader = Shader.load(Shader.SL_GLSL, vertex="atmosphere.vert.glsl", fragment="atmosphere.frag.glsl")
                planet.setShaderInput("planetTex", tex)
                planet.setShaderInput("intensity", 1.2)
                planet.setShaderInput("level", atmlevel)
                planet.setShaderInput("atmosphereColor", LVecBase3f(0.5, 0.7, 1.0))

        #
            light_dir = planet.getRelativeVector(render, LVecBase3f((self.sun.getPos(render) - planetNode.getPos(render)).normalized())) # It took an embarassing amount of time for this code to be realised
            planet.setShaderInput("lightDirWorld", light_dir)
        #
            planet.setShader(atmshader)

        # Atmosphere end

        # Saturn Rings

        if name == "Saturn":
            rings = loader.loadModel("models/board")
            rings.setPos(planet.getPos())
            rings.setName("Rings")
            rings.setScale(self.root, 1.7)
            ring_tex = loader.loadTexture("textures/saturn_rings.png")
            rings.setTexture(ring_tex, 0)
            rings.setTransparency(TransparencyAttrib.MAlpha)
            rings.setColor(0.7,0.7,0.7)
            rings.setShaderOff()
            rings.setLightOff()
            rings.reparentTo(planet)
            rings.lookAt(rings.getPos()+light_dir)
            rings.setP(-90)


        # Data stored on planet
        planetNode.setTag("body", body)
        
        
        #taskMgr.doMethodLater(0.1, self.hitboxUpdate, ('hitboxUpdatePlanet'+str(name)), extraArgs=[collider.getX(self.root),collider.getY(self.root),collider.getZ(self.root),collider,size], appendTask=True)        
        taskMgr.add(self.glareUpdate, ('glareUpdatePlanet'+str(name)), extraArgs=[board.getX(self.root),board.getY(self.root),board.getZ(self.root),board,planet,planetNode,collider], appendTask=True)
        #taskMgr.add(self.planetUpdate, ('Planetupdate'+str(name)), extraArgs=[name, planet, planetNode, parentNode, a, e, i, Omega, omega, M0, period, rotperiod, W0, jd_epoch], appendTask=True)
        board.setScale((0.5/size)+(size)/150)
        planet.reparentTo(planetNode)

        if body == "planet":
            planetNode.setTag("one", "Planet")
        elif body == "moon":
            planetNode.setTag("one", "Moon of "+str(parentobj))
        elif body == "dwarf_planet":
            planetNode.setTag("one", "Dwarf Planet")

        planetNode.setTag("two", "Diameter: "+str(radius*2)+" km")
        planetNode.setTag("three", "Semi Major Axis: "+str(a)+" AU")
        planetNode.setTag("four", "Orbital Period: "+str(period)+" days")
        planetNode.setTag("five", "Rotational Period: "+str(rotperiod)+" days")
        planetNode.setTag("six", "Inclination: "+str(i))
        
    def starGenerate(self):
        domeData = csvhandler.read_data("hygdata.csv", 6) # Uses custom library to get (in order:)
        starholder = render.attachNewNode('stars')  
        # Star Name, HIP Number, Right Ascention, Declination, Magnitude, Spectral class (letter)
        for star in domeData:
            name = (str(star[0]))
            if name == "":
               name = ("HIP "+str(star[1])) 
            starNode = starholder.attachNewNode(str(name))
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
            classes = [["o",LVecBase4f(.4,.4,1,0)],
                       ["b",LVecBase4f(.7,.7,1,1)],
                       ["a",LVecBase4f(.9,.9,1,1)],
                       ["f",LVecBase4f(1,1,1,1)],
                       ["g",LVecBase4f(1,1,.9,1)],
                       ["k",LVecBase4f(1,1,.7,1)],
                       ["m",LVecBase4f(1,1,.4,1)],]
            for i in classes:
                if i[0] == starclass:
                    starobj.setColor(i[1])
            starSolid = CollisionBox((-1,-1,-1), (1,1,1))
            starCol = CollisionNode('star-collision')
            starCol.addSolid(starSolid)
            collider = starNode.attachNewNode(starCol)
            collider.setPythonTag('owner', starNode)
            if star[1]:
                starNode.setTag("one", "HIP Number: "+str(star[1]))
            starNode.setTag("two", "RA: "+str(star[2]))
            starNode.setTag("three", "DEC: "+str(star[3]))
            starNode.setTag("four", str(star[5])+" Type Star")
            starNode.setTag("five", "Magnitude: "+str(star[4]))
            #starNode.setTag("six", "DEC: "+str(star[3]))
            starNode.setLightOff()
            
    def createUI(self):
        color = (0.8,0.8,1,1)
        self.runningtext = OnscreenText(text="Running", pos=(-0.1, 0.1), scale=0.04, fg=color, font=self.lightfont, align=1, parent=base.a2dBottomRight) # Temp "pause" menu
        self.selectiontext = OnscreenText(text="", pos=(0.1,-0.15), scale=0.07, fg=color, font=self.font, align=0, parent=base.a2dTopLeft) # Selected obj
        self.desc1 = OnscreenText(text="", pos=(0.1,-0.205), scale=0.05, fg=color, font=self.lightfont, align=0, parent=base.a2dTopLeft)
        self.desc2 = OnscreenText(text="", pos=(0.1,-0.255), scale=0.05, fg=color, font=self.lightfont, align=0, parent=base.a2dTopLeft)
        self.desc3 = OnscreenText(text="", pos=(0.1,-0.305), scale=0.05, fg=color, font=self.lightfont, align=0, parent=base.a2dTopLeft)
        self.desc4 = OnscreenText(text="", pos=(0.1,-0.355), scale=0.05, fg=color, font=self.lightfont, align=0, parent=base.a2dTopLeft)
        self.desc5 = OnscreenText(text="", pos=(0.1,-0.405), scale=0.05, fg=color, font=self.lightfont, align=0, parent=base.a2dTopLeft)
        self.desc6 = OnscreenText(text="", pos=(0.1,-0.455), scale=0.05, fg=color, font=self.lightfont, align=0, parent=base.a2dTopLeft)
        self.speedtext = OnscreenText(text=("7500 km/s"), pos=(-0.1, -0.1), scale=0.05, fg=color, font=self.font, align=1, parent=base.a2dTopRight) # Temp "pause" menu
        self.cameratext = OnscreenText(text="", pos=(0.1,0.1), scale=0.04, fg=color, font=self.lightfont, align=0, parent=base.a2dBottomLeft)
        self.rendertype = OnscreenText(text="", pos=(0.1,0.15), scale=0.04, fg=color, font=self.lightfont, align=0, parent=base.a2dBottomLeft)
        
    def selectorUpdate(self,task):
        if hasattr(self.selectedObject, 'name'): # Just make sure that there's an object selected otherwise CRASH
            pos = Point3()
            pos = (self.compute2dPosition(self.selectedObject,pos))
            if pos != False:
                self.selector.show()   
                self.selector.setPos(pos)
                if self.running == 1:
                    if self.selectedObject.getDistance(camera) < 50:
                        self.selector.setScale(((self.selectedObject.getScale(self.root))*(1.2+((sin(((time.time()))))**2)/8))*(2/(self.selectedObject.getDistance(camera))))
                    else:
                        self.selector.setScale(0.03+((sin(((time.time()))))**2)/80)
            else:
                self.selector.hide()
        else:
            self.selector.hide()
        return task.cont

    def sunHitboxUpdate(self, x, y, z, nodeloc, size, task):
        
        # "WTF does this do?"
        # Essentially, if a hitbox (or really any object) is supposed to be too far away from the camera,
        # Like, far away where it's basically a background,
        # Instead of having it stupid-far, it is actually only a few units away from the camera,
        # and moves with the camera, to make it appear stationary.
        
        tempnode = self.root.attachNewNode('temp')
        tempnode.setPos(LVecBase3f(x,y,z))
        distance = camera.getDistance(tempnode)
        x2 = tempnode.getX(render)
        y2 = tempnode.getY(render)
        z2 = tempnode.getZ(render)
        if distance > 65:
            tempnode.reparentTo(render)
            nodeloc.setScale(1/size)
            nodeloc.setPos(render, ((65*((x2)/distance)),(65*((y2)/distance)),(65*((z2)/distance))))
        else:
            nodeloc.setScale(1)
            nodeloc.setPos(self.root, x,y,z)
        tempnode.removeNode()
        return task.again

    def planetUpdate(self, name, planet, planetNode, parentNode, a, e, i, Omega, omega, M0, period, rotperiod, W0, jd_epoch, task):
        if not planet.getName == self.focusplanet:
            planets = self.root.find("planets")
            
            julian = self.currenttime
            location = planethandler.orbitalCalc(julian, jd_epoch, a, e, i, Omega, omega, M0, period)

            # Rotational Characteristics

            planet.setH(((planethandler.rotationalCalc(julian,jd_epoch,rotperiod,W0))-90)+parentNode.getH())
            
            # Orbital calculations

            planet_pos = LVecBase3f(location[0],location[1],location[2])
            planetNode.setPos(self.root, parentNode.getPos()+planet_pos*self.scale) # 1000 units = 1 AU
            collider = planetNode.find("planet-collision")
            collider.setPos(planet.getPos())

            board = planetNode.find("PlanetFlair")
            board.setPos(planet.getPos())

            # Saturn Rings

            if name == "Saturn":
                rings = planet.find("Rings")
                rings.setPos(planet.getPos())
                rings.lookAt(self.sun)
                rings.setH((rings.getH()+180))
                rings.setP(90)
                rings.setR(0)         
            
    def glareUpdate(self, x, y, z, nodeloc, planetloc, planetparentloc, collider, task):

        # SAME AS HITBOXUPDATE BUT FOR A GLARE WHICH APPEARS WHEN FAR AWAY ( LIKE REAL LIFE )!
        
        tempnode = self.root.attachNewNode('temp')
        tempnode.setPos(LVecBase3f(x,y,z))
        distance = camera.getDistance(tempnode)
        x2 = tempnode.getX(render)
        y2 = tempnode.getY(render)
        z2 = tempnode.getZ(render)
        objname = planetloc.getName()
        if planetparentloc.hasTag("body"):
            bodytype = planetparentloc.getTag("body")
        if distance > 250:
            if self.focusplanet == objname:
                self.rendertype.text = ("Solar Render Sphere")
                self.localroot.setPos(0,0,0)
                planetparentloc.setScale(planetparentloc.getScale(self.root))
                self.scenetype = "solar"
                self.focusplanet = False
                planetparentloc.reparentTo(self.root.find("planets"))
                planetparentloc.setPos(self.root, self.globalpos)
            nodeloc.show()
            planetloc.hide()
            tempnode.reparentTo(render)
            nodeloc.setPos(render, ((250*((x2)/distance)),(250*((y2)/distance)),(250*((z2)/distance))))
            collider.setScale(self.root, 1)
            collider.setPos(render, ((65*((x2)/distance)),(65*((y2)/distance)),(65*((z2)/distance))))
        else:
            collider.setScale(self.root, planetloc.getScale(self.root)*1.5)
            collider.setPos(planetloc, (0,0,0))
            if self.scenetype == "solar" and (bodytype == "planet" or bodytype == "dwarf_planet") : # We only want the body-as-center function to happen with planets, moons are overkill
                self.rendertype.text = (str(objname)+" Render Sphere")
                self.localroot.setPos(0,0,0)
                planetparentloc.setScale(planetparentloc.getScale(self.localroot))
                self.scenetype = "planetary"
                self.focusplanet = objname
                self.localpos = planetparentloc.getPos(self.localroot)
                self.globalpos = planetparentloc.getPos(self.root)
                planetparentloc.reparentTo(self.localroot)
                planetparentloc.setPos(self.localroot, self.localpos)
                self.localpos = planetloc.getPos(self.localroot)
            nodeloc.hide()
            planetloc.show()
        tempnode.removeNode()
        return task.again
    
    def sunGlare(self, x, y, z, nodeloc, task):

        # SAME AS HITBOXUPDATE BUT FOR A GLARE WHICH APPEARS WHEN FAR AWAY ( LIKE REAL LIFE )!
        
        tempnode = self.root.attachNewNode('temp')
        tempnode.setPos(LVecBase3f(x,y,z))
        distance = camera.getDistance(tempnode)
        x2 = tempnode.getX(render)
        y2 = tempnode.getY(render)
        z2 = tempnode.getZ(render)
        if distance > self.scale:
            tempnode.reparentTo(render)
            nodeloc.setPos(render, ((self.scale*((x2)/distance)),(self.scale*((y2)/distance)),(self.scale*((z2)/distance))))
        else:
            nodeloc.setPos(x,y,z)
        tempnode.removeNode()
        return task.again
    
    def camUpdate(self,task):

        self.cameratext.text = ("Camera Render Rotation "+str(camera.getH(render))+" : "+str(camera.getP(render))+" : "+str(camera.getR(render)))
        playerMoveSpeed = self.speed
        movesmoothness = 1.1 # Higher = less smooth
        
        x_movement = self.xvel
        y_movement = self.yvel
        z_movement = self.zvel
        
        dt = globalClock.getDt() # Gives update speed (tick period)

        if self.running == 1:
            self.runningtext.text = "Running"
        else:
            self.runningtext.text = "Paused"
        # if self.running == 1:
        # if True
        if self.running == 1:
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

            
        self.localroot.setPos(
            self.localroot.getX() - x_movement,
            self.localroot.getY() - y_movement,
            self.localroot.getZ() - z_movement,
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
        self.accept('r', self.changespeed, extraArgs=[2])
        self.accept('f', self.changespeed, extraArgs=[0.5])
        self.accept('o', self.toggleOrbits)
        self.accept('t', self.generateOrbits) 

    def toggleOrbits(self):
        self.display.play()
        if self.orbits == True:
            self.orbits = False
        else:
            self.orbits = True
            
    def changespeed(self, val):
        if (planethandler.unitsToKm((self.speed)*globalClock.getDt()*globalClock.getAverageFrameRate()*10, self.scale))*val > 1000:
            self.speed = (self.speed)*val
            self.speedtext.setText((str(round(planethandler.unitsToKm((self.speed)*globalClock.getDt()*globalClock.getAverageFrameRate()*10, self.scale)/100)*100))+" km/s")
        
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
            if not self.selectedObject == hitObject:
                self.select.play()
                self.selectedObject = hitObject
            if self.selectedObject is not None:
                if hasattr(self.selectedObject, 'name'): # Just make sure that there's an object selected otherwise CRASH
                    self.selectiontext.text = str(self.selectedObject.name)
                else:
                    self.selectiontext.text = "" # IDK when an object would be nameless, but...
                    
                if self.selectedObject.hasTag("one"):
                    self.desc1.text = (str(self.selectedObject.getTag("one")))
                else:
                    self.desc1.text = ""
                    
                if self.selectedObject.hasTag("two"):
                    self.desc2.text = (str(self.selectedObject.getTag("two")))
                else:
                    self.desc2.text = ""
                    
                if self.selectedObject.hasTag("three"):
                    self.desc3.text = (str(self.selectedObject.getTag("three")))
                else:
                    self.desc3.text = ""

                if self.selectedObject.hasTag("four"):
                    self.desc4.text = (str(self.selectedObject.getTag("four")))
                else:
                    self.desc4.text = ""

                if self.selectedObject.hasTag("five"):
                    self.desc5.text = (str(self.selectedObject.getTag("five")))
                else:
                    self.desc5.text = ""

                if self.selectedObject.hasTag("six"):
                    self.desc6.text = (str(self.selectedObject.getTag("six")))
                else:
                    self.desc6.text = ""
            
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

app = Planetarium()
app.run()
