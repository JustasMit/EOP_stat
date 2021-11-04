import arcpy
import os
from additional_criteria import *

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