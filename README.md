# Lunar calendar painting

Quick lamp/painting/clock project. I have no idea how to paint so i need to use leds.


### Assuming fool moon cycle repeats after 29.53059 days

# Images

<img src="wiki/light.jpg" alt="Image Light" width="200"/>
<img src="wiki/dark.jpg" alt="Image Dark" width="200"/>

# Dependencies  

1. Install [platformio](https://platformio.org/) vs code extension

2. Open lunar_calendar as PlatformIo project dependencies will be automatically installed
    - fastled/FastLED@^3.5.0

# Hardware 

1. Project is based on Arduino UNO (Rev 3)
2. Addressable LED strip 
3. Painting frame and some PLA plastic since I can not draw moon by hand

# 3D models 
<img src="wiki/3d_models.png" alt="Image Dark" width="300"/>

From the left: 
1. Corner light diffuser, located in the frame corner behind canvas, with cutout for led strip
2. Side light diffuser, glued to the side of the frame behind canvas
3. My simplified depiction of the moon   

All were printed with PLA and glued to the canvas.

Download all as [3mf file](moon_phase_lamp_v5.3mf) or [Autodesk Fusion repository](https://a360.co/420mgQl).



# Moon clock math

Full Moon cycle last ~29.53059 days, and we usually distinguish 8 different moon phases:
1. New Moon
2. Waxing Crescent
3. First Quarter
4. Waxing Gibbous
5. Full Moon 
6. Waning Gibbous
7. Last Quarter
8. Waning Crescent 

So it's simple matter of:
   1. Establishing current moon cycle time 
   2. Keeping time using arduino build in clock ([delay](https://docs.arduino.cc/language-reference/en/functions/time/delay/) function). I'ts not perfect but inaccuracies should average out over 29 days of moon cycle.

In addition I also implemented randomized moon colors. I didn't bother simulating moon-earth-sun system, or connecting to remote api providing moon color state. I just randomized it.

Source: [science.nasa.gov](https://science.nasa.gov/moon/moon-phases/) [current moon phase](https://moonphases.co.uk/) 

