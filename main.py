#!/usr/bin/env python3

from notifiers import IftttNotifier, StdoutNotifier
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
    parser.add_argument("--category", type=int, required=True, help="The category number of the course")
    parser.add_argument("-w", "--weekday", type=int,action="append", required=True, help="The weekday of the course (Sunday = 0)")
    parser.add_argument("--ifttt_key", help="The IFTTT key")
    parser.add_argument("-c", "--console", action='store_true', help="Notify on the console in addition to IFTTT")

    args = parser.parse_args(raw_args)

    return args


def main(args):
    notifiers = [
        IftttNotifier(key=args.ifttt_key),
    ]
    if args.console:
        notifiers.append(StdoutNotifier())

    logging.info(f"Searching for courses in category {args.category} on weekdays {args.weekday}")

    process = CrawlerProcess(
        settings={
            "BOT_NAME": "Baederland Swimming Courses",
            "ITEM_PIPELINES": {
                "pipelines.InMemoryCollectorPipeline": 1,
            },
            "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7",
            "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
            "FEED_EXPORT_ENCODING": "utf-8",
            "COURSE_CATEGORY": args.category
        }
    )
    logging.getLogger("scrapy").setLevel(logging.WARNING)
    process.crawl(CourseSpider)
    process.start()

    courses = pipelines.COLLECTED_COURSES
    logging.debug(f"Found {len(courses)} courses (unfiltered)")
    # for c in courses:
    #     print(c)
    matched_courses = [c for c in courses if c.weekday in args.weekday and c.available_slots > 0]
    logging.debug(f"Matched {len(matched_courses)} courses")

    for course in matched_courses:
        for notifier in notifiers:
            notifier.course_is_available(course)


def setup_logging(level):
    logging.basicConfig(level=level, format="%(message)s")
    logging.getLogger("asyncio").setLevel(logging.WARNING)


if __name__ == "__main__":
    setup_logging(logging.INFO)
    main(parse_arguments(sys.argv[1:]))
