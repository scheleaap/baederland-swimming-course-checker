#!/usr/bin/env python3

from notifiers import PushoverNotifier, StdoutNotifier
import argparse
import logging
import sys
from scrapy.crawler import CrawlerProcess

import pipelines
from spiders import CourseSpider


def parse_arguments(raw_args):
    parser = argparse.ArgumentParser(
        description="Notifies that a swimming course is available.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--search-url", type=str, help="The URL of the initial search",
                        default="https://www.baederland.de/kurse/kursfinder/?course%5Blocation%5D=&course%5Blatlng%5D=&course%5Bpool%5D%5B%5D=43&course%5Bpool%5D%5B%5D=12&course%5Bpool%5D%5B%5D=23&course%5Bpool%5D%5B%5D=35&course%5Bpool%5D%5B%5D=10&course%5Bpool%5D%5B%5D=17&course%5Bpool%5D%5B%5D=28&course%5Bpool%5D%5B%5D=26&course%5Bpool%5D%5B%5D=36&course%5Bpool%5D%5B%5D=33&course%5Bpool%5D%5B%5D=5&course%5Bpool%5D%5B%5D=18&course%5Bpool%5D%5B%5D=14&course%5Bpool%5D%5B%5D=13&course%5Bpool%5D%5B%5D=9&course%5Bpool%5D%5B%5D=5&course%5Bpool%5D%5B%5D=14&course%5Bpool%5D%5B%5D=26&course%5Bcategory%5D%5B%5D=55&course%5Bdate%5D=04.12.2024&course%5Bweekday%5D%5B%5D=1&course%5Bweekday%5D%5B%5D=2&course%5Bweekday%5D%5B%5D=4&course%5Bweekday%5D%5B%5D=5&course%5Bweekday%5D%5B%5D=6")
    parser.add_argument("--log-all", action='store_true', help="Log all (i.e. also non matching courses)")
    parser.add_argument("--console", action=argparse.BooleanOptionalAction, default=False, help="Notify on the console (default: false)")
    parser.add_argument("--pushover", action=argparse.BooleanOptionalAction, default=True, help="Notify to Pushover (default: true)")
    parser.add_argument("--pushover-app-token", help="The Pushover app token")
    parser.add_argument("--pushover-user-key", help="The Pushover user key")
    parser.add_argument("-q", "--quiet", action='store_true', help="Suppress all regular output (default: false)")

    args = parser.parse_args(raw_args)

    return args


def main(args):
    log_level = logging.WARNING if args.quiet else logging.INFO

    logger = logging.getLogger("blscc.main")
    logger.setLevel(log_level)

    notifiers = []
    if args.console:
        notifiers.append(StdoutNotifier())
    if args.pushover:
        if args.pushover_app_token is None or args.pushover_user_key is None:
            logger.error("Please specify both the Pushover app token and user key")
            sys.exit(1)
        notifiers.append(PushoverNotifier(app_token=args.pushover_app_token, user_key=args.pushover_user_key))

    logger.info(f"Searching for courses, starting from URL {args.search_url}")

    process = CrawlerProcess(
        settings={
            "BOT_NAME": "Baederland Swimming Courses",
            "LOG_LEVEL": log_level,
            "ITEM_PIPELINES": {
                "pipelines.InMemoryCollectorPipeline": 1,
            },
            "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7",
            "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
            "FEED_EXPORT_ENCODING": "utf-8",
            "SEARCH_URL": args.search_url
        }
    )
    logging.getLogger("scrapy").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    process.crawl(CourseSpider)
    process.start()

    courses = pipelines.COLLECTED_COURSES
    logger.debug(f"Found {len(courses)} courses (unfiltered)")
    if args.log_all:
        for c in courses:
            logger.debug(f"Found course: {c}")
    matched_courses = [c for c in courses if c.available_slots > 0]
    logger.debug(f"Matched {len(matched_courses)} courses")

    if matched_courses:
        for notifier in notifiers:
            notifier.courses_available(matched_courses)


if __name__ == "__main__":
    main(parse_arguments(sys.argv[1:]))
