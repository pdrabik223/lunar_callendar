
#include "LedStrip.h"

LedStrip<5> led_strip(16);

unsigned get_random_color()
{

  if (random(3) != 0)
    return 0;
  if (random(2) == 0)
    return random(1, 6);
  return random(6, 8);
}
// one thing is to calculate current phase of the moon

// second is to calculate how high over the horizon (for poland) moon is

const unsigned NO_LEDS = 8;

const unsigned NO_MOON_COLORS = 8;
const unsigned long DELAY = 60000; // wait 60s

unsigned last_phase = 2;
unsigned phase_color_memory[2] = {get_random_color(), get_random_color()};

const CRGB moon_colors[NO_MOON_COLORS] = {
    CRGB(110, 110, 110), // white
    CRGB(112, 75, 26),   // yellow
    CRGB(100, 66, 3),    // orange
    CRGB(110, 30, 30),   // pink
    CRGB(110, 0, 0),     // red
    CRGB(42, 124, 140),  // orange
    CRGB(151, 64, 168),  // purple
    CRGB(0, 0, 110),     // blue
};

const CRGB moon_dimm_colors[NO_MOON_COLORS] = {
    CRGB(55, 55, 55), // white
    CRGB(56, 36, 13), // yellow
    CRGB(50, 33, 2),  // orange
    CRGB(55, 15, 15), // pink
    CRGB(55, 0, 0),   // red
    CRGB(21, 75, 70), // orange
    CRGB(75, 32, 84), // purple
    CRGB(0, 0, 55),   // blue
};

const unsigned used_leds[NO_LEDS] = {
    15, // new
    1,  // third quarter
    3,  // waning gibbous
    5,  // full
    7,  // waxing gibbous
    9,  // first quarter
    11, // waxing crescent
    13, // waning crescent

};

const unsigned long moon_lunar_cycle_minutes = 42524046;

const unsigned long moon_lunar_segment_minutes = moon_lunar_cycle_minutes / 16;

unsigned long current_moon_lunar_cycle_minutes = 37771951;

const unsigned get_phase()
{
  unsigned phase = 0;
  unsigned long current_moon_lunar_cycle_minutes_copy = current_moon_lunar_cycle_minutes;
  while (1 < 2)
  {
    if (current_moon_lunar_cycle_minutes_copy < moon_lunar_segment_minutes)
      break;
    current_moon_lunar_cycle_minutes_copy -= moon_lunar_segment_minutes;
    phase++;
  }
  return phase;
}

void update_leds(const unsigned segment)
{
  if (last_phase == segment)
    return;

  last_phase = segment;
  led_strip.Clear();

  for (uint32_t j = 0; j < NO_LEDS; j++)
  {
    led_strip.Set(used_leds[j], CRGB(10, 10, 10));
  }

  if (segment % 2 == 0)
  {
    led_strip.Set(used_leds[segment / 2], moon_colors[phase_color_memory[0]]);
  }
  else
  {
    led_strip.Set(used_leds[segment / 2], moon_dimm_colors[phase_color_memory[0]]);
    if ((segment / 2) + 1 < NO_LEDS)
      led_strip.Set(used_leds[(segment / 2) + 1], moon_dimm_colors[phase_color_memory[1]]);
    else
      led_strip.Set(used_leds[0], moon_dimm_colors[phase_color_memory[1]]);

    phase_color_memory[0] = phase_color_memory[1];
    phase_color_memory[1] = get_random_color();
  }

  for (uint32_t j = 0; j < NO_LEDS; j++)
  {
    led_strip.Set(used_leds[j] - 1, CRGB(0, 0, 0));
  }

  led_strip.Update();
}

void setup()
{
  randomSeed(0);

  for (uint32_t j = 0; j < NO_LEDS; j++)
  {
    led_strip.Set(used_leds[j], CRGB(10, 10, 10));
  }
  led_strip.Update();
}
void loop()
{
  // test_colors();
  auto phase = get_phase();
  update_leds(phase);

  delay(DELAY);
  current_moon_lunar_cycle_minutes += 1;

  if (current_moon_lunar_cycle_minutes >= moon_lunar_cycle_minutes)
    current_moon_lunar_cycle_minutes -= moon_lunar_cycle_minutes;
}