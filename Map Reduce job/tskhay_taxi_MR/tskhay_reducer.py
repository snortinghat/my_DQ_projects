#!/usr/bin/env python
"""reducer.py"""

import sys

trip_types_dict = {
    '': 'Undefined',
    '1': 'Credit card',
    '2': 'Cash',
    '3': 'No charge',
    '4': 'Dispute',
    '5': 'Unknown',
    '6': 'Voided trip'
}

def perform_reduce():
    current_key = None
    tips_sum = 0
    trip_count = 0
    print('Payment Type,Month,Tips average amount')

    for line in sys.stdin:
        line = line.strip()
        key, trip_tips = line.split('\t')

        try:
            trip_tips = float(trip_tips)
        except ValueError:
            continue

        if key == current_key:
            tips_sum += trip_tips
            trip_count += 1
        else:
            if current_key:
                try:
                    tips_avg = round((tips_sum / trip_count),2)
                except:
                    tips_avg = 'Undefined'

                trip_type_code = current_key[7:]
                trip_type_text = trip_types_dict[trip_type_code]
                trip_date = current_key[:7]
                print('%s,%s,%s' % (trip_type_text, trip_date[:7], tips_avg))

            current_key = key
            tips_sum = trip_tips
            trip_count = 1
    try:
        tips_avg = round((tips_sum / trip_count),2)
    except:
        tips_avg = 'Undefined'

    trip_type_code = current_key[7:]
    trip_type_text = trip_types_dict[trip_type_code]
    trip_date = current_key[:7]
    print('%s,%s,%s' % (trip_type_text, trip_date[:7], tips_avg))


if __name__ == '__main__':
    perform_reduce()
