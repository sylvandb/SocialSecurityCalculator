#!/usr/bin/env python3
#
# This Python script will calculate your expected retirement benefits
# from Social Security given your annual earnings. This script does
# not extrapolate potential future earnings. It only uses the income
# information provided into the EarningsRecord dictionary below.
#
# Inputs:
#           1) EarningsRecord -
#               Will attempt to read file: Your_Social_Security_Statement_Data.xml
#               Dictionary mapping a year to the amount of Social
#               Security eligible earnings in that particular year
#
#           2) NationalAverageWageIndexSeries -
#               Data pulled directly from the Social Security website for the
#               national average wage data
#
#
# Written by Ryan Antkowiak (antkowiak@gmail.com) 2017-07-15
# Copyright (c) 2017 All Rights Reserved
#

# Import modules
from datetime import datetime
from math import floor
import xml.etree.ElementTree as et
import sys

# filename on cmdline or the default
SOC_SEC_XML = sys.argv[1] if sys.argv[1:] else "Your_Social_Security_Statement_Data.xml"


# ??? delay load_xml_statement and the calculations???
def get_results():
    if xml_statement_error:
        raise IndexError(xml_statement_error)
    return Results


def format_results(results, max_increase=3):
    lines = []
    lines.append("Earnings record years analyzed ____________ {}".format(len(results['EarningsRecord'])))
    lines.append("Earning Years with 0 Earnings _____________ {}".format(', '.join(results['MissingEarningYears'])))
    lines.append("Total Actual Earnings in all Years ________{:11.2f}".format(results['TotalActualEarnings']))
    lines.append("Total Adjusted Earnings in all Years ______{:11.2f}".format(results['TotalAdjustedEarnings']))
    lines.append("Discarded Adjusted Earnings _______________{:11.2f}".format(results['TotalAdjustedEarnings'] - results['Top35YearsEarnings']))
    lines.append("Top 35 Years of Adjusted Earnings _________{:11.2f}".format(results['Top35YearsEarnings']))
    lines.append("Average Indexed Monthly Earnings (AIME) ___{:11.2f}".format(results['AverageIndexedMonthlyEarnings']))
    lines.append("First Bend Point __________________________{:11.2f}".format(results['FirstBendPoint']))
    lines.append("Second Bend Point _________________________{:11.2f}".format(results['SecondBendPoint']))
    lines.append("Reduced (70%) Monthly Benefit _____________{:11.2f}".format(results['ReducedBenefit']))
    lines.append("Reduced (70%) Annual Benefit ______________{:11.2f}".format(results['ReducedBenefit'] * 12.0))
    lines.append("Normal Monthly Benefit ____________________{:11.2f}".format(results['NormalBenefit']))
    lines.append("Normal Annual Benefit _____________________{:11.2f}".format(results['NormalBenefit'] * 12.0))
    try:
        for yr in range(max_increase):
            lines.append("Increased Monthly Benefit FRA+{} ___________{:11.2f}".format(yr + 1, results['IncreasedBenefit'][yr]))
            lines.append("Increased Annual Benefit FRA+{} ____________{:11.2f}".format(yr + 1, results['IncreasedBenefit'][yr] * 12.0))
    except IndexError:
        pass
    return lines


# Earnings history by year.
# You can find out the information by logging into "my Social Security" at
# https://www.ssa.gov
# and navigating to your earnings record at
# https://secure.ssa.gov/OSSS/er/er001View.do
# Add 2016 - 2019 earning data from https://www.ssa.gov/oact/cola/AWI.html#Series

try:
    from earnings import EarningsRecord
except ImportError:
    EarningsRecord = {}
""" in earnings.py, format like:
EarningsRecord = {
    1998 :      0.0,
    1999 :      0.0,
    2000 :      0.0,
    2001 :      0.0,
    2002 :      0.0,
    2003 :      0.0,
    2004 :      0.0,
    2005 :      0.0,
    2006 :      0.0,
    2007 :      0.0,
    2008 :      0.0,
    2009 :      0.0,
    2010 :      0.0,
    2011 :      0.0,
    2012 :      0.0,
    2013 :      0.0,
    2014 :      0.0,
    2015 :      0.0,
    2016 :      0.0,
    2017 :      0.0
}
"""


