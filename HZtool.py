import arcpy
import os

from arcpy.management import Append
from additional_criteria import *

def hz_line(hz):
    area = 0
    with arcpy.da.SearchCursor(hz, ("KET_NR", "SHAPE@LENGTH", "Plotas")) as cursor:
        for row in cursor:
            if row[0] == 11: area += row[1]*0.12
            elif row[0] == 110: area += row[1]*0.12 + row[1]*0.0396
            elif row[0] == 111: area += row[1]*0.5
            elif row[0] == 112: area += row[1]*0.175
            elif row[0] == 1131:    # nes daznai Plotas yra Null
                if row[2]:
                    area += row[1]*0.5*row[2]
                else:
                    area += row[1]*0.5*3.5
            elif row[0] == 1132: area += row[1]*0.2035
            elif row[0] == 1133: area += row[1]*0.0286
            elif row[0] == 114: area += row[1]*0.5
            elif row[0] == 12: area += row[1]*0.25
            elif row[0] == 122: area += row[1]*0.125
            elif row[0] == 125: area += row[1]*0.5
            elif row[0] == 126: area += row[1]*0.12
            elif row[0] == 127: area += row[1]*0.37036
            elif row[0] == 13: area += row[1]*0.24
            elif row[0] == 14: area += row[1]*0.12
            elif row[0] == 15: area += row[1]*0.0396
            elif row[0] == 16: area += row[1]*0.0792
            elif row[0] == 17: area += row[1]*0.06
            elif row[0] == 18: area += row[1]*0.0825
            elif row[0] == 19: area += row[1]*0.06
    return area

def hz_polygon(hz):
    area = 0
    with arcpy.da.SearchCursor(hz, ("KET_NR", "SHAPE@AREA")) as cursor:
        for row in cursor:
            if row[0] == 1151: area += row[1]*0.35
            elif row[0] == 1152: area += row[1]*0.35
            elif row[0] == 1153: area += row[1]*0.35
            elif row[0] == 132: area += row[1]*0.2
            elif row[0] == 1322: area += row[1]*0.18
    return area

def hz_point(hz):
    area = 0
    with arcpy.da.SearchCursor(hz, "KET_NR") as cursor:
        for row in cursor:
            if row[0] == 1161: area += 1.44
            elif row[0] == 1162: area += 1.82
            elif row[0] == 1163: area += 1.82
            elif row[0] == 1164: area += 2.62
            elif row[0] == 1165: area += 2.62
            elif row[0] == 1166: area += 2.62
            elif row[0] == 1167: area += 2.62
            elif row[0] == 1168: area += 2.62
            elif row[0] == 1169: area += 4
            elif row[0] == 11611: area += 2.5
            elif row[0] == 11621: area += 2.5
            elif row[0] == 11631: area += 2.5
            elif row[0] == 11641: area += 3.5
            elif row[0] == 11651: area += 3.5
            elif row[0] == 11691: area += 5
            elif row[0] == 1171: area += 1.98
            elif row[0] == 1172: area += 1.98
            elif row[0] == 118: area += 2.05
            elif row[0] == 119: area += 2
            elif row[0] == 120: area += 6.5
            elif row[0] == 121: area += 2
            elif row[0] == 123: area += 0.5
            elif row[0] == 11231: area += 1
            elif row[0] == 11232: area += 1.5
            elif row[0] == 124: area += 0.5
            elif row[0] == 128: area += 2
            elif row[0] == 129: area += 2
            elif row[0] == 130: area += 2
            elif row[0] == 14: area += 1
            elif row[0] == 15: area += 1.5
        return area

def hz_stats(hz):
    desc = arcpy.Describe(hz)
    shape = desc.shapeType
    if shape == "Polyline":
        return hz_line(hz)
    elif shape == "Polygon":
        return hz_polygon(hz)
    elif shape == "Point":
        return hz_point(hz)

all_hz = []
total_area = 0
scratchGDB = arcpy.env.scratchGDB

choice = arcpy.GetParameterAsText(1)
if choice == "Linijos":
    all_hz.append(os.path.join(os.getcwd(), "jupiteris2.sde\\VP_SDE1.INFRASTR.KELIO_ZENKLAI\\VP_SDE1.INFRASTR.KZ_HZ_Linijos"))
elif choice == "Plotai":
    all_hz.append(os.path.join(os.getcwd(), "jupiteris2.sde\\VP_SDE1.INFRASTR.KELIO_ZENKLAI\\VP_SDE1.INFRASTR.KZ_HZ_Plotai"))
elif choice == "Taškai":
    all_hz.append(os.path.join(os.getcwd(), "jupiteris2.sde\\VP_SDE1.INFRASTR.KELIO_ZENKLAI\\VP_SDE1.INFRASTR.KZ_HZ_Taskai"))
elif choice == "Visi":
    hz_name = {1: "KZ_HZ_Linijos", 2: "KZ_HZ_Plotai", 3: "KZ_HZ_Taskai"}
    for i in [1, 2, 3]:
        all_hz.append(os.path.join(os.getcwd(), "jupiteris2.sde\\VP_SDE1.INFRASTR.KELIO_ZENKLAI\\VP_SDE1.INFRASTR.{}".format(hz_name[i])))


creation_type = arcpy.GetParameterAsText(2)
teritory = arcpy.GetParameterAsText(3)
date = arcpy.GetParameterAsText(4)

for hz in all_hz:
    out_featureclass = os.path.join(scratchGDB, hz.rsplit(".", 1)[-1])

    if date:
        hz = by_date(hz, date)
    if creation_type != "Visi":
        hz = by_type(hz, creation_type, "{}_By_Date".format(out_featureclass))

    hz = by_teritory(hz, teritory, "{}_By_Teritory".format(out_featureclass))
    total_area += hz_stats(hz)
        
arcpy.SetParameter(0, total_area)
arcpy.Delete_management(scratchGDB)
