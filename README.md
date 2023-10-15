# Bäderland Swimming Course Checker

The BLSCC notifies you through [IFTTT](https://ifttt.com/) when a swimming course is available at Hamburg's
[Bäderland](https://www.baederland.de/) swimming pools.

## Usage

First, set up an IFTTT [webhook](https://ifttt.com/maker_webhooks) named `hhpl` and copy the key.

```sh
$ ./notify_course_availability.sh --ifttt_key=<key> ...
```

## Technical Details

The tool uses [Scrapy](https://scrapy.org/) to parse HTML.
