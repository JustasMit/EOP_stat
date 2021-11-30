import arcpy
import os

def by_date(layer, date, type):
    if date == "":
        if type == "Sukurtas arba redaguotas":
            return arcpy.MakeFeatureLayer_management(layer, type, "created_date IS NOT NULL OR last_edited_date IS NOT NULL OR created_date IS NULL OR last_edited_date IS NULL")
        elif type == "Sukurtas":
            return arcpy.MakeFeatureLayer_management(layer, type, "created_date IS NOT NULL OR (created_date IS NULL AND last_edited_date IS NULL)")
        elif type == "Redaguotas":
            return arcpy.MakeFeatureLayer_management(layer, type, "NOT (created_date IS NOT NULL OR (created_date IS NULL AND last_edited_date IS NULL))")
            
    elif date:
        if type == "Sukurtas arba redaguotas":
            return arcpy.MakeFeatureLayer_management(layer, type, "(last_edited_date IS NOT NULL And last_edited_date > '{}') or created_date > '{}'".format(date, date))
        if type == "Sukurtas":
            return arcpy.MakeFeatureLayer_management(layer, type, "created_date IS NOT NULL And created_date > '{}'".format(date))
        if type == "Redaguotas":
            return arcpy.MakeFeatureLayer_management(layer, type, "(last_edited_date IS NOT NULL and created_date <> last_edited_date) And last_edited_date > '{}'".format(date))  
    
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

kz = r"\\venera\projektai\Geoproc\EOP_stat\jupiteris2.sde\VP_SDE1.INFRASTR.KELIO_ZENKLAI\VP_SDE1.INFRASTR.KZ"
creation_type = arcpy.GetParameterAsText(1)
teritory = arcpy.GetParameterAsText(2)
date = arcpy.GetParameterAsText(3)

kz = by_date(kz, date, creation_type)
kz = by_teritory(kz, teritory, "{}_By_Teritory".format(out_featureclass))

statistic = kz_stats(kz)

arcpy.SetParameter(0, statistic)
arcpy.Delete_management(scratchGDB)