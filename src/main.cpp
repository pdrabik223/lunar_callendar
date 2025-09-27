
#include "LedStrip.h"

LedStrip<5> led_strip(16);

const unsigned NO_LEDS = 8;
const unsigned NO_MOON_COLORS = 6;
const double MINIMAL_BRIGHTNESS_LEVEL = 0.1;
const unsigned long DELAY = 60000; // wait 60s

const CRGB moon_colors[NO_MOON_COLORS] = {
    CRGB(180, 180, 180), // white
    CRGB(220, 150, 52),  // yellow
    CRGB(200, 132, 6),   // orange
    CRGB(220, 80, 80),   // pink
    CRGB(149, 66, 245),  // purple
    CRGB(84, 248, 254),  // light blue
};

const CRGB get_random_color()
{
  if (random(2) != 0)
    return moon_colors[0];
  if (random(2) == 0)
    return moon_colors[random(1, 4)];
  return moon_colors[random(4, 6)];
}

CRGB phase_color_memory[2] = {get_random_color(), get_random_color()};

const unsigned used_leds[NO_LEDS] = {
    15, // new moon
    13, // Waxing Crescent
    11, // first quarter
    9,  // waxing gibbous
    7,  // full moon
    5,  // waning gibbous
    3,  // last quarter
    1,  // waning crescent
};

const CRGB dimm(const CRGB &original_color,
                const double brightness_level = 1)
{

  if (brightness_level <= MINIMAL_BRIGHTNESS_LEVEL)
    return CRGB(original_color.red * MINIMAL_BRIGHTNESS_LEVEL,
                original_color.green * MINIMAL_BRIGHTNESS_LEVEL,
                original_color.blue * MINIMAL_BRIGHTNESS_LEVEL);

  return CRGB(original_color.red * brightness_level,
              original_color.green * brightness_level,
              original_color.blue * brightness_level);
};

const CRGB avg(const CRGB &a, const CRGB &b)
{
  return CRGB((a.red + b.red) / 2,
              (a.green + b.green) / 2,
              (a.blue + b.blue) / 2);
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

unsigned long current_moon_lunar_cycle_minutes = 7243;

double get_moon_angle()
{
  return double(current_moon_lunar_cycle_minutes) / double(moon_lunar_cycle_minutes);
}

unsigned prev_moon_phase = 2;

struct Phase
{

  unsigned current_moon_phase;
  double dimm_level;

  Phase(double position)
  {

    current_moon_phase = int(position * 8);
    dimm_level = ((position * 8) - current_moon_phase);
    dimm_level *= 1000;
    dimm_level = int(dimm_level);
    dimm_level /= 1000;

    if (dimm_level < MINIMAL_BRIGHTNESS_LEVEL)
      dimm_level = MINIMAL_BRIGHTNESS_LEVEL;

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

  const unsigned get_phase(const unsigned offset = 0) const
  {
    return (current_moon_phase + offset) % 8;
  }

  const CRGB get_current_color() const
  {
    return dimm(phase_color_memory[0], 1 - dimm_level);
  }

  const CRGB get_next_color() const
  {
    return dimm(phase_color_memory[1], dimm_level);
  }

  const CRGB average_color() const
  {
    return avg(phase_color_memory[0], phase_color_memory[1]);
  }
};

Phase previous_phase = Phase(0.0);

void update_leds(const Phase &phase)
{
  if (phase.current_moon_phase == previous_phase.current_moon_phase &&
      int(phase.dimm_level * 1000) == int(previous_phase.dimm_level * 1000))
  {
    return;
  }

  previous_phase = phase;
  led_strip.Clear();

  for (uint32_t j = 0; j < NO_LEDS; j++)
  {
    led_strip.Set(used_leds[j], dimm(phase.average_color(), MINIMAL_BRIGHTNESS_LEVEL));
  }

  auto avg_color = phase.average_color();

  led_strip.Set(used_leds[phase.get_phase()], dimm(avg_color, phase.dimm_level));
  led_strip.Set(used_leds[phase.get_phase(-1)], dimm(avg_color, 1 - phase.dimm_level));

  for (uint32_t j = 0; j < NO_LEDS; j++)
  {
    led_strip.Set(used_leds[j] - 1, CRGB(0, 0, 0));
  }

  led_strip.Update();
}

void setup()
{
  randomSeed(1337);
  led_strip.Update();
}

void loop()
{
  update_leds(Phase(get_moon_angle()));

  delay(DELAY);

  ++current_moon_lunar_cycle_minutes;

  if (current_moon_lunar_cycle_minutes >= moon_lunar_cycle_minutes)
    current_moon_lunar_cycle_minutes -= moon_lunar_cycle_minutes;
}