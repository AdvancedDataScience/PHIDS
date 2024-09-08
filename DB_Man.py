import pandas as pd
import os
import numpy as np
from dateutil.relativedelta import relativedelta
DataDirectory="assets/all_schemes/trat/"
#Section 0:
#Prepare functions
print("LOADDDD MEEEEE")
pd.options.mode.chained_assignment = None
SelectedColumns=['tran_id','scheme', 'hcode', 'pid', 'sex',
       'pdx', 'sdx1', 'sdx2', 'sdx3', 'sdx4', 'sdx5', 'sdx6', 'sdx7', 'sdx8',
       'sdx9', 'sdx10', 'sdx11', 'proc1', 'proc2', 'proc3', 'proc4', 'proc5',
       'proc6', 'proc7', 'proc8', 'proc9', 'proc10', 'proc11', 'proc12',
       'proc13', 'proc14', 'proc15', 'proc16', 'proc17', 'proc18', 'proc19', 'age_year', 'age_month', 'age_day', ]


def AgeAtVisitDF(df_tmp):
    try:
        result=relativedelta(pd.to_datetime(df_tmp['date_serv']), pd.to_datetime(df_tmp['dob']))
        return result.years,result.months,result.days
    except ValueError:
        return np.nan,np.nan,np.nan
def ToEngYear(x):
    return x-543
#Section 1:
hosp_codes_full=pd.read_excel("assets/health_office_excel.xlsx")
hosp_codes=hosp_codes_full[['รหัส 5 หลัก','รหัสจังหวัด', 'จังหวัด', 'รหัสอำเภอ', 'อำเภอ/เขต', 'รหัสตำบล','ตำบล/แขวง']].rename(columns={'รหัส 5 หลัก':'CODE5','รหัสจังหวัด':'ADM1_PCODE','จังหวัด':'ADM1_TH','รหัสอำเภอ':'ADM2_PCODE','อำเภอ/เขต':'ADM2_TH','รหัสตำบล':'ADM3_PCODE','ตำบล/แขวง':'ADM3_TH'})
icd_codes_full=pd.read_excel("assets/ICD_Detail.xlsx")
icd_codes=icd_codes_full[['CODE','SHORT DESCRIPTION (VALID ICD-10 FY2024)']].rename(columns={'SHORT DESCRIPTION (VALID ICD-10 FY2024)':'Disease'})
#Section 2:
#2.1 OPD Data
CreateFile=False
if(CreateFile):
      #Loading in around 2 minutes.
      UC_Files=os.listdir(DataDirectory)
      df_list={}
      fl_uc=pd.DataFrame()
      Folder='op'
      Files=os.listdir(DataDirectory+Folder)
      if(len(Files)>0):
            print(Folder)
            Files.sort()
            for iFile in Files:
                  scheme=iFile.split("_")[0]
                  if(scheme=='uc'):
                        FileLocation=DataDirectory+Folder+"/"+iFile
                        print(FileLocation)
                        fl_uc= pd.concat([fl_uc, pd.read_csv(FileLocation,low_memory=False)])
                        fl_uc['scheme']='uc'
                        df_list={scheme : fl_uc}
                  elif(scheme=='sss'):
                        FileLocation=DataDirectory+Folder+"/"+iFile
                        print(FileLocation)
                        fl_sss=pd.read_csv(FileLocation,sep="\t",low_memory=False).rename(str.lower, axis='columns').rename(columns={'tsid':'tran_id','cpid':'pid'})
                        fl_sss[["age_year", "age_month",'age_day']] = fl_sss.apply(AgeAtVisitDF, axis=1, result_type="expand")
                        fl_sss['scheme']='sss'
                        df_list={scheme : fl_sss}
                  elif(scheme=='csmbs'):
                        FileLocation=DataDirectory+Folder+"/"+iFile
                        print(FileLocation)
                        fl_csmbs=pd.read_csv(FileLocation,sep="\t",low_memory=False).rename(str.lower, axis='columns').rename(columns={'tsid':'tran_id','cpid':'pid'})
                        fl_csmbs['date_serv_d']=fl_csmbs['date_serv_d'].apply(str);fl_csmbs['date_serv_m']=fl_csmbs['date_serv_m'].apply(str);fl_csmbs['date_serv_y']=fl_csmbs['date_serv_y'].apply(str)
                        fl_csmbs['date_serv'] = fl_csmbs['date_serv_d']+"/" + fl_csmbs['date_serv_m']+"/" + fl_csmbs['date_serv_y']
                        fl_csmbs['dob_d']=fl_csmbs['dob_d'].apply(str);fl_csmbs['dob_m']=fl_csmbs['dob_m'].apply(str);fl_csmbs['dob_y']=fl_csmbs['dob_y'].apply(str)
                        fl_csmbs['dob'] = fl_csmbs['dob_d']+"/" + fl_csmbs['dob_m']+"/" + fl_csmbs['dob_y']
                        fl_csmbs[["age_year", "age_month",'age_day']] = fl_csmbs.apply(AgeAtVisitDF, axis=1, result_type="expand")
                        fl_csmbs['scheme']='csmbs'
                        df_list={scheme : fl_csmbs}
            uc_op_selected=fl_uc[SelectedColumns]
            sss_op_selected=fl_csmbs[SelectedColumns]
            csmbs_op_selected=fl_csmbs[SelectedColumns]
            op_all=pd.concat([uc_op_selected,sss_op_selected,csmbs_op_selected])
            print("UC shape={},SSS shape={},CSMBS shape={},Overall shape={}".format(uc_op_selected.shape,sss_op_selected.shape,csmbs_op_selected.shape,op_all.shape))
            op_all['tran_id']=op_all.index
            op_all.loc[(op_all['sex'] != 1) & (op_all['sex'] != 2),'sex']=np.nan
            op_all.to_pickle(DataDirectory +'op/op.pkl.zip', compression='zip')
