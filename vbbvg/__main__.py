#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CLI Entry point for the program.
"""

import argparse

import termcolor

import vbbvg


def main():
    desc = 'Show current real-time VBB/BVG departure times for some given stop.'
    p = argparse.ArgumentParser(description=desc)

    p.add_argument('--verbose',
        help='Display various additional information...', 
        action=u'store_true')

    p.add_argument('--header',
        help='Display additional header with current time, stop name and ID.', 
        action=u'store_true')

    p.add_argument('--test',
        help='Run some test usage examples for the stop given with --stop. '
             'All other options will be ignored.',
        action=u'store_true')

    name_filter_default = u'(Berlin)'
    p.add_argument('--filter-name', metavar='EXPR', 
        help='Expression for filtering desired stop names only '
             '(default: "%s").' % name_filter_default.encode('utf-8'),
        default=name_filter_default.encode('utf-8'))

    line_filter_default = u''
    p.add_argument('--filter-line', metavar='EXPR', 
        help='Expression for filtering desired lines only '
             '(default: "%s").' % line_filter_default.encode('utf-8'),
        default=line_filter_default.encode('utf-8'))

    num_line_groups_default = 1
    p.add_argument('--num-line-groups', metavar='NUMBER', type=int,
        help='Number of shown line groups containing all different '
             'combinatinos of (Line/Destination).'
             '(default: %d).' % num_line_groups_default,
        default=num_line_groups_default)

    p.add_argument('--stop', metavar='NAME_ID', 
        help='Stop name or ID (recommended), e.g. "Möckernbrücke" or "9017104". '
             'If not given, an interactive dialog asking for a stop name or ID '
             'will be started on the command-line.',
        default=u''.encode('utf-8'))

    tablefmt_default = u'simple'
    p.add_argument('--tablefmt', metavar='NAME', 
        help='Table format, e.g. "rst", "html" and many more (see tabulate -h), '
             'default: "%s".' % tablefmt_default.encode('utf-8'), 
        default=tablefmt_default.encode('utf-8'))

    args = p.parse_args()
    if args.test:
        if args.stop:
            vbbvg.test_stop(args.stop.decode('utf-8')) # test without decode
        else:
            msg = 'No stop provided with --stop.'
            termcolor.cprint(msg, 'red', attrs=['bold'])
    else:
        vbbvg.show_table(args)

if __name__ == '__main__':
    main()
