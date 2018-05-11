#!/usr/bin/env python3

import logging
import sys
logging.basicConfig(
    stream=sys.stdout, level=logging.DEBUG, format='%(message)s')

import arrow
import clize
import requests
import requests_cache

from ics import Calendar, Event

requests_cache.install_cache('requests_cache', expire_after=(60 * 60 * 24))

from tabulate import tabulate

from parser import parse_timetable, parse_artist_info


def to_arrow(date, time):
    hours, minutes = (int(x) for x in time.split(':'))

    time_arrow = arrow.get(date).replace(
        hours=hours, minutes=minutes, tzinfo=('UTC+2'))

    # no events start before 11, if it's earlier than that
    # then this event is 'actually' on the next day (way past bedtime!)
    if hours < 11:
        return time_arrow.replace(days=1)
    else:
        return time_arrow


def to_ics_event(date, act, include_artist_info):
    stage, start_time, end_time, artist, artist_id = act

    begin = to_arrow(date, start_time)
    end = to_arrow(date, end_time)

    logging.info('parsed act: %s, %s, %s-%s', stage, artist,
                 begin.format('HH:mm'), end.format('HH:mm'))

    description = None
    if include_artist_info:
        logging.info('fetching artist info for %s (%s)', artist, artist_id)
        subtitle, info = scrape_artist_info_page(artist_id)
        description = '{}\n\n{}'.format(subtitle, info) if subtitle else info

    return Event(
        name=artist,
        location=stage,
        begin=begin,
        end=end,
        description=description)


def scrape_artist_info_page(artist_id):
    url = 'https://lineup.primaverasound.es/2018_artists'
    params = {'id': artist_id, 'lang': 'en'}
    page_content = requests.get(url, params=params).content.decode()
    return parse_artist_info(page_content)


def scrape_all_acts(include_artist_info):
    # 7 day festival, yo
    url = 'https://www.primaverasound.es/horarios'

    def get_all_timetables():
        days = range(1, 8)
        for day in days:
            logging.info('fetching day %d of %d', day, days[-1])
            params = {
                'd': day,
                'lang': 'en',
            }

            yield requests.get(url, params=params).content.decode()

    for page_content in get_all_timetables():
        date, acts = parse_timetable(page_content)

        for act in acts:
            yield to_ics_event(date, act, include_artist_info)


def main(outfile='primavera-2018.ics', include_artist_info=True):
    '''Scrape the Primavera website for act times and build an ICS file of the
    result.

    outfile: destination

    include_artist_info: whether or not to also scrape individual artist pages for descriptions (much slower!)
    '''
    events = scrape_all_acts(include_artist_info)

    logging.info('writing new calendar file to %s', outfile)
    calendar = Calendar(events=events)

    with open(outfile, 'w') as f:
        f.writelines(calendar)

    logging.info('enjoy the festival!')
    return


if __name__ == '__main__':
    clize.run(main)
