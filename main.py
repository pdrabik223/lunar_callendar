from math import floor
import random
import time
import utime
from pi_pico_neopixel_tools.color import Color
from pi_pico_w_server_tools.app import App, compose_response, format_dict, load_html
import socket
from pi_pico_neopixel_tools.led_strip import LedStrip 
# import ephem
import ntptime
from machine import RTC
import _thread

NEW_MOON = 15 #ok
WAXING_CRESCENT = 13
FIRST_QUARTER = 11
WAXING_GIBBOUS = 9
FULL_MOON = 7 # ok
WANING_GIBBOUS = 5
LAST_QUARTER = 3
WANING_CRESCENT = 1

moon_phases = [   
NEW_MOON,WAXING_CRESCENT,FIRST_QUARTER,WAXING_GIBBOUS,FULL_MOON,WANING_GIBBOUS,LAST_QUARTER,WANING_CRESCENT
]

moon_phases_string = [   
"🌑 New Moon","🌒 Waxing Crescent","🌓 First Quarter","🌔 Waxing Gibbous","🌕 Full Moon","🌖 Waning Gibbous","🌗 Last Quarter","🌘 Waning Crescent"
]

moon_colors_rgb = [
    Color(220, 223, 230),  # silvery white
    Color(240, 224, 160),  # pale yellow
    Color(255, 204, 102),  # golden
    Color(255, 165, 70),   # orange
    Color(178, 72, 56),    # reddish
    Color(184, 115, 51),   # copper
    Color(169, 169, 169),  # gray
    Color(188, 198, 204),  # ashen
    Color(173, 216, 230),  # blue tint
    Color(147, 112, 219),  # purple – medium
    Color(186, 85, 211),   # purple – soft orchid
    Color(255, 182, 193),  # pink – light
    Color(255, 105, 180)   # pink – hot pink
]


led_strip = LedStrip(16, 22)
app = App(hostname="lunar_calendar.local")
rtc = RTC()

is_animation_on = False
animation_timeout = 5 # in minutes
animation_timer = 0
brightness = 100
brightness_night_mode = 50
moon_cycle_length_days = 29.53059
known_moon_phase_and_time = (
0, # index of the phase in moon phases array, corresponds to New Moon 
(2026,1,18,20,52,0,0,0)
)
seconds_in_day = 86400
uptime_minutes = 0
led_color = Color.white()
is_color_random = False
is_night_mode = False

current_phase = 1

night_mode_start = (0,0,0,23,59,0,0,0)
night_mode_end = (0,0,0,5,30,0,0,0)

def parse_hour_and_minute(data:str):
    data = data.split(":")
    hour = int(data[0])
    minute = int(data[1])
    
    return (0,0,0,hour,minute,0,0,0)


def get_hour_and_minute(timestamp:tuple):
    hour = timestamp[3]
    minute = timestamp[4]
    
    if hour < 10:
        hour = f"0{hour}"
    else:
        hour = f"{hour}"
    
    if minute < 10:
        minute = f"0{minute}"
    else:
        minute = f"{minute}"
    
    return f"{hour}:{minute}"
    
    
def hexify(num):
    return f"{num:02x}"

def time_str():
    t = utime.localtime()
    dt = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
    t[0], t[1], t[2], t[3], t[4], t[5]
)
    return dt
    
def get_hex_color(color:Color):
    
    return '#' + (''.join(hexify(value) for value in color.to_tuple()))

def get_operation_time(uptime:int):
    if uptime <= 0:
        return "<1min"
    
    if uptime < 60:
        return f"{uptime}min"
    
    if uptime < 24 * 60:
        return f"{uptime // 60}h {uptime%60}min"
    
    return f"{(uptime // (24 * 60))}days {(uptime % (24 * 60)) // 60}h {floor(uptime%60)}min"


def favicon(cl: socket.socket, parameters: dict):
    cl.sendall(compose_response())
    
def home_page(cl: socket.socket, parameters: dict):    
    cl.sendall(compose_response(response=format_dict(load_html("static/index.html"),{
    "local_time" : time_str(),
    "lunar_phase" : moon_phases_string[current_moon_phase_id()],
    "moon_age": (datetime_diff_seconds(utime.localtime(), known_moon_phase_and_time[1]) / seconds_in_day) % moon_cycle_length_days,
    "animation_timeout":animation_timeout,
    "uptime":uptime_minutes,
    "brightness" : brightness,
    "color" : get_hex_color(led_color),
    "night_mode_start":get_hour_and_minute(night_mode_start),
    "is_color_random":  "checked" if is_color_random else "",
    "is_night_mode_on": "checked" if is_night_mode else "",
    "night_mode_start":get_hour_and_minute(night_mode_start),
    "night_mode_end":get_hour_and_minute(night_mode_end),
    "night_mode_brightness" : brightness_night_mode
    
    }
)))
    
