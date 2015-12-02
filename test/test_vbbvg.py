#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Run with 'py.test test.py'

Note that returned tables are Pandas DataFrame objects.
"""

import datetime

import pytest

import vbbvg


def test0():
    "Load all available stop/id data and apply some filters."

    df = vbbvg.load_data()
    assert len(df) == 13199

    df = vbbvg.filter_data(df, filter_name='(Berlin)')
    assert len(df) == 2925


def test1():
    "Get table with departures for a specific stop."

    table = vbbvg.get_next_departures(u'bundesplatz')
    assert len(table) > 5
    assert u'Ringbahn S 42' in table.Destination.values
    assert u'Ringbahn S 41' in table.Destination.values


def test2():
    "Compare tables received for stop name and ID given for the same stop."

    table1 = vbbvg.get_next_departures(u'möckernbrücke')
    table2 = vbbvg.get_next_departures(u'9017104')
    assert set(table1.Destination.values) == set(table2.Destination.values)


def test3():
    "Calculate time to wait between now and some later departure time."

    delta_secs = 10
    now = datetime.datetime(2012, 1, 1, 18, 0, 0)
    dep = datetime.datetime(2012, 1, 1, 18, 0, delta_secs)
    wait = vbbvg.wait_time(dep.strftime('%H:%M'), now=now)
    assert wait == '00:00'


def test4():
    "Calculate time to wait between now and some later departure time."

    now = datetime.datetime(2012, 1, 1, 18, 0, 0)
    dep = datetime.datetime(2012, 1, 1, 18, 2, 0)
    wait = vbbvg.wait_time(dep.strftime('%H:%M'), now=now)
    assert wait == '02:00'


def test5():
    "Calculate time to wait between now and some later departure time."

    now = datetime.datetime(2012, 1, 1, 18, 30, 30)
    dep = datetime.datetime(2012, 1, 1, 18, 45, 0)
    wait = vbbvg.wait_time(dep.strftime('%H:%M'), now=now)
    assert wait == '14:30'

def test6():
    "Calculate time to wait between now and some later departure time."

    now = datetime.datetime(2012, 1, 1, 18, 30, 30)
    dep = datetime.datetime(2012, 1, 1, 19, 45, 0)
    wait = vbbvg.wait_time(dep.strftime('%H:%M'), now=now)
    assert wait == '01:14:30'


def test7():
    "Test filtering on lines."

    pass


def _test_create_examples():
    "Test creating examples."

    # fails because sys.argv[0] is /opt/bin/py.test ...
    vbbvg.run_examples(u'Bundesplatz')