# National Average Wage Index (NAWI) data as defined by:
# https://www.ssa.gov/oact/cola/AWI.html
#
NationalAverageWageIndexSeries = {
    1951 :  2799.16,   1952 :  2973.32,   1953 :  3139.44,   1954 :  3155.64,   1955 :  3301.44,
    1956 :  3532.36,   1957 :  3641.72,   1958 :  3673.80,   1959 :  3855.80,   1960 :  4007.12,
    1961 :  4086.76,   1962 :  4291.40,   1963 :  4396.64,   1964 :  4576.32,   1965 :  4658.72,
    1966 :  4938.36,   1967 :  5213.44,   1968 :  5571.76,   1969 :  5893.76,   1970 :  6186.24,
    1971 :  6497.08,   1972 :  7133.80,   1973 :  7580.16,   1974 :  8030.76,   1975 :  8630.92,
    1976 :  9226.48,   1977 :  9779.44,   1978 : 10556.03,   1979 : 11479.46,   1980 : 12513.46,
    1981 : 13773.10,   1982 : 14531.34,   1983 : 15239.24,   1984 : 16135.07,   1985 : 16822.51,
    1986 : 17321.82,   1987 : 18426.51,   1988 : 19334.04,   1989 : 20099.55,   1990 : 21027.98,
    1991 : 21811.60,   1992 : 22935.42,   1993 : 23132.67,   1994 : 23753.53,   1995 : 24705.66,
    1996 : 25913.90,   1997 : 27426.00,   1998 : 28861.44,   1999 : 30469.84,   2000 : 32154.82,
    2001 : 32921.92,   2002 : 33252.09,   2003 : 34064.95,   2004 : 35648.55,   2005 : 36952.94,
    2006 : 38651.41,   2007 : 40405.48,   2008 : 41334.97,   2009 : 40711.61,   2010 : 41673.83,
    2011 : 42979.61,   2012 : 44321.67,   2013 : 44888.16,   2014 : 46481.52,   2015 : 48098.63,
    2016 : 48642.15,   2017 : 50321.89,   2018 : 52145.80,   2019 : 54099.99,   2020 : 55628.60,
}


def load_xml_statement(fspec=SOC_SEC_XML):
    msg = None
    try:
        xtree = et.parse(fspec)
    except OSError as e:
        if not EarningsRecord:
            msg = "No Earnings Record and no XML statement! - %s\n" % (e,)
            print(msg, file=sys.stderr)
            EarningsRecord.update({2022: 0})
    else:
        namespaces = {'osss': 'http://ssa.gov/osss/schemas/2.0'}
        xroot = xtree.getroot()
        EarningsRecord.clear()
        EarningsRecord.update({int(node.attrib.get("startYear")): float( node.find("osss:FicaEarnings", namespaces).text)
            for node in xroot.findall('osss:EarningsRecord/osss:Earnings', namespaces)})
    return msg


xml_statement_error = load_xml_statement()

# The first year with Social Security Earnings
EarningsRecord_FirstYear = min(EarningsRecord, key=int)

# The last year with Social Security Earnings
EarningsRecord_LastYear = max(EarningsRecord, key=int)

# The first year of NAWI data
NationalAverageWageIndexSeries_FirstYear = min(NationalAverageWageIndexSeries, key=int)

# The last year of NAWI data
NationalAverageWageIndexSeries_LastYear = max(NationalAverageWageIndexSeries, key=int)

# Dictionary to hold the Average Wage Index (AWI) adjustment by year
AWI_Factors = {}

# Keep track of the last year for which an AWI adjustment factor is calculated
Last_AWI_Year = NationalAverageWageIndexSeries_FirstYear

# Calculate the AWI adjustment factor for each year that we have data
for i in range(NationalAverageWageIndexSeries_FirstYear, NationalAverageWageIndexSeries_LastYear) :
    AWI_Factors[i] = 1 + ( (NationalAverageWageIndexSeries[NationalAverageWageIndexSeries_LastYear] - NationalAverageWageIndexSeries[i]) / NationalAverageWageIndexSeries[i])
    Last_AWI_Year = i

# If we don't have data for the most recent years, just pad out the adjustment
# factor to be "1.0" up until the last year with earnings
for i in range(Last_AWI_Year + 1, EarningsRecord_LastYear + 1) :
    AWI_Factors[i] = 1.0

