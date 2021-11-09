import arcpy
import os

def by_date(layer, date):
    return arcpy.MakeFeatureLayer_management(layer, "Date_Temp", "last_edited_date > '{}'".format(date))

def by_type(layer, type, output):
    if type == "Sukurtas":
        return arcpy.MakeFeatureLayer_management(layer, type, "created_date IS NOT NULL and created_date = last_edited_date")
    elif type == "Redaguotas":
        return arcpy.MakeFeatureLayer_management(layer, type, "created_date <> last_edited_date")
    elif type == "Sukurtas arba redaguotas":
        return arcpy.MakeFeatureLayer_management(layer, type, "(created_date IS NOT NULL and created_date = last_edited_date) or created_date <> last_edited_date")

def by_teritory(layer, teritory, output):
    arcpy.MakeFeatureLayer_management("https://services1.arcgis.com/usA3lHW20rGU6glp/ArcGIS/rest/services/Zenklu_prieziuros_teritorijos_view/FeatureServer/0", "Teritory")
    if teritory != "Visa teritorija":
        arcpy.MakeFeatureLayer_management("Teritory", teritory, "SENIUNIJA = '{}'".format(teritory))
        return arcpy.analysis.Clip(layer, teritory, output, None)
    else:
        return arcpy.analysis.Clip(layer, "Teritory", output, None)

def infr_line(infr):
    length = 0
    with arcpy.da.SearchCursor(infr, "SHAPE@LENGTH") as cursor:
        for row in cursor:
            length += row[0]
    return length

def infr_polygon(infr):
    area = 0
    with arcpy.da.SearchCursor(infr, "SHAPE@AREA") as cursor:
        for row in cursor:
            area += row[0]
    return area

def infr_point(infr):
    count = arcpy.GetCount_management(infr)
    return count[0]

def infr_stats(infr):
    desc = arcpy.Describe(infr)
    shape = desc.shapeType
    if shape == "Polyline":
        return infr_line(infr)
    elif shape == "Polygon":
        return infr_polygon(infr)
    elif shape == "Point":
        return infr_point(infr)

scratchGDB = arcpy.env.scratchGDB
out_featureclass = os.path.join(scratchGDB, "INFR_TEMP")  

choice = arcpy.GetParameterAsText(1)
if choice == "Linijos":
    infr_name = "KZ_INFSTR_Linijos"
elif choice == "Plotai":
    infr_name = "KZ_INFSTR_Plotai"
elif choice == "Taskai":
    infr_name = "KZ_INFSTR_Taskai"
infr = r"\\venera\projektai\Geoproc\EOP_stat\jupiteris2.sde\VP_SDE1.INFRASTR.KELIO_ZENKLAI\VP_SDE1.INFRASTR.{}".format(infr_name)
creation_type = arcpy.GetParameterAsText(2)
teritory = arcpy.GetParameterAsText(3)
date = arcpy.GetParameterAsText(4)


if date:
    infr = by_date(infr, date)
if creation_type != "Visi":
    infr = by_type(infr, creation_type, "{}_By_Date".format(out_featureclass))
infr = by_teritory(infr, teritory, "{}_By_Teritory".format(out_featureclass))
statistic = infr_stats(infr)

arcpy.SetParameter(0, statistic)
arcpy.Delete_management(scratchGDB)