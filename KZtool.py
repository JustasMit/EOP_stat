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

def kz_stats(kz):
    count = arcpy.GetCount_management(kz)
    return count[0]

scratchGDB = arcpy.env.scratchGDB
out_featureclass = os.path.join(scratchGDB, "KZ_TEMP")  

kz = os.path.join(os.getcwd(), "jupiteris2.sde\\VP_SDE1.INFRASTR.KELIO_ZENKLAI\\VP_SDE1.INFRASTR.KZ")
creation_type = arcpy.GetParameterAsText(1)
teritory = arcpy.GetParameterAsText(2)
date = arcpy.GetParameterAsText(3)

if date:
    kz = by_date(kz, date)
if creation_type != "Visi":
    kz = by_type(kz, creation_type, "{}_By_Date".format(out_featureclass))
kz = by_teritory(kz, teritory, "{}_By_Teritory".format(out_featureclass))

statistic = kz_stats(kz)

arcpy.SetParameter(0, statistic)
arcpy.Delete_management(scratchGDB)