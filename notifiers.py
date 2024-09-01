import logging
import requests
from items import Course


class Notifier:
    def courses_available(self, courses: list[Course]):
        pass


class StdoutNotifier(Notifier):
    def courses_available(self, courses: list[Course]):
        courses_string = "\n".join(sorted(
            [f"- {c.name}, {c.date_start} - {c.date_end} {c.time_start} @ {c.location}" for c in courses]
        ))
        print(
            f"{len(courses)} swimming courses are available. Go get one now!\n"
            f"The available courses are:\n"
            f"{courses_string}"
        )


class IftttNotifier(Notifier):
    def __init__(self, key: str) -> None:
        self.key = key

    def courses_available(self, courses: list[Course]):
        logger = logging.getLogger("blscc.notifiers")

        course_names = {c.name for c in courses}
        value2 = (
            f"Swimming course '{next(iter(course_names))}' is available. Go get it now!"
            if len(course_names) == 1
            else f"{len(courses)} swimming courses are available. Go get one now!"
        )
        payload = {
            "value1": "Swimming courses available",
            "value2": value2,
            "value3": courses[0].search_url,
        }
        logger.debug(f"Calling IFTTT with payload {payload}")
        response = requests.post(
            f"https://maker.ifttt.com/trigger/hhpl/with/key/{self.key}", json=payload
        )
        response.raise_for_status()
