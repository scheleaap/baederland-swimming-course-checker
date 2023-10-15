import re
from datetime import datetime, date, time

import scrapy
from scrapy.crawler import Crawler

from items import Course

DEFAULT_BASE_URL = "https://www.baederland.de/kurse/kursfinder/"

# '18:00-19:00 Uhr'
TIME_PATTERN = re.compile(r"^(\d\d:\d\d)-(\d\d:\d\d) Uhr$")

# '0\t\t\t\t\t\t\t\t\t\t\t\t\t\tfreie Plätze'
AVAILABLE_SLOTS_PATTERN = re.compile(r"^(\d+)\t+freie Plätze$")


class CourseSpider(scrapy.Spider):
    name = "course"

    @classmethod
    def from_crawler(cls, crawler: Crawler, *args, **kwargs):
        return cls(category=crawler.settings.getint("COURSE_CATEGORY"))

    def __init__(self, category: int, *args, **kwargs):
        super(CourseSpider, self).__init__(*args, **kwargs)
        self.start_urls = [
            f"https://www.baederland.de/kurse/kursfinder/?course[category][]={category}&course[weekday][]=1&course[weekday][]=2&course[weekday][]=4&course[weekday][]=5&course[weekday][]=6&course[weekday][]=7"
        ]

    def parse(self, response, **kwargs):
        for weekday in response.css('a.button-list--button'):
            yield response.follow(weekday, self.parse_weekday)

    def parse_weekday(self, response):
        for course in response.css('div.course-item--link a'):
            yield response.follow(course, self.parse_course)

    def parse_course(self, response):
        name = response.css("h2::text").get().strip()

        teaser = response.css(".teaser")[0]

        # '26.10.2023-14.12.2023'
        raw_dates = teaser.css(".datum::text").get().strip()
        # '18:00-19:00 Uhr'
        raw_times = teaser.css(".termin::text").get().strip()
        # 'Elbgaustraße'
        raw_location = teaser.css(".standort::text").get().strip()
        # 'available_slots': '0\t\t\t\t\t\t\t\t\t\t\t\t\t\tfreie Plätze'
        raw_available_slots = teaser.css(".freie-plaetze::text").get().strip()
        # '132,00 €'
        # raw_price = teaser.css(".euro::text").get().strip()

        (date_start, date_end) = self.raw_to_dates(raw_dates)
        (time_start, time_end) = self.raw_to_times(raw_times)
        course = Course(
            name=name,
            url=response.url,
            weekday=date_start.isoweekday(),
            date_start=date_start,
            date_end=date_end,
            time_start=time_start,
            time_end=time_end,
            location=raw_location,
            available_slots=self.raw_to_available_slots(raw_available_slots)
        )
        yield course

    def raw_to_dates(self, raw: str) -> tuple[date, date]:
        splitted = raw.split("-")
        return (
            datetime.strptime(splitted[0], "%d.%m.%Y").date(),
            datetime.strptime(splitted[1], "%d.%m.%Y").date()
        )

    def raw_to_times(self, raw: str) -> tuple[time, time]:
        m = TIME_PATTERN.match(raw)
        return (
            time.fromisoformat(m.group(1)),
            time.fromisoformat(m.group(2))
        )

    def raw_to_available_slots(self, raw: str) -> int:
        m = AVAILABLE_SLOTS_PATTERN.match(raw)
        return int(m.group(1))
