import arcpy
import os
from additional_criteria import *

def kz_stats(kz):
    count = arcpy.GetCount_management(kz)
    return count[0]

kz = arcpy.GetParameterAsText(0)
scratchGDB = arcpy.env.scratchGDB
out_featureclass = os.path.join(scratchGDB, kz.rsplit(".", 1)[-1])       
creation_type = arcpy.GetParameterAsText(0)
teritory = arcpy.GetParameterAsText(0)
date = arcpy.GetParameterAsText(0)

if date:
    kz = by_date(kz, date)
if creation_type != "Visi":
    kz = by_type(kz, creation_type, "{}_By_Date".format(out_featureclass))
kz = by_teritory(kz, teritory, "{}_By_Teritory".format(out_featureclass))
statistic = kz_stats(kz)

arcpy.SetParameter(1, statistic)
arcpy.Delete_management(scratchGDB)