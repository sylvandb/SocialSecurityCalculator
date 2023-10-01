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
# Written by Ryan Antkowiak 2017-07-15
# Copyright (c) 2017 All Rights Reserved
#
# UPDATE data tables annually or as needed

# Import modules
from datetime import datetime
from math import floor
import xml.etree.ElementTree as et
import sys


# filename default
SOC_SEC_XML = "Your_Social_Security_Statement_Data.xml"

# cmdline args
Earnings = sys.argv[1:] and sys.argv[1] in ('--earnings', )
if Earnings:
    del sys.argv[1]
# filename on cmdline
if sys.argv[1:]:
    SOC_SEC_XML = sys.argv[1]
    del sys.argv[1]
Earnings = Earnings or (sys.argv[1:] and sys.argv[1] in ('--earnings', ))



# UPDATE National Average Wage Index (NAWI) data as defined by:
# https://www.ssa.gov/oact/cola/AWI.html
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
    2021 : 60575.07,
}


# UPDATE S&P 500 Index - Historical Annual Data
# https://www.macrotrends.net/2526/sp-500-historical-annual-returns
# TODO: cross check (with yahoo or ???)
# Year: (Average Closing Price,  Year Open,  Year High,  Year Low,  Year Close,  Annual % Change)
SnP500AnnualData = {
    2022: (4097.49, 4796.56, 4796.56, 3577.03, 3839.50, -19.44),
    2021: (4273.41, 3700.65, 4793.06, 3700.65, 4766.18, 26.89),
    2020: (3217.86, 3257.85, 3756.07, 2237.40, 3756.07, 16.26),
    2019: (2913.36, 2510.03, 3240.02, 2447.89, 3230.78, 28.88),
    2018: (2746.21, 2695.81, 2930.75, 2351.10, 2506.85, -6.24),
    2017: (2449.08, 2257.83, 2690.16, 2257.83, 2673.61, 19.42),
    2016: (2094.65, 2012.66, 2271.72, 1829.08, 2238.83, 9.54),
    2015: (2061.07, 2058.20, 2130.82, 1867.61, 2043.94, -0.73),
    2014: (1931.38, 1831.98, 2090.57, 1741.89, 2058.90, 11.39),
    2013: (1643.80, 1462.42, 1848.36, 1457.15, 1848.36, 29.60),
    2012: (1379.61, 1277.06, 1465.77, 1277.06, 1426.19, 13.41),
    2011: (1267.64, 1271.87, 1363.61, 1099.23, 1257.60, 0.00),
    2010: (1139.97, 1132.99, 1259.78, 1022.58, 1257.64, 12.78),
    2009: (948.05, 931.80, 1127.78, 676.53, 1115.10, 23.45),
    2008: (1220.04, 1447.16, 1447.16, 752.44, 903.25, -38.49),
    2007: (1477.18, 1416.60, 1565.15, 1374.12, 1468.36, 3.53),
    2006: (1310.46, 1268.80, 1427.09, 1223.69, 1418.30, 13.62),
    2005: (1207.23, 1202.08, 1272.74, 1137.50, 1248.29, 3.00),
    2004: (1130.65, 1108.48, 1213.55, 1063.23, 1211.92, 8.99),
    2003: (965.23, 909.03, 1111.92, 800.73, 1111.92, 26.38),
    2002: (993.93, 1154.67, 1172.51, 776.76, 879.82, -23.37),
    2001: (1192.57, 1283.27, 1373.73, 965.80, 1148.08, -13.04),
    2000: (1427.22, 1455.22, 1527.46, 1264.74, 1320.28, -10.14),
    1999: (1327.33, 1228.10, 1469.25, 1212.19, 1469.25, 19.53),
    1998: (1085.50, 975.04, 1241.81, 927.69, 1229.23, 26.67),
    1997: (873.43, 737.01, 983.79, 737.01, 970.43, 31.01),
    1996: (670.49, 620.73, 757.03, 598.48, 740.74, 20.26),
    1995: (541.72, 459.11, 621.69, 459.11, 615.93, 34.11),
    1994: (460.42, 465.44, 482.00, 438.92, 459.27, -1.54),
    1993: (451.61, 435.38, 470.94, 429.05, 466.45, 7.06),
    1992: (415.75, 417.26, 441.28, 394.50, 435.71, 4.46),
    1991: (376.19, 326.45, 417.09, 311.49, 417.09, 26.31),
    1990: (334.63, 359.69, 368.95, 295.46, 330.22, -6.56),
    1989: (323.05, 275.31, 359.80, 275.31, 353.40, 27.25),
    1988: (265.88, 255.94, 283.66, 242.63, 277.72, 12.40),
    1987: (287.00, 246.45, 336.77, 223.92, 247.08, 2.03),
    1986: (236.39, 209.59, 254.00, 203.49, 242.17, 14.62),
    1985: (186.83, 165.37, 212.02, 163.68, 211.28, 26.33),
    1984: (160.46, 164.04, 170.41, 147.82, 167.24, 1.40),
    1983: (160.47, 138.34, 172.65, 138.34, 164.93, 17.27),
    1982: (119.71, 122.74, 143.02, 102.42, 140.64, 14.76),
    1981: (128.04, 136.34, 138.12, 112.77, 122.55, -9.73),
    1980: (118.71, 105.76, 140.52, 98.22, 135.76, 25.77),
    1979: (103.00, 96.73, 111.27, 96.13, 107.94, 12.31),
    1978: (96.11, 93.82, 106.99, 86.90, 96.11, 1.06),
    1977: (98.18, 107.00, 107.00, 90.71, 95.10, -11.50),
    1976: (102.04, 90.90, 107.83, 90.90, 107.46, 19.15),
    1975: (86.18, 70.23, 95.61, 70.04, 90.19, 31.55),
    1974: (82.78, 97.68, 99.80, 62.28, 68.56, -29.72),
    1973: (107.44, 119.10, 120.24, 92.16, 97.55, -17.37),
    1972: (109.13, 101.67, 119.12, 101.67, 118.05, 15.63),
    1971: (98.32, 91.15, 104.77, 90.16, 102.09, 10.79),
    1970: (83.15, 93.00, 93.46, 69.29, 92.15, 0.10),
    1969: (97.77, 103.93, 106.16, 89.20, 92.06, -11.36),
    1968: (98.38, 96.11, 108.37, 87.72, 103.86, 7.66),
    1967: (91.96, 80.38, 97.59, 80.38, 96.47, 20.09),
    1966: (85.18, 92.18, 94.06, 73.20, 80.33, -13.09),
    1965: (88.16, 84.23, 92.63, 81.60, 92.43, 9.06),
    1964: (81.37, 75.43, 86.28, 75.43, 84.75, 12.97),
    1963: (69.86, 62.69, 75.02, 62.69, 75.02, 18.89),
    1962: (62.32, 70.96, 71.13, 52.32, 63.10, -11.81),
    1961: (66.27, 57.57, 72.64, 57.57, 71.55, 23.13),
    1960: (55.85, 59.91, 60.39, 52.20, 58.11, -2.97),
    1959: (57.42, 55.44, 60.71, 53.58, 59.89, 8.48),
    1958: (46.20, 40.33, 55.21, 40.33, 55.21, 38.06),
    1957: (44.42, 46.20, 49.13, 38.98, 39.99, -14.31),
    1956: (46.64, 45.16, 49.64, 43.11, 46.67, 2.62),
    1955: (40.50, 36.75, 46.41, 34.58, 45.48, 26.40),
    1954: (29.72, 24.95, 35.98, 24.80, 35.98, 45.02),
    1953: (24.72, 26.54, 26.66, 22.71, 24.81, -6.62),
    1952: (24.45, 23.80, 26.59, 23.09, 26.57, 11.78),
    1951: (22.32, 20.77, 23.85, 20.69, 23.77, 16.46),
    1950: (18.39, 16.66, 20.43, 16.65, 20.41, 21.78),
    1949: (15.24, 14.95, 16.79, 13.55, 16.76, 10.26),
    1948: (15.51, 15.34, 17.06, 13.84, 15.20, -0.65),
    1947: (15.15, 15.20, 16.20, 13.71, 15.30, 0.00),
    1946: (17.07, 17.25, 19.25, 14.12, 15.30, -11.87),
    1945: (15.14, 13.33, 17.68, 13.21, 17.36, 30.72),
    1944: (12.47, 11.66, 13.29, 11.56, 13.28, 13.80),
    1943: (11.52, 9.84, 12.64, 9.84, 11.67, 19.45),
    1942: (8.67, 8.89, 9.77, 7.47, 9.77, 12.43),
    1941: (9.83, 10.48, 10.86, 8.37, 8.69, -17.86),
    1940: (11.01, 12.63, 12.77, 8.99, 10.58, -15.29),
    1939: (12.05, 13.08, 13.23, 10.18, 12.49, -5.45),
    1938: (11.48, 10.52, 13.91, 8.50, 13.21, 25.21),
    1937: (15.41, 17.02, 18.68, 10.17, 10.55, -38.59),
    1936: (15.45, 13.40, 17.69, 13.40, 17.18, 27.92),
    1935: (10.58, 9.51, 13.46, 8.06, 13.43, 41.37),
    1934: (9.83, 10.11, 11.82, 8.36, 9.50, -5.94),
    1933: (9.04, 6.83, 12.20, 5.53, 10.10, 46.59),
    1932: (6.92, 7.82, 9.31, 4.40, 6.89, -15.15),
    1931: (13.66, 15.85, 18.17, 7.72, 8.12, -47.07),
    1930: (21.00, 21.18, 25.92, 14.44, 15.34, -28.48),
    1929: (26.19, 24.81, 31.86, 17.66, 21.45, -11.91),
    1928: (19.94, 17.76, 24.35, 16.95, 24.35, 37.88),
}

