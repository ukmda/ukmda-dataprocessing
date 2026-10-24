# Copyright (C) 2018-2023 Mark McIntyre
#
# script to get next batch start time in a format compatible with at
#

import datetime
import sys
from crontab import CronTab
import argparse

from utils.getRiseSet import getNextRiseSet

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='Update the overnight batch start time to adjust for the changing time of dawn.')
    arg_parser.add_argument('offset', metavar='OFFSET', type=int, help='offset to apply', default=90)
    arg_parser.add_argument('-b', '--batchscript', metavar='BATCHSCRIPT', type=str, help='batch script to alter')
    cml_args = arg_parser.parse_args()


    offset = int(cml_args.offset)
    batchname = 'nightlyJob'
    if cml_args.batchscript:
        batchname = cml_args.batchscript

    dawn, dusk = getNextRiseSet(51.88, -1.31, 80) 

    starttime = dawn + datetime.timedelta(minutes=offset)
    print(f'Setting batch start time for {batchname} to', starttime.strftime('%H:%M'))

    cron = CronTab(user=True)
    iter=cron.find_command(batchname)
    for i in iter:
        if i.is_enabled():
            i.hour.on(starttime.hour)
            i.minute.on(starttime.minute)
    cron.write()
