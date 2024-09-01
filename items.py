from dataclasses import dataclass
from datetime import date, time


@dataclass
class Course:
    name: str
    url: str
    weekday: int
    date_start: date
    date_end: date
    time_start: time
    time_end: time
    location: str
    available_slots: int
    search_url: str