else:
     #read file
     #load in 12 sec.
     op_all=pd.read_pickle(DataDirectory +'op/op.pkl.zip', compression='zip')
     print(op_all.shape)
     #print("Loaded file: UC shape={},SSS shape={},CSMBS shape={},Overall shape={}".format(sum(op_all['scheme']=='uc'),sum(op_all['scheme']=='sss'),sum(op_all['scheme']=='csmbs')))
            

UC_Op_Count=op_all.groupby(['pdx','hcode']).agg({'pid': 'count'}).rename(columns={'pid':'N'}).reset_index()
OPD_df=UC_Op_Count.merge(icd_codes,left_on='pdx',right_on='CODE',how='left').merge(hosp_codes,left_on='hcode',right_on='CODE5')
OPD_InitialDistrict=OPD_df[['ADM2_TH','ADM2_PCODE']].sort_values('ADM2_PCODE')['ADM2_TH'].iloc[0]
OPD_InitialSubdistrict=OPD_df[['ADM3_TH','ADM3_PCODE']].sort_values('ADM3_PCODE')['ADM3_TH'].iloc[0]

#IP SECTION-------------------------------------------------------


#dischs: สถานภาพการจำหน่าย ใช้รหัส 1=complete recovery 2=improved 3=not improved 4=normal delivery 5= un-delivery 6=normal child d/c with mother 7=normal child d/c separately 8=stillbirth 9=dead
#discht:ประเภทการจำหน่าย ใช้รหัส 1=with approval 2=against advice 3=escape 4=by transfer 5=other 8=dead autopsy 9=dead no autopsy
ip_SelectedColumns=['tran_id','scheme', 'hcode', 'pid', 'sex','los','dischs','discht', 'pdx', 'sdx1',
       'sdx2', 'sdx3', 'sdx4', 'sdx5', 'sdx6', 'sdx7', 'sdx8', 'sdx9', 'sdx10',
       'sdx11', 'sdx12', 'sdx13', 'sdx14', 'sdx15', 'sdx16', 'sdx17', 'sdx18',
       'sdx19', 'sdx20', 'proc1', 'proc2', 'proc3', 'proc4', 'proc5',
       'proc6', 'proc7', 'proc8', 'proc9', 'proc10', 'proc11', 'proc12',
       'proc13', 'proc14', 'proc15', 'proc16', 'proc17', 'proc18', 'proc19', 'age_year', 'age_month', 'age_day']
