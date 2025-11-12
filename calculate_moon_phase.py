import datetime
import ephem
from typing import List, Tuple
import datetime


def get_phase_on_day(year: int, month: int, day: int):
  """Returns a float from 0-1. where 0=new, 0.5=full, 1=new"""

  date = ephem.Date(datetime.date(year,month,day))

  nnm = ephem.next_new_moon(date)
  pnm = ephem.previous_new_moon(date)

  lunation = (date-pnm)/(nnm-pnm)

  return lunation



if  __name__ == "__main__":
    now = datetime.datetime.now()
    minutes_in_moon_cycle = 42524.0496
    print((get_phase_on_day(now.year, now.month, now.day) + (1 / 16)) * minutes_in_moon_cycle)
    