def save_settings(cl: socket.socket, parameters: dict):
    
    global brightness
    global led_color
    global is_color_random
    global is_night_mode
    global night_mode_start
    global night_mode_end
    global brightness_night_mode
    global animation_timeout
    
    brightness = int(parameters.get('brightness', brightness))
    if brightness < 0: brightness = 0
    if brightness > 255: brightness = 255
    
    brightness_night_mode = int(parameters.get('nightModeBrightness', brightness_night_mode))
    if brightness_night_mode < 0: brightness_night_mode = 0
    if brightness_night_mode > 255: brightness_night_mode = 255
    
    animation_timeout = int(parameters.get('animationTimeout', animation_timeout))
    if animation_timeout < 0: animation_timeout = 0
    
    is_color_random = parameters.get('isColorRandom', 
                                     "true" if is_color_random else "false") == "true"
    
    is_night_mode = parameters.get('isNightMode', 
                                     "true" if is_night_mode else "false") == "true"
    
    new_color_str = parameters.get('color', get_hex_color(led_color))
    
    led_color = Color(*tuple(int(new_color_str[i:i+2], 16) for i in (0, 2, 4)))
    
    night_mode_start = parse_hour_and_minute(parameters.get("nightModeStart", get_hour_and_minute(night_mode_start)))
    
    night_mode_end = parse_hour_and_minute(parameters.get("nightModeEnd", get_hour_and_minute(night_mode_end)))
    
    update_leds()
    cl.sendall(compose_response())


def night_mode():
    global night_mode_start
    global night_mode_end
    global is_night_mode
    
    if not is_night_mode: return
    current_time = utime.localtime()

    current = current_time[3] * 60 + current_time[4]
     
    start = night_mode_start[3] * 60 + night_mode_start[4]
    end = night_mode_end[3] * 60 + night_mode_end[4]
    
    if end < start:
        return not(current < start  and current > end)
        
    if current > start and current < end:
        return True
    
    return False

def loading_animation(phase: int):
    global led_color
    global brightness
    global current_phase
     
     
    led_brightness = brightness
    
    if night_mode():
        led_brightness = brightness_night_mode

    if current_phase != phase:
        current_phase = phase
        if is_color_random:
            led_color = random.choice(moon_colors_rgb)
            

    led_strip.fill(Color.black())
    
    for i in range(moon_phases.index(phase), len(moon_phases) + moon_phases.index(phase)):
        led_strip.set_pixel(moon_phases[i % len(moon_phases)], led_color, led_brightness)
        time.sleep(0.1)
        

def display_moon_phase(phase: int):
    global led_color
    global brightness
    global current_phase
     
     
    led_brightness = brightness
    
    if night_mode():
        led_brightness = brightness_night_mode


    led_strip.fill(Color.black())
    

    if current_phase != phase:
        current_phase = phase
        if is_color_random:
            led_color = random.choice(moon_colors_rgb)
            
    
    led_strip.set_pixel(phase, led_color, led_brightness)


def datetime_diff_seconds(timestamp_a,timestamp_b):
    
    t1 = utime.mktime(timestamp_a)
    t2 = utime.mktime(timestamp_b)
    return t1 - t2

def synch_time(rtc, timezone_offset = 1):
    ntptime.settime()
    
    t = time.time() + (60 * (60 * timezone_offset))
    tm = time.localtime(t)
    
    rtc.datetime((
    tm[0], tm[1], tm[2],
    tm[6] + 1,        # weekday (1–7)
    tm[3], tm[4], tm[5], 0
))
    
lunar_phases = [
    (0, 1),
    (1, 6.38),
    (6.39, 8.38),
    (8.39, 13.76),
    (13.77, 15.76),
    (15.77, 21.14),
    (21.15, 23.14),
    (23.15, 28.53),
    (28.54, 29.53)
]
def get_phase_id(lunar_age):
 
    for id, (start, end) in enumerate(lunar_phases):
        if start <= lunar_age <= end:
            return id % 8 
        
def current_moon_phase_id():
    global known_moon_phase_and_time
    
    moon_age = (datetime_diff_seconds(utime.localtime(), known_moon_phase_and_time[1]) / seconds_in_day) % moon_cycle_length_days
    offset = get_phase_id(moon_age)
    
    return (known_moon_phase_and_time[0] + offset) % len(moon_phases)

def update_leds():
    global animation_timeout
    global animation_timer
    global is_animation_on
    
    if (animation_timer < animation_timeout ):  
        if (not is_animation_on):
            loading_animation(moon_phases[current_moon_phase_id()])
        display_moon_phase(moon_phases[current_moon_phase_id()])
        is_animation_on = True
    else:
        led_strip.fill(Color.black())
        is_animation_on = False
        
def animation():
    global uptime_minutes
    global animation_timer
    while(1<2):
        for _ in range(24 * 60 * 60):
            update_leds()
            time.sleep(1)
            
            uptime_minutes += 1 / 60
            animation_timer += 1
            
        synch_time(rtc) # once a day synch time of the 

def run_animation(cl: socket.socket, parameters: dict):
    
    global animation_timer
    animation_timer = 0
    cl.sendall(compose_response())


def status(cl: socket.socket, parameters: dict):
    cl.sendall(compose_response())


if __name__ == "__main__":
    # print(get_hex_color(led_color))
    synch_time(rtc)
    random.seed(utime.localtime()[4] * 60 + utime.localtime()[5])
    _thread.start_new_thread(animation, ())
    
    app.register_endpoint("/v1", home_page)
    app.register_endpoint("/v1/save_settings", save_settings)
    app.register_endpoint("/v1/run_animation", run_animation)
    app.register_endpoint("/v1/status", status)
    # app.register_endpoint("/favicon.ico", save_settings)


    try:
        app.main_loop()
    except (KeyboardInterrupt, Exception) as ex:
        print(f"Server error type: {type(ex)}\tmessage: {ex}\texiting")