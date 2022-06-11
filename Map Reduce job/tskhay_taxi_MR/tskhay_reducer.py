#!/usr/bin/env python
"""reducer.py"""

import sys

def type_expander(type_char):
    if type_char == '':
        return 'Undefined'
    elif type_char == '1':
        return 'Credit card'
    elif type_char == '2':
        return 'Cash'
    elif type_char == '3':
        return 'No charge'
    elif type_char == '4':
        return 'Dispute'
    elif type_char == '5':
        return 'Unknown'
    elif type_char == '6':
        return 'Voided trip'
    else:
        return 'Other'


def perform_reduce():
    current_date_type = None
    tips_sum = 0
    trip_count = 0
    print('Payment Type,Month,Tips average amount')
    for line in sys.stdin:
        line = line.strip()
        date_type, trip_tips = line.split('\t')

        try:
            trip_tips = float(trip_tips)
        except ValueError:
            continue

        if date_type == current_date_type:
            tips_sum += trip_tips
            trip_count += 1
        else:
            if current_date_type:
                try:
                    tips_avg = round((tips_sum / trip_count),2)
                except:
                    tips_avg = 'Undefined'

                type_char = current_date_type[7:]
                type_text = type_expander(type_char)

                print('%s,%s,%s' % (type_text, current_date_type[:7], tips_avg))
            current_date_type = date_type
            tips_sum = trip_tips
            trip_count = 1
    try:
        tips_avg = round((tips_sum / trip_count),2)
    except:
        tips_avg = 'Undefined'
    type_char = current_date_type[7:]
    type_text = type_expander(type_char)
    print('%s,%s,%s' % (type_text, current_date_type[:7], tips_avg))


if __name__ == '__main__':
    perform_reduce()
