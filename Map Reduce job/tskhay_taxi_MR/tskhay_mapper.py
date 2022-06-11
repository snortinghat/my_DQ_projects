#!/usr/bin/env python
"""mapper.py"""

import sys


def perform_map():
    for line in sys.stdin:
        line = line.strip()
        all_values = line.split(',')

        date_extended = all_values[1]
        date = date_extended[:7]
        payment_type = all_values[9]
        trip_tips = all_values[13]
        if date[:4] == '2020':
            print('%s%s\t%s' % (date, payment_type, trip_tips))


if __name__ == '__main__':
    perform_map()
