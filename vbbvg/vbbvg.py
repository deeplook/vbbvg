#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Get next real-time departure times for VBB/BVG public transport lines. 

Please read the file README.rst for more information.
"""

from __future__ import division, print_function

import re
import sys
import datetime
import argparse
import six.moves.urllib as urllib
import subprocess
import os
from os.path import dirname, join

import termcolor
import pandas as pd
from tabulate import tabulate


# The BVG online service wrapped by this tool:
BVG_URL_BASE = u'http://mobil.bvg.de'
BVG_URL_PATH = u'/Fahrinfo/bin/stboard.bin/dox'
BVG_URL_QUERY = u'?input=%s&start=Suchen&boardType=depRT'
BVG_URL_PAT = BVG_URL_BASE + BVG_URL_PATH + BVG_URL_QUERY

# Data taken from http://daten.berlin.de/kategorie/verkehr (CC-BY 3.0):
STOPS_PATH = join(dirname(__file__), 'vbbvg_stops.csv')


def load_data(verbose=False):
    "Load all VBB stop names and IDs into a Pandas dataframe."

    df = pd.read_csv(STOPS_PATH, usecols=['stop_id', 'stop_name'])
    if verbose:
        print('- Loaded %d entries from "%s".' % (len(df), STOPS_PATH))
    return df


def filter_data(df, filter_name, verbose=False):
    "Filter certain entries with given name."

    # pick only entries ending with 'Berlin' in column stop_name, incl. '(Berlin)' 
    # df = df[df.stop_name.apply(lambda cell: 'Berlin' in cell)]
    df = df[df.stop_name.apply(
        lambda cell: filter_name.encode('utf-8') in cell)]

    # remove ' (Berlin)' in column stop_name
    # df.stop_name = df.stop_name.apply(lambda cell: re.sub(' \(Berlin\)', '', cell))

    # remove initial 'S' and 'U' and 'S+U' in column stop_name
    # this creates a warning!
    # df.stop_name = df.stop_name.apply(lambda cell: re.sub('^([S\+U]+) +(.*)', lambda m: m.groups()[1], cell))

    if verbose:
        msg = '- Filtered down to %d entries containing "%s".'
        print(msg % (len(df), filter_name))

    return df


# The following function is not tested in test.py.

def get_name_id_interactive(stop, df):
    """
    Return VBB/BVG ID for given stop name in given table.

    Enter interactive dialog when result is not unique.
    """

    # this is very fast, but searching in a list of ca. 2900 tuples might be also
    # fast enough, and that would mean removing some repeated preprocessing...

    # pick only entries containing the given stop substring in column stop_name
    df1 = df[df.stop_name.apply(lambda cell: stop.lower() in cell.lower())]
    df1 = df1.sort_values(by=['stop_name'])
    df1_len = len(df1)
    if df1_len == 1:
        result = {
            'stop_id': df1.iloc[0].stop_id,
            'stop_name': df1.iloc[0].stop_name
        }
        return result
    elif df1_len > 1:
        msg = 'Please pick one of the following matching stop names:'
        termcolor.cprint(msg, attrs=['bold'])
        fmt = '%%%dd. %%s' % len(str(df1_len))
        for i, (index, _id, stop_name) in enumerate(df1.itertuples()):
            print(fmt % (i, stop_name))

        try:
            msg = 'Please select index of desired stop '\
                  'in list above (0-%d): ' % (df1_len - 1)
            msg = termcolor.colored(msg, attrs=['bold'])
            result = raw_input(msg)
        except KeyboardInterrupt:
            print('')
            return

        try:
            i = int(result)
        except ValueError:
            msg = "'%s' is not an integer number." % result
            termcolor.cprint(msg, 'red', attrs=['bold'])
            return

        if not 0 <= i <= df1_len - 1:
            msg = 'Invalid index.'
            termcolor.cprint(msg, 'red', attrs=['bold'])
            return

        result = {
            'stop_id': df1.iloc[i].stop_id,
            'stop_name': df1.iloc[i].stop_name
        }
        return result


def wait_time(departure, now=None):
    """
    Calculate waiting time until the next departure time in 'HH:MM' format.

    Return time-delta (as 'MM:SS') from now until next departure time in the 
    future ('HH:MM') given as (year, month, day, hour, minute, seconds). 
    Time-deltas shorter than 60 seconds are reduced to 0.
    """

    now = now or datetime.datetime.now()
    yn, mn, dn = now.year, now.month, now.day
    hour, minute = map(int, departure.split(':'))
    dt = datetime.datetime(yn, mn, dn, hour=hour, minute=minute)
    delta = (dt - now).seconds
    if (dt - now).days < 0:
        delta = 0
    if delta < 3600:
        return '%02d:%02d' % (delta // 60, delta % 60)
    else:
        delta_hh = delta // 3600
        delta_rest = delta - delta_hh * 3600
        return '%02d:%02d:%02d' % (delta_hh, delta_rest // 60, delta_rest % 60)


def get_next_departures(stop, filter_line=None, num_line_groups=1, verbose=False):
    """
    Get all real-time departure times for given stop and return as filtered table.

    Terminate if we can assume there is no connection to the internet. 
    """

    # Get departures table from online service
    # (great: we don't have to iterate over multiple pages).

    url = BVG_URL_PAT % stop
    if verbose:
        print('- Fetching table for URL "%s".' % url)
    try:
        tables = pd.read_html(url.encode('utf-8'))
    except urllib.error.URLError:
        msg = 'Not connected to the internet?'
        termcolor.cprint(msg, 'red', attrs=['bold'])
        sys.exit(1)
    except ValueError:
        return []
    table = tables[0]
    table.columns = ['Departure', 'Line', 'Destination']

    if verbose:
        print('- Got table with %d entries for "%s".' % (len(table), stop))

    # Cleanup

    # Drop entries with '*' in column Departure...
    # (causes trouble when resulting in an empty table!)
    # table = table[table.Departure.apply(lambda row: " *" not in row)]
    # So, instead remove '*' in column Departure...
    table.is_copy = False # prevents SettingWithCopyWarning
    table.Departure = table.apply(
        lambda row: re.sub('\s*\*\s*', '', row.Departure), axis=1)

    # Replace regex ' +' with ' ' in column Line...
    table.Line = table.apply(lambda row: re.sub(' +', ' ', row.Line), axis=1)

    # Filter desired number of unique combinations of Line and Destination column.
    indices = []
    for i in range(num_line_groups):
        try:
            indices += sorted([tab.index.values[i] 
                for line_dest, tab in table.groupby(['Line', 'Destination'])])
        except IndexError:
            break
    table = table[table.index.map(lambda x: x in indices)]

    # Insert a left-most column with minutes and seconds from now 
    # until the departure time.
    table.insert(0, "Wait", table.Departure.apply(lambda dep: wait_time(dep)))

    # Filter on desired lines only
    if filter_line:
        table = table[table.Line.apply(
            lambda cell: filter_line.lower().encode('utf-8') in cell.lower())]

    return table


# The following function is not tested in test.py.

def show_header(**header):
    "Display a HTTP-style header on the command-line."

    print('%s: %s' % ('Now', header['now']))
    print('%s: %s' % ('Stop-Name', header['name']))
    print('%s: %s' % ('Stop-ID', header.get('id', None)))
    print('')


# The following function is not tested in test.py.

def show_table(args):
    "Output table on standard out."

    df = load_data(verbose=args.verbose)
    df = filter_data(df, filter_name=args.filter_name, verbose=args.verbose)

    stop = re.sub(' +', ' ', args.stop)
    if re.match('^\d+$', stop.decode('utf-8')):
        _id = stop
        name = df[df.stop_id==int(_id)].stop_name.item()
    else:
        result = get_name_id_interactive(stop, df)
        if not result:
            return
        name, _id = result['stop_name'], result['stop_id']

    now = datetime.datetime.now().strftime('%H:%M:%S')
    tab = get_next_departures(_id, filter_line=args.filter_line, 
        num_line_groups=args.num_line_groups, verbose=args.verbose)

    if args.header:
        show_header(now=now, name=name, id=_id)
    if len(tab) > 0:
        tabl = [row[1:]for row in tab.itertuples()]
        print(tabulate(tabl, headers=list(tab.columns),
            tablefmt=args.tablefmt))
    else:
        print('No departures found.')


# The following function is not tested in test.py.

def test_stop(stop_name):
    """Run a series of tests on the command-line for the given stop name."""

    # Make sure we don't have more than one consecutive blank in the stop name.
    stop_name = re.sub(' +', ' ', stop_name)

    # Use '  ' in strings below to allow single blanks in stop names.
    examples = '''
        --help
        --stop  %(stop_name)s
        --stop  %(stop_name)s  --header
        --stop  %(stop_name)s  --tablefmt  rst
        --stop  %(stop_name)s  --num-line-groups  2
        --stop  %(stop_name)s  --num-line-groups  2  --filter-line  U
    '''  % {'stop_name': stop_name.encode('utf-8')}
    # --stop Bahnhof --header --filter-name "(Potsdam)" # fails
    examples = examples.strip().split('\n')

    for example in examples:
        prog = join(os.getcwd(), sys.argv[0])
        cmd = '%s  %s  %s' % (sys.executable, prog, example.strip())
        termcolor.cprint(cmd, attrs=['bold']) ## todo: 
        print('')
        subprocess.check_call(cmd.decode('utf-8').split('  '))
        print('')