if(CreateFile):
      Folder = 'ip'
      DataDirectory="assets/all_schemes/trat/"
      #IP_UC
      iFile='uc_ip_1.csv'
      FileLocation=DataDirectory+Folder+"/"+iFile #print(FileLocation)
      ip_uc= pd.read_csv(FileLocation,low_memory=False)
      ip_uc['scheme']='uc' #print(ip_uc.columns)
      #IP_SSS
      iFile='sss_ip_1.csv'
      FileLocation=DataDirectory+Folder+"/"+iFile #print(FileLocation)
      ip_sss= pd.read_csv(FileLocation,sep="\t",low_memory=False).rename(str.lower, axis='columns').rename(columns={'tsid':'tran_id','cpid':'pid','dateadm':'date_serv'})
      ip_sss[["age_year", "age_month",'age_day']] = ip_sss.apply(AgeAtVisitDF, axis=1, result_type="expand")
      ip_sss['scheme']='sss' #print(ip_sss.columns)
      #IP_CSMBS
      iFile='csmbs_ip_1.csv'
      FileLocation=DataDirectory+Folder+"/"+iFile #print(FileLocation)
      ip_csmbs= pd.read_csv(FileLocation,sep="\t",low_memory=False).rename(str.lower, axis='columns').rename(columns={'tsid':'tran_id','cpid':'pid'})
      ip_csmbs['dateadm_d']=ip_csmbs['dateadm_d'].apply(str);ip_csmbs['dateadm_m']=ip_csmbs['dateadm_m'].apply(str);ip_csmbs['dateadm_y']=ip_csmbs['dateadm_y'].apply(str)
      ip_csmbs['date_serv'] = ip_csmbs['dateadm_d']+"/" + ip_csmbs['dateadm_m']+"/" + ip_csmbs['dateadm_y']
      ip_csmbs['dob_d']=ip_csmbs['dob_d'].apply(str);ip_csmbs['dob_m']=ip_csmbs['dob_m'].apply(str);ip_csmbs['dob_y']=ip_csmbs['dob_y'].apply(str)
      ip_csmbs['dob'] = ip_csmbs['dob_d']+"/" + ip_csmbs['dob_m']+"/" + ip_csmbs['dob_y']
      ip_csmbs[["age_year", "age_month",'age_day']] = ip_csmbs.apply(AgeAtVisitDF, axis=1, result_type="expand")
      ip_csmbs['scheme']='csmbs' #print(ip_csmbs.columns)
      #IP_SELECTED_AND_CONCATRENATE
      ip_uc_selected=ip_uc[ip_SelectedColumns]
      ip_sss_selected=ip_sss[ip_SelectedColumns]
      ip_csmbs_selected=ip_csmbs[ip_SelectedColumns]
      ip_all=pd.concat([ip_uc_selected,ip_sss_selected,ip_csmbs_selected])
      print("UC shape={},SSS shape={},CSMBS shape={},Overall shape={}".format(ip_uc_selected.shape,ip_sss_selected.shape,ip_csmbs_selected.shape,ip_all.shape))
      ip_all['tran_id']=ip_all.index
      ip_all.loc[(ip_all['sex'] != 1) & (ip_all['sex'] != 2),'sex']=np.nan
      ip_all.to_pickle(DataDirectory +'ip/ip.pkl.zip', compression='zip')
      #load in 2 sec
else:
     #read file
     #load in 12 sec.
     ip_all=pd.read_pickle(DataDirectory +'ip/ip.pkl.zip', compression='zip')
     print(ip_all.shape)
     #print("Loaded file: UC shape={},SSS shape={},CSMBS shape={},Overall shape={}".format(sum(op_all['scheme']=='uc'),sum(op_all['scheme']=='sss'),sum(op_all['scheme']=='csmbs')))

