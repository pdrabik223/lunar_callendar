
#include "LedStrip.h"

LedStrip<5> led_strip(16);

const unsigned NO_LEDS = 8;
const unsigned NO_MOON_COLORS = 8;
const double MINIMAL_BRIGHTNESS_LEVEL = 0.1;
const unsigned long DELAY = 60000; // wait 60s

const CRGB moon_colors[NO_MOON_COLORS] = {
    CRGB(220, 220, 220), // white
    CRGB(220, 150, 52),  // yellow
    CRGB(200, 132, 6),   // orange
    CRGB(220, 0, 0),     // red
    CRGB(220, 60, 60),   // pink
    CRGB(149, 66, 245),  // purple
    CRGB(84, 248, 254),  // light blue
    CRGB(0, 0, 220),     // blue
};

const CRGB get_random_color()
{

  if (random(3) != 0)
    return moon_colors[0];
  if (random(2) == 0)
    return moon_colors[random(1, 6)];
  return moon_colors[random(6, 8)];
}

unsigned last_phase = 2;
CRGB phase_color_memory[2] = {get_random_color(), get_random_color()};

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

const CRGB dimm(const CRGB &original_color, double brightness_level = 1)
{

  if (brightness_level <= MINIMAL_BRIGHTNESS_LEVEL)
    return CRGB(original_color.red * MINIMAL_BRIGHTNESS_LEVEL,
                original_color.green * MINIMAL_BRIGHTNESS_LEVEL,
                original_color.blue * MINIMAL_BRIGHTNESS_LEVEL);

  // brightness_level = int(brightness_level * 100) / 100;

  // Serial.println(brightness_level);

  return CRGB(original_color.red * brightness_level,
              original_color.green * brightness_level,
              original_color.blue * brightness_level);
};

void reset_led_colors()
{
  led_strip.Clear();

  for (uint32_t j = 0; j < NO_LEDS; j++)
  {
    led_strip.Set(used_leds[j], dimm(moon_colors[0], MINIMAL_BRIGHTNESS_LEVEL));
  }
}

void test_colors()
{

  while (1 < 2)
  {

    for (uint32_t i = 0; i < NO_MOON_COLORS; i++)
    {
      led_strip.Clear();

      for (uint32_t j = 0; j < NO_LEDS; j++)
      {
        led_strip.Set(used_leds[j], dimm(moon_colors[i], 1));
      }

      led_strip.Update();
      delay(500);
    }
  }
}

const unsigned long moon_lunar_cycle_minutes = 42524;

unsigned long current_moon_lunar_cycle_minutes = 37719;

unsigned previous_moon_phase = -1;

double get_moon_angle()
{
  return double(current_moon_lunar_cycle_minutes) / double(moon_lunar_cycle_minutes);
}

unsigned print_me = 0;
unsigned prev_moon_phase = 2;

struct Phase
{

  unsigned current_moon_phase;
  double dimm_level;

  Phase(double position)
  {

    current_moon_phase = int(position * 8);
    dimm_level = ((position * 8) - current_moon_phase);
    // int val = dimm_level * 1000;
    // dimm_level = val / 1000;
    // Serial.println(dimm_level, 8);
    // dimm_level = ((int)(dimm_level * 100) / 100);

    if (current_moon_phase != prev_moon_phase)
    {
      prev_moon_phase = current_moon_phase;
      phase_color_memory[0] = phase_color_memory[1];
      phase_color_memory[1] = get_random_color();
    }
  }
  const Phase &operator=(const Phase &other)
  {

    this->current_moon_phase = other.current_moon_phase;
    this->dimm_level = other.dimm_level;
    return *this;
  }
  const unsigned get_current_phase() const
  {
    return current_moon_phase;
  }

  const unsigned get_next_phase() const
  {
    return (current_moon_phase + 1) % 8;
  }

  const CRGB get_current_color() const
  {
    return dimm(phase_color_memory[0], 1 - dimm_level);
  }

  const CRGB get_next_color() const
  {
    return dimm(phase_color_memory[1], dimm_level);
  }
};

Phase previous_phase = Phase(0.0);

void update_leds(const Phase &phase)
{
  if (phase.current_moon_phase == previous_phase.current_moon_phase && phase.dimm_level == previous_phase.dimm_level)
  {
    Serial.println("ignore");
    return;
  }
  Serial.println("update");
  previous_phase = phase;

  reset_led_colors();

  led_strip.Set(used_leds[phase.get_current_phase()], phase.get_current_color());
  led_strip.Set(used_leds[phase.get_next_phase()], phase.get_next_color());

  for (uint32_t j = 0; j < NO_LEDS; j++)
  {
    led_strip.Set(used_leds[j] - 1, CRGB(0, 0, 0));
  }

  led_strip.Update();
}

void setup()
{
  randomSeed(45);
  Serial.begin(9600);
  reset_led_colors();
  led_strip.Update();
}

void loop()
{
  // test_colors();
  // auto phase = get_phase();
  update_leds(Phase(get_moon_angle()));

  // delay(1); // 600 x the speed
  ++current_moon_lunar_cycle_minutes;

  if (current_moon_lunar_cycle_minutes >= moon_lunar_cycle_minutes)
    current_moon_lunar_cycle_minutes -= moon_lunar_cycle_minutes;
}