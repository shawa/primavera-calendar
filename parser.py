#!/usr/bin/env python3

from itertools import islice, chain
from collections import namedtuple

from bs4 import BeautifulSoup
from titlecase import titlecase
import clize


def middle(lst):
    return lst[1:-1]


def has_children(soup):
    return len(list(soup.children)) > 0


def text_content(soup):
    return soup.get_text().strip()


def parse_cell(cell):
    if not has_children(cell):
        return None

    time_description = text_content(cell.find('div', {'class': 'hora'}))
    start, end = time_description.replace('(', '').replace(')', '').split(' - ')
    artist = text_content(cell.find('div', {'class': 'artists_2017'}))

    return start, end, artist


def parse_row(stages, row):
    cells = middle(row.find_all('td'))
    for i, cell in enumerate(cells):
        parsed = parse_cell(cell)
        if parsed is None:
            continue

        start, end, raw_artist =  parsed
        stage = stages[i]
        artist = titlecase(raw_artist)
        yield stage, start, end, artist


def parse_table(table):
    areas_head, stages_head = table.find_all('thead')
    stages = [text_content(stage) for stage in middle(stages_head.find_all('th'))]
    body = table.find('tbody')
    rows = body.find_all('tr')[:-1]
    parsed_cells = (parse_row(stages, row) for row in rows)
    return chain(*parsed_cells)


def parse(content):
    soup = BeautifulSoup(content, 'html.parser')

    table = soup.find('table', {'id': 'listaHorarios'})
    date = text_content(soup.find('div', {'id': 'title_dias'}).find('span', {'class': 'rojo'}))

    return date, parse_table(table)
