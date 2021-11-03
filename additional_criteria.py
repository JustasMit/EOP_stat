import arcpy
import datetime

def by_date(layer, date):
    if len(date) > 10:
        date_formatted = datetime.datetime.strptime(date, "%d/%m/%Y %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
    else:
        date_formatted = datetime.datetime.strptime(date, "%d/%m/%Y").strftime("%Y-%m-%d")
    return arcpy.MakeFeatureLayer_management(layer, "Date_Temp", "last_edited_date > '{}'".format(date_formatted))

def by_type(layer, type, output):
    if type == "Sukurtas":
        return arcpy.MakeFeatureLayer_management(layer, type, "created_date IS NOT NULL") # daug created_date yra null. sitas buvo nelogiskas: last_edited_date Or (last_edited_date IS NOT NULL And created_date IS NULL)")
    elif type == "Redaguotas":
        return arcpy.MakeFeatureLayer_management(layer, type, "created_date <> last_edited_date")
    elif type == "Sukurtas arba redaguotas":
        created = arcpy.MakeFeatureLayer_management(layer, "Created_Temp", "created_date IS NOT NULL")
        edited = arcpy.MakeFeatureLayer_management(layer, "Edited_Temp", "created_date <> last_edited_date")
        return arcpy.Merge_management([created, edited], output)

def by_teritory(layer, teritory, output):
    arcpy.MakeFeatureLayer_management("https://services1.arcgis.com/usA3lHW20rGU6glp/ArcGIS/rest/services/Zenklu_prieziuros_teritorijos_view/FeatureServer/0", "Teritory")
    if teritory != "Visa teritorija":
        arcpy.MakeFeatureLayer_management("Teritory", teritory, "SENIUNIJA = '{}'".format(teritory))
        return arcpy.analysis.Clip(layer, teritory, output, None)
    else:
        return arcpy.analysis.Clip(layer, "Teritory", output, None)