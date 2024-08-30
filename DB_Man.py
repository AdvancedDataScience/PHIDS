import pandas as pd
import os

DataDirectory="assets/all_schemes/trat/"
UC_Files=os.listdir(DataDirectory)
#AllDirs=["cdc","gh","bod","ds","op","ip"]
AllDirs=["op"]
df_list={}
df_tmp=pd.DataFrame()
for Folder in AllDirs:
        Files=os.listdir(DataDirectory+Folder)
        if(len(Files)>0):
            print(Folder)
            Files.sort()
            for iFile in Files:
                  scheme=iFile.split("_")[0]
                  if(scheme=='uc'):
                        FileLocation=DataDirectory+Folder+"/"+iFile
                        print(FileLocation)
                        df_tmp= pd.concat([df_tmp, pd.read_csv(FileLocation,low_memory=False)])
                        df_list={scheme : df_tmp}
UC_Op=df_list['uc']
hosp_codes_full=pd.read_excel("assets/health_office_excel.xlsx")
hosp_codes=hosp_codes_full[['รหัส 5 หลัก','รหัสจังหวัด', 'จังหวัด', 'รหัสอำเภอ', 'อำเภอ/เขต', 'รหัสตำบล','ตำบล/แขวง']].rename(columns={'รหัส 5 หลัก':'CODE5','รหัสจังหวัด':'ADM1_PCODE','จังหวัด':'ADM1_TH','รหัสอำเภอ':'ADM2_PCODE','อำเภอ/เขต':'ADM2_TH','รหัสตำบล':'ADM3_PCODE','ตำบล/แขวง':'ADM3_TH'})
icd_codes_full=pd.read_excel("assets/ICD_Detail.xlsx")
icd_codes=icd_codes_full[['CODE','SHORT DESCRIPTION (VALID ICD-10 FY2024)']].rename(columns={'SHORT DESCRIPTION (VALID ICD-10 FY2024)':'Disease'})


UC_Op_Count=UC_Op.groupby(['pdx','hcode']).agg({'pid': 'count'}).rename(columns={'pid':'N'}).reset_index()
OPD_df=UC_Op_Count.merge(icd_codes,left_on='pdx',right_on='CODE').merge(hosp_codes,left_on='hcode',right_on='CODE5')
OPD_InitialDistrict=OPD_df[['ADM2_TH','ADM2_PCODE']].sort_values('ADM2_PCODE')['ADM2_TH'].iloc[0]
OPD_InitialSubdistrict=OPD_df[['ADM3_TH','ADM3_PCODE']].sort_values('ADM3_PCODE')['ADM3_TH'].iloc[0]

IPD_df=UC_Op_Count.merge(icd_codes,left_on='pdx',right_on='CODE').merge(hosp_codes,left_on='hcode',right_on='CODE5')
IPD_InitialDistrict=IPD_df[['ADM2_TH','ADM2_PCODE']].sort_values('ADM2_PCODE')['ADM2_TH'].iloc[0]
IPD_InitialSubdistrict=IPD_df[['ADM3_TH','ADM3_PCODE']].sort_values('ADM3_PCODE')['ADM3_TH'].iloc[0]

CDC_df=UC_Op_Count.merge(icd_codes,left_on='pdx',right_on='CODE').merge(hosp_codes,left_on='hcode',right_on='CODE5')
CDC_InitialDistrict=CDC_df[['ADM2_TH','ADM2_PCODE']].sort_values('ADM2_PCODE')['ADM2_TH'].iloc[0]
CDC_InitialSubdistrict=CDC_df[['ADM3_TH','ADM3_PCODE']].sort_values('ADM3_PCODE')['ADM3_TH'].iloc[0]

DS_df=UC_Op_Count.merge(icd_codes,left_on='pdx',right_on='CODE').merge(hosp_codes,left_on='hcode',right_on='CODE5')
DS_InitialDistrict=DS_df[['ADM2_TH','ADM2_PCODE']].sort_values('ADM2_PCODE')['ADM2_TH'].iloc[0]
DS_InitialSubdistrict=DS_df[['ADM3_TH','ADM3_PCODE']].sort_values('ADM3_PCODE')['ADM3_TH'].iloc[0]

BOD_df=UC_Op_Count.merge(icd_codes,left_on='pdx',right_on='CODE').merge(hosp_codes,left_on='hcode',right_on='CODE5')
BOD_InitialDistrict=BOD_df[['ADM2_TH','ADM2_PCODE']].sort_values('ADM2_PCODE')['ADM2_TH'].iloc[0]
BOD_InitialSubdistrict=BOD_df[['ADM3_TH','ADM3_PCODE']].sort_values('ADM3_PCODE')['ADM3_TH'].iloc[0]

GH_df=UC_Op_Count.merge(icd_codes,left_on='pdx',right_on='CODE').merge(hosp_codes,left_on='hcode',right_on='CODE5')
GH_InitialDistrict=GH_df[['ADM2_TH','ADM2_PCODE']].sort_values('ADM2_PCODE')['ADM2_TH'].iloc[0]
GH_InitialSubdistrict=GH_df[['ADM3_TH','ADM3_PCODE']].sort_values('ADM3_PCODE')['ADM3_TH'].iloc[0]