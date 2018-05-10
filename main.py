#!/usr/bin/env python3

import logging
import sys
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format='%(message)s')

import arrow
import clize
import requests
import requests_cache

from ics import Calendar, Event

requests_cache.install_cache('requests_cache', expire_after=(60 * 60 * 24))

from tabulate import tabulate
from parser import parse

def to_arrow(date, time):
    hours, minutes = (int(x) for x in time.split(':'))

    time_arrow = arrow.get(date).replace(hours=hours, minutes=minutes, tzinfo=('UTC+2'))

    # no events start before 11, if it's earlier than that
    # then this event is 'actually' on the next day (way past bedtime!)
    if hours < 11:
        return time_arrow.replace(days=1)
    else:
        return time_arrow

def to_ics_event(date, act):
    stage, start_time, end_time, artist = act

    begin = to_arrow(date, start_time)
    end = to_arrow(date, end_time)

    logging.info('parsed act: %s, %s, %s-%s', stage, artist, begin.format('HH:mm'), end.format('HH:mm'))
    return Event(name=artist, location=stage, begin=begin, end=end)


def get_events(date, acts):
    for act in acts:
        yield to_ics_event(date, act)


def scrape_all_acts():
    days = range(1, 8)
    url = 'https://www.primaverasound.es/horarios'

    def page_contents():
        for day in days:
            logging.info('fetching day %d of %d', day, days[-1])
            yield requests.get(url, params={'d': day}).content.decode()

    # 7 day festival, yo
    for page_content in page_contents():
        date, acts = parse(page_content)
        yield from get_events(date, acts)


def main(outfile='primavera-2018.ics'):
    events = scrape_all_acts()

    logging.info('writing new calendar file to %s', outfile)
    calendar = Calendar(events=events)

    with open(outfile, 'w') as f:
        f.writelines(calendar)

    logging.info('enjoy the festival!')
    return

if __name__ == '__main__':
    clize.run(main)
