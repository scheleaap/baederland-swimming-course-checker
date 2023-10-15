# Bäderland Swimming Course Checker

The BLSCC notifies you through [IFTTT](https://ifttt.com/) when a swimming course is available at Hamburg's [Bäderland Hamburg](https://www.baederland.de/).

## Usage

First, set up an IFTTT [webhook](https://ifttt.com/maker_webhooks) named `hhpl` and copy the key.

```sh
$ ./notify_course_availability.sh --ifttt_key=<key> ...
```

## Technical Details

The tool parses HTML :-(.