#suspect = [(y, PChg, round(10000 * (YClose / YOpen - 1))/100) for y, (AvgCP, YOpen, YHigh, YLow, YClose, PChg) in SnP500AnnualData.items()
#    if abs(PChg * 100 - round(10000 * (YClose / YOpen - 1))) > abs(PChg * 20)]
#print(suspect); exit()


# UPDATE Social Security OASI+DI Tax Rates - paid by each of employee and employer
# https://www.ssa.gov/OACT/ProgData/oasdiRates.html
OASDITaxRateChanges = {
    1937: 1,
    1950: 1.5,
    1954: 2.0,
    1957: 2.25,
    1959: 2.5,
    1960: 3.0,
    1962: 3.125,
    1963: 3.625,
    1966: 3.85,
    1967: 3.9,
    1968: 3.8, # wow, it dropped?!
    1969: 4.2, # must have been a mistake ;)
    1971: 4.6,
    1973: 4.85,
    1974: 4.95,
    1978: 5.05,
    1979: 5.08,
    1981: 5.35,
    1982: 5.4,
    1984: 5.7,
    1988: 6.06,
    1990: 6.2,
}
OASDITaxRates = {}
DefaultOASDITaxRate = 0
for year in range(min(OASDITaxRateChanges), 1 + max(OASDITaxRateChanges)):
    DefaultOASDITaxRate = OASDITaxRateChanges.get(year, DefaultOASDITaxRate)
    OASDITaxRates[year] = DefaultOASDITaxRate



