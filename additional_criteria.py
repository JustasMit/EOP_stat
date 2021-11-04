import arcpy
import datetime

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