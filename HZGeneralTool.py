import arcpy
import os
import json
import unicodedata
import tempfile, shutil

# def by_territory(layer, territories, output):
#     arcpy.MakeFeatureLayer_management("https://services1.arcgis.com/usA3lHW20rGU6glp/ArcGIS/rest/services/Zenklu_prieziuros_teritorijos_view/FeatureServer/0", "Territory")
#     for territory in territories:
#         if territory != "Visa teritorija":
#             arcpy.MakeFeatureLayer_management("Territory", territory, "SENIUNIJA = '{}'".format(territory))
#             arcpy.analysis.Clip(layer, territory, output + "_" + territory, None)
#         else:
#             arcpy.analysis.Clip(layer, "Territory", output + "_all_territories", None)

def hz_line(hz, marking):
    area = 0
    with arcpy.da.SearchCursor(hz, ("KET_NR", "SHAPE@LENGTH", "Plotas", "ZENKL_BUDAS")) as cursor:
        for row in cursor:
            if row[3] == marking:
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

def hz_polygon(hz, marking):
    area = 0
    with arcpy.da.SearchCursor(hz, ("KET_NR", "SHAPE@AREA", "ZENKL_BUDAS")) as cursor:
        for row in cursor:
            if row[2] == marking:
                if row[0] == 1151: area += row[1]*0.35
                elif row[0] == 1152: area += row[1]*0.35
                elif row[0] == 1153: area += row[1]*0.35
                elif row[0] == 132: area += row[1]*0.2
                elif row[0] == 1322: area += row[1]*0.18
    return area

def hz_point(hz, marking):
    area = 0
    with arcpy.da.SearchCursor(hz, ("KET_NR", "ZENKL_BUDAS")) as cursor:
        for row in cursor:
            if row[1] == marking:
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

def hz_stats(hz, marking):
    desc = arcpy.Describe(hz)
    shape = desc.shapeType
    if shape == "Polyline":
        return hz_line(hz, marking)
    elif shape == "Polygon":
        return hz_polygon(hz, marking)
    elif shape == "Point":
        return hz_point(hz, marking)

sdeTempPath = tempfile.mkdtemp()
arcpy.CreateDatabaseConnection_management(sdeTempPath,'SDE1.sde','SQL_SERVER','jupiteris2','DATABASE_AUTH','geodinter', 'matavimai3', 'SAVE_USERNAME','VP_SDE1')
arcpy.env.workspace = sdeTempPath + '\SDE1.sde'

all_hz = []
total_area = 0

hz_name = {1: "KZ_HZ_Linijos", 2: "KZ_HZ_Plotai", 3: "KZ_HZ_Taskai"}
for i in [1, 2, 3]:
  all_hz.append(fr'VP_SDE1.INFRASTR.KELIO_ZENKLAI/VP_SDE1.INFRASTR.{hz_name[i]}')
  
arcpy.AddMessage(all_hz)
arcpy.AddMessage(sdeTempPath)

territories = ["Šiaurinis", "Rytinis", "Pietinis", "Vakarinis", "Centrinis"]
marking = arcpy.GetParameterAsText(1)

key_to_num = {"Suma": 0, "Plastikas": 1, "Dazai": 2, "Metalas": 3, "Plyteles": 4, "Kitas": 5, "Asfaltas": 6, "Termoplastas": 7, "Antislydiminis plastikas": 8}
num_to_key = {0: "Suma", 1: "Plastikas", 2: "Dazai", 3: "Metalas", 4: "Plyteles", 5: "Kitas", 6: "Asfaltas", 7: "Termoplastas", 8: "Antislydiminis plastikas"}

if marking:
    markings = {"Suma": 0}
    marking_list = marking.replace("'", "").split(";")
    temp_markings = dict.fromkeys(marking_list, 0)
    markings.update(temp_markings)
    markings = dict((key_to_num[key], value) for (key, value) in markings.items())

arcpy.MakeFeatureLayer_management(str("https://services1.arcgis.com/usA3lHW20rGU6glp/ArcGIS/rest/services/Zenklu_prieziuros_teritorijos_view/FeatureServer/0"), "Territory")

territories_dict = {}
for territory in territories:
    territory_markings = {}
    for hz in all_hz:
        
        arcpy.MakeFeatureLayer_management("Territory", territory, "SENIUNIJA = '{}'".format(territory))
        hz = arcpy.analysis.Clip(hz, territory, fr'in_memory/{territory}', None)

        if marking:
            for mark in markings:
                if mark == 0: continue
                temp_area = hz_stats(hz, mark)
                territory_markings.setdefault(mark, 0)
                territory_markings[mark] += temp_area
                markings[mark] += temp_area
                markings[0] += temp_area
        else:
            for i in range(1, 9):
                total_area += hz_stats(hz, i)
    
    if marking:
        territory_markings = dict((num_to_key[key], value) for (key, value) in territory_markings.items())
        territories_dict[territory] = territory_markings
    else:
        territories_dict[territory] = total_area

normalized_key = unicodedata.normalize('NFKD', "\u0160iaurinis").encode('ASCII', 'ignore').decode('ASCII')
territories_dict[normalized_key] = territories_dict.pop("\u0160iaurinis")
        
totals = {}
for territory_data in territories_dict.values():
    for type_name, type_area in territory_data.items():
        if type_name not in totals:
            totals[type_name] = 0
        totals[type_name] += type_area

total_area = sum(totals.values())
territories_dict["Visa teritorija"] = {type_name: type_area for type_name, type_area in totals.items()}
territories_dict["Visa teritorija"]["Visi tipai"] = total_area

if marking:
    arcpy.SetParameter(0, json.dumps(territories_dict))
else:
    arcpy.SetParameter(0, total_area)

arcpy.Delete_management("in_memory")
shutil.rmtree(sdeTempPath)