# Dictionary to hold the amount of annual adjusted earnings (as adjusted by the
# AWI factors in each year) per year
AdjustedEarnings = {}

# Calculate the amount of the adjusted earnings for each year by multiplying
# the earnings in each year by the AWI adjustment factor for that specific year
for i in range(EarningsRecord_FirstYear, EarningsRecord_LastYear + 1) :
    AdjustedEarnings[i] = EarningsRecord[i] * AWI_Factors[i]

MissingEarningYears = list(str(k) for k, v in EarningsRecord.items() if not v)
TotalAllEarnings = sum(EarningsRecord.values())
TotalAdjustedEarnings = sum(AdjustedEarnings.values())

# Top 35 years of adjusted annual earnings
Top35YearsEarnings = sum(sorted(AdjustedEarnings.values())[-35:])

# Calculate the Average Indexed Monthly earnings (AIME) by dividing the Top 35
# years of earnings by the number of months in 35 years (35 * 12 = 420)
AIME = Top35YearsEarnings / 420.0

# Calculate the Social Security "Bend Points" for the Primary Insurance Amount
# (PIA) as defined by:
# https://www.ssa.gov/oact/cola/piaformula.html
FirstBendPoint = round(180.0 * NationalAverageWageIndexSeries[NationalAverageWageIndexSeries_LastYear] / 9779.44)
SecondBendPoint = round(1085.0 * NationalAverageWageIndexSeries[NationalAverageWageIndexSeries_LastYear] / 9779.44)

# Variable to hold the normal monthly benefit amount
NormalMonthlyBenefit = 0.0;

# If the calculated AIME is below the first bend point
if AIME <= FirstBendPoint:
    NormalMonthlyBenefit = 0.9 * AIME
# Otherwise, if the AIME is between the two bend points
elif AIME > FirstBendPoint and AIME <= SecondBendPoint:
    NormalMonthlyBenefit = (0.9 * FirstBendPoint) + ( 0.32 * (AIME - FirstBendPoint) )
# Otherwise if the AIME is beyond the second bend point
else:
    NormalMonthlyBenefit = (0.9 * FirstBendPoint) + ( 0.32 * (SecondBendPoint - FirstBendPoint) ) + ( 0.15 * (AIME - SecondBendPoint) )

# The monthly benefit amount is rounded down to the nearest 0.10
NormalMonthlyBenefit = (floor(NormalMonthlyBenefit * 10.0)) / 10.0

# Calculate the reduced monthly benefit. Note that this takes into account the
# worst case scenario (70%). Depending on your birth date and how early you
# begin drawing Social Security, this number may be different.
ReducedMonthlyBenefit = 0.7 * NormalMonthlyBenefit
ReducedMonthlyBenefit = (floor(ReducedMonthlyBenefit * 10.0)) / 10.0

# Calculate the increased benefit from delaying past Full Retirement Age
# Note this calculates for 5 years, the maximum, but currently the increase
# ends at age 70. This means someone with an FRA of 67 can only get 3 years
# of increased benefits. The rest calculated don't apply to that person.
IncreasedBenefit = []
Benefit = NormalMonthlyBenefit * 12
for yr in range(5):
    Benefit *= 1.08
    MonthlyBenefit = Benefit / 12
    MonthlyBenefit = (floor(MonthlyBenefit * 10.0)) / 10.0
    IncreasedBenefit.append(MonthlyBenefit)


Results = {
    "EarningsRecord": EarningsRecord,
    "MissingEarningYears": MissingEarningYears,
    "TotalActualEarnings": TotalAllEarnings,
    "TotalAdjustedEarnings": TotalAdjustedEarnings,
    "Top35YearsEarnings": Top35YearsEarnings,
    "AverageIndexedMonthlyEarnings": AIME,
    "FirstBendPoint": FirstBendPoint,
    "SecondBendPoint": SecondBendPoint,
    "NormalBenefit": NormalMonthlyBenefit,
    "ReducedBenefit": ReducedMonthlyBenefit,
    "IncreasedBenefit": IncreasedBenefit,
}




if __name__ == "__main__":

    print('\n'.join(format_results(Results)))
