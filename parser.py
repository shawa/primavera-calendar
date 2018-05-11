#!/usr/bin/env python3

import re
from itertools import islice, chain
from collections import namedtuple

import clize
from urllib.parse import urlparse, parse_qsl
from bs4 import BeautifulSoup
from titlecase import titlecase

TIME_RE = re.compile(r'\((\d{2}:\d{2}) - (\d{2}:\d{2})\)')


def middle(lst):
    return lst[1:-1]


def has_children(soup):
    return len(list(soup.children)) > 0


def text(soup):
    return soup.get_text().strip()


def parse_artist_info(artist_info):
    soup = BeautifulSoup(artist_info, 'html.parser')
    subtitle = text(soup.select_one('h4.font01'))
    info = text(soup.select_one('div.artist-desc'))
    return subtitle, info


def parse_cell(cell):
    if not has_children(cell):
        return None

    time_string = text(cell.select_one('div.hora'))
    start, end = TIME_RE.match(time_string).groups()
    artist = text(cell.select_one('div.artists_2017'))

    return start, end, artist


def parse_row(stages, row, include_artist_info=True):
    cells = middle(row.select('td'))
    for i, cell in enumerate(cells):
        parsed = parse_cell(cell)
        if parsed is None:
            continue

        start, end, raw_artist = parsed
        stage = stages[i]
        artist = titlecase(raw_artist)

        href = cell.select_one('a.artistaAnchor')['href']
        artist_id = dict(parse_qsl(urlparse(href).query))['id']

        yield stage, start, end, artist, artist_id


def parse_table(table):
    _areas_head, stages_head = table.select('thead')
    stages = [text(stage) for stage in middle(stages_head.select('th'))]
    body = table.select_one('tbody')
    rows = body.select('tr')[:-1]
    parsed_cells = (parse_row(stages, row) for row in rows)
    return chain(*parsed_cells)


def parse_timetable(content):
    soup = BeautifulSoup(content, 'html.parser')

    table = soup.select_one('table#listaHorarios')
    date = text(soup.select_one('div#title_dias > span.rojo'))
    return date, parse_table(table)