Soft_Fail = False
XML_Statement_Error = None
Results = {}

# ??? delay load_xml_statement and the calculations???
def get_results():
    if not Results:
        do_the_big_calculation_method()
    if XML_Statement_Error:
        raise ValueError(XML_Statement_Error)
    snp500()
    return Results


def years2ym(years):
    y = int(years)
    mfloat = 12 * (years - y)
    m = int(round(mfloat))
    m += (mfloat > m)
    return y, m


def format_results(results):
    yr = 0
    try:
        while True:
            results['IncreasedBenefit'][yr]
            yr += 1
    except IndexError:
        pass
    FRA = 70 - yr
    lines = []
    lines.append("Earnings record years analyzed ____________ {}".format(len(results['EarningsRecord'])))
    lines.append("First Earnings Year analyzed ______________ {}".format(min(results['EarningsRecord'])))
    lines.append("Last Earnings Year analyzed _______________ {}".format(max(results['EarningsRecord'])))
    lines.append("Earning Years with 0 Earnings _____________ {}".format(', '.join(results['MissingEarningYears'])))
    lines.append("Total Actual Earnings in all Years ________{:11.2f}".format(results['TotalActualEarnings']))
    lines.append("Total Adjusted Earnings in all Years ______{:11.2f}".format(results['TotalAdjustedEarnings']))
    lines.append("Discarded Adjusted Earnings _______________{:11.2f}".format(results['TotalAdjustedEarnings'] - results['Top35YearsEarnings']))
    lines.append("Top 35 Included Minimum Annual Income _____{:11.2f}".format(results['Top35YearsMinimum']))
    lines.append("Top 35 Years of Adjusted Earnings _________{:11.2f}".format(results['Top35YearsEarnings']))
    lines.append("Average Indexed Monthly Earnings (AIME) ___{:11.2f}".format(results['AverageIndexedMonthlyEarnings']))
    lines.append("First Bend Point __________________________{:11.2f}".format(results['FirstBendPoint']))
    lines.append("Second Bend Point _________________________{:11.2f}".format(results['SecondBendPoint']))
    lines.append("Reduced (70%) Monthly Benefit (age 62) ____{:11.2f}".format(results['ReducedBenefit']))
    rb = results['ReducedBenefit'] * 12.0
    nb = results['NormalBenefit'] * 12.0
    lines.append("Reduced (70%) Annual Benefit ______________{:11.2f}".format(rb))
    lines.append("Normal Monthly Benefit (age {}) ___________{:11.2f}".format(FRA, results['NormalBenefit']))
    lines.append("Normal Annual Benefit _____________________{:11.2f}".format(nb))
    lines.append("Increase over ReducedBenefit ______________{:10.1f}%".format(100 * (nb / rb - 1)))
    b_cost = (FRA - 62) * rb
    lines.append("Delay Opportunity Cost from ReducedBenefit {:11.2f}".format(b_cost))
    recovered = b_cost / (nb - rb)
    year, month = years2ym(FRA + recovered)
    lines.append("  Recovered after {:.1f} years, age {} +{} months".format(recovered, year, month))
    for yr in range(0, yr):
        m_ib = results['IncreasedBenefit'][yr]
        a_ib = m_ib * 12.0
        lines.append("Delaying until FRA+{} (age {}):".format(yr + 1, FRA + yr + 1))
        lines.append("  Increased Monthly Benefit _______________{:11.2f}".format(m_ib))
        lines.append("  Increased Annual Benefit ________________{:11.2f}".format(a_ib))
        lines.append("  Increase over ReducedBenefit ____________{:10.1f}%".format(100 * (a_ib / rb - 1)))
        lines.append("  Increase over NormalBenefit _____________{:10.1f}%".format(100 * (a_ib / nb - 1)))
    rb_cost = (70 - 62) * rb
    nb_cost = (70 - FRA) * nb
    lines.append("Delay Opportunity Cost from ReducedBenefit {:11.2f}".format(rb_cost))
    recovered = rb_cost / (a_ib - rb)
    year, month = years2ym(FRA + recovered)
    lines.append("  Recovered after {:.1f} years, age {} +{} months".format(recovered, year, month))
    lines.append("Delay Opportunity Cost from NormalBenefit _{:11.2f}".format(nb_cost))
    recovered = nb_cost / (a_ib - nb)
    year, month = years2ym(FRA + recovered)
    lines.append("  Recovered after {:.1f} years, age {} +{} months".format(recovered, year, month))
    lines.extend("%s: %s" % (k, v) for k, v in res.items() if k[:6] == 'SnP500')
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


