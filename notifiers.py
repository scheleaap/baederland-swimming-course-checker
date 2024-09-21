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


class PushoverNotifier(Notifier):
    def __init__(self, app_token: str, user_key: str) -> None:
        self.app_token = app_token
        self.user_key = user_key

    def courses_available(self, courses: list[Course]):
        logger = logging.getLogger("blscc.notifiers")

        course_names = {c.name for c in courses}
        message = (
            f"Swimming course '{next(iter(course_names))}' is available. Go get it now!"
            if len(course_names) == 1
            else f"{len(courses)} swimming courses are available. Go get one now!"
        ) + f"\n\n{courses[0].search_url}"
        payload = {
            "token": self.app_token,
            "user": self.user_key,
            "title": "Swimming courses available",
            "message": message,
        }
        logger.debug(f"Calling Pushover with payload {payload}")
        response = requests.post(
            f"https://api.pushover.net/1/messages.json", data=payload
        )
        response.raise_for_status()
