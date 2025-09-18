# Lunar calendar painting

Quick lamp/painting/clock project. I have no idea how to paint so i use arduino.

# Dependencies  

1. Install [platformio](https://platformio.org/) vs code extension

2. Open lunar_calendar as PlatformIo project dependencies will be automatically installed
    - fastled/FastLED@^3.5.0

# Hardware 

1. Project is based on Arduino UNO (Rev 3)
2. Addressable LED strip 
3. Painting frame and some PLA plastic since I can not draw moon by hand

# [3D models](moon_phase_lamp v5.3mf)
Or [Autodesk Fusion repository](https://a360.co/420mgQl) 

## Simple moon model and behind canvas light refusers  
![3d models](3d_models.png)

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