# Show your earnings record in formatted form suitable to
# copy/paste into https://ssa.tools/calculator.html
def show_earnings(earnings=None, outf=None):
    outf = outf or print
    for year, amount in iter_earnings(earnings):
        outf(f"{year}  ${amount:d}")


def iter_earnings(earnings=None):
    earnings = earnings or EarningsRecord
    for y, a in earnings.items():
        yield (y, int(a))


def load_xml_statement(fspec=SOC_SEC_XML):
    global XML_Statement_Error
    XML_Statement_Error = None

    try:
        xtree = et.parse(fspec)
    except OSError as e:
        if not EarningsRecord:
            XML_Statement_Error = "No Earnings Record and no XML statement! - %s\n" % (e,)
            if not Soft_Fail:
                raise ValueError(XML_Statement_Error)
            print(XML_Statement_Error, file=sys.stderr)
            EarningsRecord.update({2022: 0})
    else:
        namespaces = {'osss': 'http://ssa.gov/osss/schemas/2.0'}
        xroot = xtree.getroot()
        EarningsRecord.clear()
        EarningsRecord.update({int(node.attrib.get("startYear")): float( node.find("osss:FicaEarnings", namespaces).text)
            for node in xroot.findall('osss:EarningsRecord/osss:Earnings', namespaces)})
    return XML_Statement_Error



def do_the_big_calculation_method():

    load_xml_statement()

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
    Top35AdjustedEarnings = sorted(AdjustedEarnings.values())[-35:]
    Top35YearsEarnings = sum(Top35AdjustedEarnings)
    Top35YearsMinimum = Top35AdjustedEarnings[0]

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
    for yr in range(3):
        Benefit *= 1.08
        MonthlyBenefit = Benefit / 12
        MonthlyBenefit = (floor(MonthlyBenefit * 10.0)) / 10.0
        IncreasedBenefit.append(MonthlyBenefit)


    Results.update({
        "EarningsRecord": EarningsRecord,
        "Top35AdjustedEarnings": Top35AdjustedEarnings,
        "MissingEarningYears": MissingEarningYears,
        "TotalActualEarnings": TotalAllEarnings,
        "TotalAdjustedEarnings": TotalAdjustedEarnings,
        "Top35YearsEarnings": Top35YearsEarnings,
        "Top35YearsMinimum": Top35YearsMinimum,
        "AverageIndexedMonthlyEarnings": AIME,
        "FirstBendPoint": FirstBendPoint,
        "SecondBendPoint": SecondBendPoint,
        "NormalBenefit": NormalMonthlyBenefit,
        "ReducedBenefit": ReducedMonthlyBenefit,
        "IncreasedBenefit": IncreasedBenefit,
    })