All_IP_Count=ip_all.groupby(['pdx','hcode']).agg({'pid': 'count'}).rename(columns={'pid':'N'}).reset_index()
IPD_df=All_IP_Count.merge(icd_codes,left_on='pdx',right_on='CODE').merge(hosp_codes,left_on='hcode',right_on='CODE5')
IPD_InitialDistrict=IPD_df[['ADM2_TH','ADM2_PCODE']].sort_values('ADM2_PCODE')['ADM2_TH'].iloc[0]
IPD_InitialSubdistrict=IPD_df[['ADM3_TH','ADM3_PCODE']].sort_values('ADM3_PCODE')['ADM3_TH'].iloc[0]
#CDC SECTION------------------------------------------------------
CDC_ICD_RANGE=['A052', 'A053', 'A054', 'A030', 'A031', 'A032', 'A033', 'A060', 'A061', 'A062', 'A063', 'A064', 'A065', 'A066', 'A067', 'A068', 'A069', 'A011', 'A012', 'A013', 'A014', 'J100', 'J101', 'J102', 'J103', 'J104', 'J105', 'J106', 'J107', 'J108', 'J109', 'J110', 'J111', 'J112', 'J113', 'J114', 'J115', 'J116', 'J117', 'J118', 'J119', 'J120', 'J121', 'J122', 'J123', 'U071', 'U072', 'B010', 'B011', 'B012', 'A800', 'A801', 'A802', 'A803', 'A804', 'B050', 'B051', 'B052', 'B053', 'B054', 'A360', 'A361', 'A362', 'A363', 'B260', 'B261', 'B262', 'B263', 'A392', 'A393', 'A394', 'A395', 'A831', 'A832', 'A833', 'A834', 'A835', 'A878', 'A879', 'B508', 'B509', 'A750', 'A751', 'A752', 'A753', 'A500', 'A501', 'A502', 'A503', 'A504', 'A505', 'A506', 'A507', 'A540', 'A541', 'A542', 'A543', 'A544', 'A545', 'A546', 'A560', 'A561', 'A562', 'A563', 'A564', 'A600', 'A601', 'B160', 'B161', 'B162', 'A241', 'A242', 'A243', 'A244', 'A221', 'A222', 'A231', 'A232', 'A233', 'A058', 'A059', 'A038', 'A039', 'J128', 'J129', 'B018', 'B019', 'A368', 'A369', 'B268', 'B269', 'A398', 'A399', 'A838', 'A839', 'B518', 'B519', 'A510', 'A511', 'A512', 'A513', 'A514', 'A515', 'A548', 'A549', 'N341', 'N342', 'N343', 'A227', 'A228', 'A229', 'A238', 'A239', 'J170', 'J171', 'A840', 'A841', 'B528', 'B529', 'A520', 'A521', 'A522', 'A523', 'J180', 'J181', 'J182', 'A848', 'A849', 'A527', 'A528', 'A529', 'J188', 'J189', 'A850', 'A851', 'A852', 'G048', 'G049']
CDC_ICD_SPOTS=['A000','A020','A010','B660','A051','T620','B150','B172','J13','U109','B06','A809','B059','B058','A370','A34','A830','A33','P350','A390','A858','G00','A970','A911','A910','A972','B500','A759','A90','A979','A920','A925','A509','A530','K671','A568','A57','A55','A609','A630','B169','B171','B170','B084','A850','B04','A820','A270','A220','B75','A408','A230','J09','A001','A021','B159','J14','B069','A379','A35','A86','G009','A971','B510','A519','A539','M730','A638','B085','A870','A821','A278','A009','A022','J15J160','B060','B004','G020','B520','O981','N743','B341','A829','A279','A028','J168','B068','G051','G030','B530','A029','J851','G038','B531','A050','A481','G039','B538','A329','B54']
CDC_ICD_LIST=set(CDC_ICD_RANGE+CDC_ICD_SPOTS)
op_cdc=op_all[op_all['pdx'].isin(CDC_ICD_LIST)]
All_CDC_Count=op_cdc.groupby(['pdx','hcode']).agg({'pid': 'count'}).rename(columns={'pid':'N'}).reset_index()
CDC_df=All_CDC_Count.merge(icd_codes,left_on='pdx',right_on='CODE').merge(hosp_codes,left_on='hcode',right_on='CODE5')
CDC_InitialDistrict=CDC_df[['ADM2_TH','ADM2_PCODE']].sort_values('ADM2_PCODE')['ADM2_TH'].iloc[0]
CDC_InitialSubdistrict=CDC_df[['ADM3_TH','ADM3_PCODE']].sort_values('ADM3_PCODE')['ADM3_TH'].iloc[0]
#Dead stat--------------------------------------------------------
if(CreateFile):
      Folder = 'ds'
      DataDirectory="assets/all_schemes/trat/"
      iFiles=['death_thai_64.xlsx','death_thai_65.xlsx','death_thai_66.xlsx']
      ds_all=pd.DataFrame()
      SheetDict={'อ.เมือง':10696, 'อ.คลองใหญ่':10845, 'อ.เขาสมิง':10846, 'อ.บ่อไร่':10847, 'อ.แหลมงอบ':10848, 'อ.เกาะกูด':10849, 'อ.เกาะช้าง':13816}

      for iFile in iFiles:
            FileLocation=DataDirectory+Folder+"/"+iFile #print(FileLocation)
            xl = pd.ExcelFile(FileLocation)
            SheetList=xl.sheet_names  # see all sheet names
            for i in SheetList:
                  iFL=pd.read_excel(FileLocation,sheet_name=i)
                  iFL['hcode']=SheetDict[i]
                  iFL.rename(columns={'NCAUSE':'pdx','total':'N'},inplace=True)
                  ds_all=pd.concat([ds_all,iFL],axis=0)
      ds_all['serv_year']=ds_all['YEAR'].apply(ToEngYear)
      iFile="ds.pkl.zip"
      FileLocation=DataDirectory+Folder+"/"+iFile #print(FileLocation)
      ds_all.to_pickle(FileLocation, compression='zip')
