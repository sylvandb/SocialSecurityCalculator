#!/usr/bin/env python3

import sys
import time

INCOME = 35000
GROWTH = 1.03
year = time.localtime().tm_year


EarningsRecord = {}

def calc_earnings():
    income = INCOME
    for y in range(year - 32, year):
        EarningsRecord[y] = income
        income *= GROWTH



if __name__ == '__main__':
    verbose = 0
    try:
        verbose = sys.argv.index('--verbose')
        del sys.argv[verbose]
    except ValueError:
        pass
    try:
        verbose = sys.argv.index('-v')
        del sys.argv[verbose]
    except ValueError:
        pass
    try:
        INCOME = int(sys.argv[1])
        GROWTH = float(sys.argv[2])
        year = int(sys.argv[3])
    except (IndexError, TypeError):
        pass
    calc_earnings()
    ymin = min(EarningsRecord)
    ymax = max(EarningsRecord)
    emin = EarningsRecord[ymin]
    emax = EarningsRecord[ymax]
    esum = sum(v for v in EarningsRecord.values())
    if verbose:
        print('<oss:EarningsRecord>')
        for year, earn in EarningsRecord.items():
            print(f'  <osss:Earnings startYear="{year}" endYear="{year}">')
            print(f'    <osss:FicaEarnings>{earn}</osss:FicaEarnings>')
            print(f'    <osss:MedicareEarnings>{earn}</osss:MedicareEarnings>')
            print(f'  </osss:Earnings>')
        print('</oss:EarningsRecord>')
    else:
        print(f'{len(EarningsRecord)} years\n  min: {ymin} = ${emin}\n  max: {ymax} = ${emax}\n  total: ${esum}')
