# The Planetarium

This project was created for my A-Level Computer Science NEA. Putting this here for any future students to use as reference as this got 100% in the final grade. This program is very rudimentary in calculations but far more than enough to satisfy the requirements - you shouldn't attempt something like this unless you want a challenge. Anything full-stack with a database can hit all the marks. Stick to what you are familiar with (as I unfortunately wasn't with this engine, so this took way longer than it should've) and if you're not too experienced with full-stack applications, pick a project that can teach you as you create it (I'd recommend looking up courses on full-stack development and having your NEA project be based off of that.)

![Saturn](https://raw.githubusercontent.com/zoravar-s/panda3d-keplerian-physsim/refs/heads/main/screenshots/6.png)

Panda3D Physics simulation of the Solar System and local stellar objects. This uses the HYG Database for stars and a custom database for local Solar System objects. This program launches at the J2000 epoch (though rotational characteristics are heavily simplified in the final program. Tidally locked planets may be rotated wrong.)
Uses Keplerian calculations to solve for each object's orbit and it's current location. Basic shaders with GLSL.

### How to install: <br>
Install Panda3D. Unzip data and have both CSV files in the main directory. Run main.py

### Current controls: <br>
WASD - Movement <br>
R - Increase camera speed <br>
F - Decrease camera speed <br>
O - Toggle orbits <br>
Esc/Left Click - Pause/Resume <br>
Left Click - Select object <br>

Currently the bodies use pre-packaged data for calculations. This may be inaccurate for later dates, as error in the rounded values increases.

<sub>Zoravar Singh. 2025-2026</sub>
