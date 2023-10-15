import logging
import requests
from items import Course


class Notifier:
    def course_is_available(self, course: Course):
        pass


class StdoutNotifier(Notifier):
    def course_is_available(self, course: Course):
        logging.info(f"Swimming course '{course.name}' is available. Go get it now!")


class IftttNotifier(Notifier):
    def __init__(self, key: str) -> None:
        self.key = key

    def course_is_available(self, course: Course):
        payload = {
            "value1": "Swimming course available",
            "value2": f"Swimming course '{course.name}' is available!",
            "value3": course.url,
        }
        response = requests.post(
            f"https://maker.ifttt.com/trigger/hhpl/with/key/{self.key}", json=payload
        )
