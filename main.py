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
"🌑 New Moon","🌒 Waxing Crescent","🌓 First Quarter","🌔 Waxing Gibbous","🌕 Full Moon","🌖 Waning Gibbous","🌗 Last Quarter","🌘 Waning Gibbous"
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


brightness = 255
moon_cycle_length_days = 29.53059
known_moon_phase_and_time = (
4,  # FULL_MOON
(2026,2,1,23,9,0,0,0)
)
seconds_in_day = 86400
uptime_minutes = 0
led_color = Color.white()
is_color_random = False
is_night_mode = False

current_phase = 4

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
    
    return f"{uptime // (24 * 60)}days {uptime // 60}h {uptime%60}min"


def favicon(cl: socket.socket, parameters: dict):
    cl.sendall(compose_response())
    
def home_page(cl: socket.socket, parameters: dict):    
    cl.sendall(compose_response(response=format_dict(load_html("static/index.html"),{
    "local_time" : time_str(),
    "lunar_phase" : moon_phases_string[current_moon_phase_id()],
    "uptime":get_operation_time(uptime_minutes),
    "brightness" : brightness,
    "color" : get_hex_color(led_color),
    "is_color_random":  "checked" if is_color_random else "",
    "is_night_mode_on": "checked" if is_night_mode else "",
    "night_mode_start":get_hour_and_minute(night_mode_start),
    "night_mode_end":get_hour_and_minute(night_mode_end),
    }
)))
    
def save_settings(cl: socket.socket, parameters: dict):
    
    global brightness
    global led_color
    global is_color_random
    global is_night_mode
    global night_mode_start
    global night_mode_end
        
    brightness = int(parameters.get('brightness', brightness))

    if brightness < 0: brightness = 0
    if brightness > 255: brightness = 255
    
    is_color_random = parameters.get('isColorRandom', 
                                     "true" if is_color_random else "false") == "true"
    
    is_night_mode = parameters.get('isNightMode', 
                                     "true" if is_night_mode else "false") == "true"
    
    new_color_str = parameters.get('color', get_hex_color(led_color))
    
    led_color = Color(*tuple(int(new_color_str[i:i+2], 16) for i in (0, 2, 4)))
    
    night_mode_start = parse_hour_and_minute(parameters.get("nightModeStart", get_hour_and_minute(night_mode_start)))
    
    night_mode_end = parse_hour_and_minute(parameters.get("nightModeEnd", get_hour_and_minute(night_mode_end)))
    
    display_moon_phase(moon_phases[current_moon_phase_id()])
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

def display_moon_phase(phase: int):
    global led_color
    global brightness
    global current_phase
    global is_color_random
    
    led_strip.fill(Color.black())
    
    
    if current_phase != phase:
        current_phase = phase
        if is_color_random:
            led_color = random.choice(moon_colors_rgb)
    if night_mode():
        return
    
    
    led_strip.set_pixel(phase, led_color, brightness)


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
    
def current_moon_phase_id():
    global known_moon_phase_and_time
    offset = int((datetime_diff_seconds(utime.localtime(), known_moon_phase_and_time[1]) / seconds_in_day) % moon_cycle_length_days)
    return (known_moon_phase_and_time[0] + offset) % len(moon_phases)


def animation():
    global uptime_minutes
    while(1<2):
        for _ in range(24 * 60):
            display_moon_phase(moon_phases[current_moon_phase_id()])
            time.sleep(60)
            uptime_minutes+=1
        synch_time(rtc) # once a day synch time of the 
    
    
if __name__ == "__main__":
    # print(get_hex_color(led_color))
    synch_time(rtc)
    random.seed(utime.localtime()[4] * 60 + utime.localtime()[5])
    
    _thread.start_new_thread(animation, ())
    app.register_endpoint("/v1", home_page)
    app.register_endpoint("/v1/save_settings", save_settings)
    app.register_endpoint("/favicon.ico", save_settings)

    try:
        app.main_loop()
    except (KeyboardInterrupt, Exception) as ex:
        print(f"Server error type: {type(ex)}\tmessage: {ex}\texiting")