else:
      ds_all=pd.read_pickle(DataDirectory +'ds/ds.pkl.zip', compression='zip')

DS_df=ds_all.merge(hosp_codes,left_on='hcode',right_on='CODE5')
DS_df.rename(columns={'pdx':'CODE','diseasethai':'Disease'},inplace=True)
DS_InitialDistrict=DS_df[['ADM2_TH','ADM2_PCODE']].sort_values('ADM2_PCODE')['ADM2_TH'].iloc[0]
DS_InitialSubdistrict=DS_df[['ADM3_TH','ADM3_PCODE']].sort_values('ADM3_PCODE')['ADM3_TH'].iloc[0]
#BOD stat---------------------------------------------------------
BOD_df=UC_Op_Count.merge(icd_codes,left_on='pdx',right_on='CODE').merge(hosp_codes,left_on='hcode',right_on='CODE5')
BOD_InitialDistrict=BOD_df[['ADM2_TH','ADM2_PCODE']].sort_values('ADM2_PCODE')['ADM2_TH'].iloc[0]
BOD_InitialSubdistrict=BOD_df[['ADM3_TH','ADM3_PCODE']].sort_values('ADM3_PCODE')['ADM3_TH'].iloc[0]
#GH Stat----------------------------------------------------------

Folder = 'gh'
DataDirectory="assets/all_schemes/trat/"
#IP_UC
iFile='refer17_24.csv'
FileLocation=DataDirectory+Folder+"/"+iFile #print(FileLocation)
gh_refer= pd.read_csv(FileLocation,low_memory=False)
All_GH_Count=gh_refer.groupby(['pdx','hcode']).agg({'pid': 'count'}).rename(columns={'pid':'N'}).reset_index()
GH_df=All_GH_Count.merge(icd_codes,left_on='pdx',right_on='CODE').merge(hosp_codes,left_on='hcode',right_on='CODE5')
GH_InitialDistrict=GH_df[['ADM2_TH','ADM2_PCODE']].sort_values('ADM2_PCODE')['ADM2_TH'].iloc[0]
GH_InitialSubdistrict=GH_df[['ADM3_TH','ADM3_PCODE']].sort_values('ADM3_PCODE')['ADM3_TH'].iloc[0]