# calulation options:
#  * percentage invested in S&P 500 (2x to include employer portion)
#  * when invested: year end (at year close), year start (at year-1 close), at average closing, at mid-%-change
# what about dividends?!?
def snp500():
    lastsnp = max(SnP500AnnualData)
    earnmax = max(Results['EarningsRecord'])
    earnmin = min(Results['EarningsRecord'])

    allsum = sum(PChg for y, (AvgCP, YOpen, YHigh, YLow, YClose, PChg) in SnP500AnnualData.items())
    allavg = allsum / len(SnP500AnnualData)

    # the last 0 means no change for years with no data, should it be allavg instead?
    DefaultYear = [0, 0, 0, 0, 0, 0]

    # If we don't have SnP data for the most recent years, it counts as 0's (0% return)
    # should it be padded with allavg instead for an average return?
    #for y in range(lastsnp + 1, earnmax + 1):
    #    earnsum += allavg
    earnsum = sum(PChg for y, (AvgCP, YOpen, YHigh, YLow, YClose, PChg) in SnP500AnnualData.items() if earnmin < y <= earnmax)
    earnavg = earnsum / len(Results['EarningsRecord'])

    snptotal = 0
    snpinvested = 0
    for year, dollar in Results['EarningsRecord'].items():
        taxamount = dollar * OASDITaxRates.get(year, DefaultOASDITaxRate) / 100
        snpinvested += taxamount
        # gain on previous investment
        snptotal *= (100 + SnP500AnnualData.get(year, DefaultYear)[5]) / 100
        # new investment of dollars this year at close of last day
        snptotal += taxamount

    def fv(years, rate, val):
        # FutureValue = (1 + Rate) ^ Years * Value
        return (1 + rate) ** years * val

    lowrate = min(allavg, earnavg) / 2
    snp5yrlowtotal = fv(5, lowrate / 100, snptotal)
    snp10yrlowtotal = fv(5, lowrate / 100, snp5yrlowtotal)

    avgrate = max(allavg, earnavg)
    snp5yravgtotal = fv(5, avgrate / 100, snptotal)
    snp10yravgtotal = fv(5, avgrate / 100, snp5yravgtotal)

    Results.update({
        "SnP500LastYear": lastsnp,
        "SnP500AllYears": len(SnP500AnnualData),
        "SnP500AvgAll": round(allavg, 2),
        "SnP500EarnYears": len(Results['EarningsRecord']),
        "SnP500AvgEarnYears": round(earnavg, 2),

        "SnP500EmployeeTaxed": round(snpinvested),
        "SnP500NowValue": round(snptotal),
        "SnP500AnnuitizedNow": [(p/100, round(p * snptotal/100)) for p in range(3, 7)],

        "SnP500LowRate": round(lowrate, 2),
        "SnP5005yrValueLow": round(snp5yrlowtotal),
        "SnP500Annuitized5yrLow": [(p/100, round(p * snp5yrlowtotal/100)) for p in range(3, 7)],
        "SnP50010yrValueLow": round(snp10yrlowtotal),
        "SnP500Annuitized10yrLow": [(p/100, round(p * snp10yrlowtotal/100)) for p in range(3, 7)],

        "SnP500AvgRate": round(avgrate, 2),
        "SnP5005yrValueAvg": round(snp5yravgtotal),
        "SnP500Annuitized5yrAvg": [(p/100, round(p * snp5yravgtotal/100)) for p in range(3, 7)],
        "SnP50010yrValueAvg": round(snp10yravgtotal),
        "SnP500Annuitized10yrAvg": [(p/100, round(p * snp10yravgtotal/100)) for p in range(3, 7)],
    })



if __name__ == "__main__":

    if Earnings:
        load_xml_statement()
        show_earnings()

    else:
        Soft_Fail = True
        res = get_results()
        print('\n'.join(format_results(res)))
