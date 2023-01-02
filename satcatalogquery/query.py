import numpy as np
import pandas as pd
from os import path,mkdir,makedirs
from pathlib import Path
import requests
from datetime import datetime
from time import sleep
from colorama import Fore

from . import Const
from . import data_prepare
from .satcatclass import SatCatlog


def _discos_buildin_filter(params,expr):
    """
    A buildin function associated to the function discos_query. 

    Inputs:
    params -> [dictionary] params in function discos_query
    expr -> [str] filter expressions for DISCOS, for example, "eq(reentry.epoch,null)". 

    Outputs:
    params_upgrade -> [dictionary] upgraded variable params in function discos_query    

    For more infomation, please reference to https://discosweb.esoc.esa.int/apidocs

    """
    if 'filter' in params.keys(): 
        params['filter'] += '&(' + expr + ')'
    else:
        params['filter'] = expr 
    return params  

def discos_query(COSPAR_ID=None,NORAD_ID=None,OBJECT_CLASS=None,PAYLOAD=None,DECAYED=None,DECAY_DATE=None,MASS=None,SHAPE=None,LENGTH=None,HEIGHT=None,DEPTH=None,RCSMin=None,RCSMax=None,RCSAvg=None,sort=None):
    """
    Query space targets by setting a series of specific parameters from the [DISCOS](https://discosweb.esoc.esa.int)(Database and Information System Characterising Objects in Space) database.

    Usage: 
    satcatlog = discos_query(DECAYED=False,RCSAvg=[5,15])

    Parameters:
    COSPAR_ID -> [str or list of str, optional, default = None] Target IDs by the in Committee On SPAce Research; if None, this option is ignored. 
    NORAD_ID -> [int, str, list, or filename(such as noradids.txt), optional, default = None] Target IDs by the North American Aerospace Defense Command; if None, this option is ignored.
    OBJECT_CLASS -> [str or list of str, optional, default = None] Classification of targets; avaliable options include 'Payload', 'Payload Debris', 'Payload Fragmentation Debris', 
    'Payload Mission Related Object', 'Rocket Body', 'Rocket Debris', 'Rocket Fragmentation Debris', 'Rocket Mission Related Object', 'Other Mission Related Object','Other Debris', Unknown', or any combination of them, 
    for examle, ['Rocket Body', 'Rocket Debris', 'Rocket Fragmentation Debris']; If None, this option is ignored.  
    PAYLOAD -> [bool, optional, default  = None] Identify whether a target belongs to payload or not. If True, payload; if False, non-payload; if None, this option is ignored.
    DECAYED -> [bool, optional, default = None] it also called reentry; If False, targets are still in orbit by now; if True, then reentry; if None, this option is ignored.
    DECAY_DATE -> [list of str with 2 elemnts, optional, default = None] Date of reentry; it must be in form of ['date1','date2'], such as ['2019-01-05','2020-05-30']; if None, then this option is ignored.
    MASS -> [list of float with 2 elemnts, optional, default = None] Mass[kg] of a target; it must be in form of [m1,m2], such as [5.0,10.0]; if None, this option is ignored.
    SHAPE -> [str or list of str, optional, default = None] Shape of targets; commonly used options include 'Cyl', 'Sphere', 'Cone', 'Dcone', Pan', 'Ell', 'Dish', 'Cable', 'Box', 'Rod', 'Poly', 'Sail', 'Ant', 
    'Frust', 'Truss', 'Nozzle', and 'lrr'. Any combinations of them are also supported, for examle, ['Cyl', 'Sphere', 'Pan'] means 'or', and ['Cyl', 'Sphere', 'Pan', '+'] means 'and'; If None, this option is ignored.  
    LENGTH -> [list of float with 2 elemnts, optional, default = None] Length[m] of a target; it must be in form of [l1,l2], such as [5.0,10.0]; if None, this option is ignored.
    HEIFHT -> [list of float with 2 elemnts, optional, default = None] Height[m] of a target; it must be in form of [h1,h2], such as [5.0,10.0]; if None, this option is ignored.
    DEPTH -> [list of float with 2 elemnts, optional, default = None] Depth[m] of a target; it must be in form of [d1,d2], such as [5.0,10.0]; if None, this option is ignored.
    RCSMin -> [list of float with 2 elemnts, optional, default = None] Minimum Radar Cross Section[m2] of a target; it must be in form of [RCS1,RCS2], such as [0.5,2.0]; if None, this option is ignored.
    RCSMax -> [list of float with 2 elemnts, optional, default = None] Maximum Radar Cross Section[m2] of a target; it must be in form of [RCS1,RCS2], such as [10.0,100.0]; if None, this option is ignored.
    RCSAvg -> [list of float with 2 elemnts, optional, default = None] Average Radar Cross Section[m2] of a target; it must be in form of [RCS1,RCS2], such as [5,20]; if None, this option is ignored.
    sort -> [str, optional, default = None] sort by features of targets in a specific order, such as by mass; avaliable options include 'COSPARID', NORADID', 'ObjectClass', 'DecayDate', 'Mass', 'Shape', 'Length', 'Height', 'Depth', 'RCSMin', 'RSCMax', and 'RCSAvg'.
    If there is a negative sign '-' ahead, such as "-Mass", it will be sorted in descending order. If None, then sort by NORADID by default.
    
    Outputs:
    satcatlog -> instance of class SatCatlog
    """
    # DISCOS tokens
    home = str(Path.home())
    direc = home + '/src/discos-data/'
    tokenfile = direc + 'discos-token'

    if not path.exists(direc): makedirs(direc)
    if not path.exists(tokenfile):
        token = input('Please input the DISCOS tokens(which can be achieved from https://discosweb.esoc.esa.int/tokens): ')
        outfile_token = open(tokenfile,'w')
        outfile_token.write(token)
        outfile_token.close()
    else:
        infile = open(tokenfile,'r')
        token = infile.readline()
        infile.close()
    
    URL = 'https://discosweb.esoc.esa.int'
    params = {}
    
    # Filter parameters for 'ObjectClass' 
    if OBJECT_CLASS is not None:
        if type(OBJECT_CLASS) is str:
            params['filter'] = "eq(objectClass,'{:s}')".format(OBJECT_CLASS)
        elif type(OBJECT_CLASS) is list:
            params_filter = []
            for element in OBJECT_CLASS:
                params_filter.append("eq(objectClass,'{:s}')".format(element))
            params['filter'] = '(' + '|'.join(params_filter) + ')'
        else:
            raise Exception('Type of ObjectClass should be either string or list.')  

    # Set Payload based on ObjectClass
    if PAYLOAD is not None:
        if PAYLOAD is True:
            PayloadtoObjectClass = ['Payload','Payload Mission Related Object','Rocket Mission Related Object','Other Mission Related Object','Unknown']
        elif PAYLOAD is False:
            PayloadtoObjectClass = ['Payload Debris', 'Payload Fragmentation Debris','Rocket Body','Rocket Debris','Rocket Fragmentation Debris','Other Debris']
        else:
            raise Exception('Type of Payload should be either None, True or False.')  

        params_filter = []
        for element in PayloadtoObjectClass:
            params_filter.append("eq(objectClass,'{:s}')".format(element))
            temp = '(' + '|'.join(params_filter) + ')'
        params = _discos_buildin_filter(params,temp)    

    # Set Decayed based on reentry.epoch 
    if DECAYED is not None:
        if DECAYED is False:
            temp = "eq(reentry.epoch,null)"
        elif DECAYED is True:
            temp = "ne(reentry.epoch,null)"
        else:
            raise Exception("'Decayed' must be one of 'False', 'True', or 'None'.")  
        params = _discos_buildin_filter(params,temp)     

    # Filter parameters for 'DECAY_DATE'
    if DECAY_DATE is not None:
        temp = "ge(reentry.epoch,epoch:'{:s}')&le(reentry.epoch,epoch:'{:s}')".format(DECAY_DATE[0],DECAY_DATE[1])
        params = _discos_buildin_filter(params,temp)
    
    # Filter parameters for 'COSPAR_ID'
    if COSPAR_ID is not None:
        if type(COSPAR_ID) is str:
            temp = "eq(cosparId,'{:s}')".format(COSPAR_ID)
        elif type(COSPAR_ID) is list:    
            temp = 'in(cosparId,{:s})'.format(str(tuple(COSPAR_ID))).replace(' ', '')
        else:
            raise Exception('Type of COSPAR_ID should be in str or list of str.')
        params = _discos_buildin_filter(params,temp)    
            
    # Filter parameters for 'NORAD_ID'        
    if NORAD_ID is not None:
        if type(NORAD_ID) is list:   
            temp = 'in(satno,{:s})'.format(str(tuple(NORAD_ID))).replace(' ', '')  
        elif type(NORAD_ID) is str:  
            if '.' in NORAD_ID: 
                NORAD_ID = list(np.loadtxt(NORAD_ID,dtype = str))
                temp = 'in(satno,{:s})'.format(str(tuple(NORAD_ID))).replace(' ', '')  
            else:    
                temp = 'eq(satno,{:s})'.format(NORAD_ID)  
        elif type(NORAD_ID) is int: 
            temp = 'eq(satno,{:s})'.format(str(NORAD_ID))           
        else:
            raise Exception('Type of NORAD_ID should be in int, str, list of int, or list of str.') 
        params = _discos_buildin_filter(params,temp)  
            
    # Filter parameters for 'Mass'            
    if MASS is not None:
        temp = 'ge(mass,{:.2f})&le(mass,{:.2f})'.format(MASS[0],MASS[1])
        params = _discos_buildin_filter(params,temp)

    # Filter parameters for 'Shape' 
    if SHAPE is not None:
        if type(SHAPE) is str:
            temp = "icontains(shape,'{:s}')".format(SHAPE)
        elif type(SHAPE) is list:
            shape_filter = []
            end_symbol = SHAPE[-1]
            if end_symbol == '+':
                for element in SHAPE[:-1]:
                    shape_filter.append("icontains(shape,'{:s}')".format(element))
                temp = '&'.join(shape_filter)
            else:
                for element in SHAPE:
                    shape_filter.append("icontains(shape,'{:s}')".format(element))
                temp = '|'.join(shape_filter)
        else:
            raise Exception('Type of Shape should either be string or list.')
        params = _discos_buildin_filter(params,temp)   

    # Filter parameters for 'Length'            
    if LENGTH is not None:
        temp = 'ge(length,{:.2f})&le(length,{:.2f})'.format(LENGTH[0],LENGTH[1])
        params = _discos_buildin_filter(params,temp)  
            
    # Filter parameters for 'Height'            
    if HEIGHT is not None:
        temp = 'ge(height,{:.2f})&le(height,{:.2f})'.format(HEIGHT[0],HEIGHT[1])
        params = _discos_buildin_filter(params,temp)
            
    # Filter parameters for 'Depth'            
    if DEPTH is not None:
        temp = 'ge(depth,{:.2f})&le(depth,{:.2f})'.format(DEPTH[0],DEPTH[1])   
        params = _discos_buildin_filter(params,temp)                     

    # Filter parameters for 'RCSMin'            
    if RCSMin is not None:
        temp = 'ge(xSectMin,{:.4f})&le(xSectMin,{:.4f})'.format(RCSMin[0],RCSMin[1])
        params = _discos_buildin_filter(params,temp)
            
    # Filter parameters for 'RCSMax'     
    if RCSMax is not None:
        temp = 'ge(xSectMax,{:.4f})&le(xSectMax,{:.4f})'.format(RCSMax[0],RCSMax[1])
        params = _discos_buildin_filter(params,temp)
            
    # Filter parameters for 'RCSAvg'     
    if RCSAvg is not None:
        temp = 'ge(xSectAvg,{:.4f})&le(xSectAvg,{:.4f})'.format(RCSAvg[0],RCSAvg[1])
        params = _discos_buildin_filter(params,temp)
    
    # Sort in ascending order       
    if sort is None:    
        params['sort'] = 'satno'  
    else:
        if sort.__contains__('COSPAR_ID'):
            params['sort'] = 'cosparId'
        elif sort.__contains__('NORAD_ID'):
            params['sort'] = 'satno'    
        elif sort.__contains__('OBJECT_CLASS'):
            params['sort'] = 'objectClass'  
        elif sort.__contains__('MASS'):
            params['sort'] = 'mass'    
        elif sort.__contains__('SHAPE'):
            params['sort'] = 'shape'
        elif sort.__contains__('LENGTH'):
            params['sort'] = 'length'   
        elif sort.__contains__('HEIGHT'):
            params['sort'] = 'height'
        elif sort.__contains__('DEPTH'):
            params['sort'] = 'depth'
        elif sort.__contains__('RCSMin'):
            params['sort'] = 'xSectMin'
        elif sort.__contains__('RSCMax'):
            params['sort'] = 'xSectMax' 
        elif sort.__contains__('RCSAvg'):
            params['sort'] = 'xSectAvg'  
        elif sort.__contains__('DECAY_DATE'):
            params['sort'] = 'reentry.epoch'
        else:
            raise Exception("Avaliable options include 'COSPAR_ID', NORAID', 'OBJECT_CLASS', 'MASS', 'SHAPE', 'LENGTH', 'HEIGHT', 'DEPTH', 'RCSMin', 'RSCMax', 'RCSAvg', and 'DECAY_DATE'. Also, a negative sign '-' can be added to the option to sort in descending order.")        
                
        # Sort in descending order
        if sort[0] == '-': params['sort'] = '-' + params['sort']

    # Initialize the page parameter 
    params['page[number]'] = 1
    extract = []
    
    while True:
        params['page[size]'] = 100 # Number of entries on each page   
        response = requests.get(f'{URL}/api/objects',headers = {'Authorization': f'Bearer {token}'},params = params)
        doc = response.json()

        if response.ok:
            if not doc['data']: raise Exception('No entries found, please reset the filter parameters.')
            data = doc['data']
            for element in data:
                extract.append(element['attributes'])
            currentPage = doc['meta']['pagination']['currentPage']
            totalPages = doc['meta']['pagination']['totalPages']
            desc = 'CurrentPage {:s}{:3d}{:s} in TotalPages {:3d}'.format(Fore.GREEN,currentPage,Fore.RESET,totalPages)
            print(desc,end='\r')
            
            if currentPage < totalPages: 
                params['page[number]'] += 1
            else:
                break

            if currentPage%20 == 0: sleep(30) # Pause for 30 seconds to avoid excessive API access frequency    
        else:
            return doc['errors']
    
    # Rename the columns and readjust the order of the columns  
    old_column = ['height', 'xSectMax', 'name', 'satno', 'objectClass','mass', 'xSectMin', 'depth', 'xSectAvg', 'length', 'shape', 'cosparId']
    new_column = ['HEIGhT', 'RCSMax', 'OBJECT_NAME', 'NORAD_ID', 'OBJECT_CLASS', 'MASS', 'RCSMin[m2]', 'DEPTH', 'RCSAvg', 'LENGTH', 'SHAPE', 'COSPAR_ID']
    # units: MASS in [kg]; RCS in [m2]; DEPTH, LENGTH, and HEIGHT in [m]
    new_column_reorder = ['OBJECT_NAME','COSPAR_ID', 'NORAD_ID','OBJECT_CLASS','MASS','SHAPE','HEIGHT','LENGTH','DEPTH','RCSMin','RCSMax','RCSAvg']
    df = pd.DataFrame.from_dict(extract,dtype=object).rename(columns=dict(zip(old_column, new_column)), errors='raise')
    df = df.reindex(columns=new_column_reorder) 
    df = df.reset_index(drop=True)
    mode = 'discos_catlog'

    return SatCatlog(df,mode)   

def celestrak_query(COSPAR_ID=None,NORAD_ID=None,PAYLOAD=None,DECAYED=None,DECAY_DATE=None,PERIOD=None,INCLINATION=None,APOGEE=None,PERIGEE=None,MEAN_ALT=None,ECC=None,OWNER=None,TLE_STATUS=None,sort=None):
    """
    Query space targets that meet the requirements by setting a series of specific parameters from the [CELESTRAK](https://celestrak.com) database.

    Usage:
    satcatlog = celestrak_query(DECAYED=False,MEAN_ALT=[400,900])

    Parameters:
    COSPAR_ID     -> [str or list of str, optional, default = None] Target IDs by the in Committee On SPAce Research; if None, this option is ignored.
    NORAD_ID      -> [int, str, list, or filename(such as noradids.txt), optional, default = None] Target IDs by the North American Aerospace Defense Command; if None, this option is ignored.
    PAYLOAD       -> [bool, optional, default = None] Identify whether a target belongs to payload or not. If True, payload; if False, non-payload; if None, this option is ignored.
    DECAYED       -> [bool, optional, default = None] It also called reentry; if False, targets are still in orbit by now; if True, then reentry; if None, this option is ignored.
    DECAY_DATE    -> [list of str with 2 elemnts, optional, default = None] Date of reentry; it must be in form of ['date1','date2'], such as ['2019-01-05','2020-05-30']; if None, this option is ignored.
    PERIOD        -> [list of float with 2 elemnts, optional, default = None] Orbit period[minutes] of targets; it must be in form of [period1,period2], such as [100.0,200.0]; if None, this option is ignored.  
    INCLINATION   -> [list of float with 2 elemnts, optional, default = None] Orbit inclination[degrees] of targets; must be in form of [inc1,inc2], such as [45.0,80.0]; if None, this option is ignored.  
    APOGEE        -> [list of float with 2 elemnts, optional, default = None] Apogee Altitude[km] of targets; it must be in form of [apoalt1,apoalt2], such as [800.0,1400.0]; if None, this option is ignored.  
    PERIGEE       -> [list of float with 2 elemnts, optional, default = None] Perigee Altitude[km] of targets; it must be in form of [peralt1,peralt2], such as [300.0,400.0]; if None, this option is ignored.  
    MEAN_ALT      -> [list of float with 2 elemnts, optional, default = None] Mean Altitude[km] of targets; it must be in form of [meanalt1,meanalt2], such as [300.0,800.0]; if None, then option is ignored. 
    ECC           -> [list of float with 2 elemnts, optional, default = None] Eccentricity of targets; it must be in form of [ecc1,ecc2], such as [0.01,0.2]; if None, then option is ignored.   
    OWNER         -> [str or list of str, optional, default = None] Satellite Ownership; country codes/names can be found at http://www.fao.org/countryprofiles/iso3list/en/; if None, this option is ignored.
    TLE_STATUS    -> [bool, optional, default = None] Identify whether a TLE is valid. If True, TLE is valid; if False, No Current Elements, No Initial Elements, or No Elements Available; if None, this option is ignored.
    sort          -> [str, optional, default = None] sort by features of targets in a specific order; avaliable options include 'COSPAR_ID', NORAD_ID', 'DECAY_DATE', 'PERIOD', 'INCLINATION', 'APOGEE', 'PERIGEE', 'MEAN_ALT', 'ECC',and 'OWNER'.
    If there is a negative sign '-' ahead, such as "-DecayDate", it will be sorted in descending order. If None, then sort by NORADID by default.
    
    Outputs:
    satcatlog -> instance of class SatCatlog
    """

    satcat_file = data_prepare.sc_file

    data = pd.read_csv(satcat_file) 
    columns_dict = {'OBJECT_ID': 'COSPAR_ID', 'NORAD_CAT_ID': 'NORAD_ID'}
    data.rename(columns=columns_dict, inplace=True)
    # unit description : 'PERIOD' in [min],'INCLINATION' in [deg], 'APOGEE' in [km],'PERIGEE' in [km],'RCS' in [m2]

    '''
    # For .txt file
    # Set the field width according to the SATCAT Format Documentation[https://celestrak.com/satcat/satcat-format.php]
    set_colspecs = [(0,11),(13,18),(20,21),(21,22),(23,47),(49,54),(56,66),(68,73),\
                    (75,85),(87,94),(96,101),(103,109),(111,117),(119,127),(129,132)]
    data = pd.read_fwf(satcat_file, colspecs = set_colspecs, header = None) 

    data.columns = ['COSPAR_ID', 'NORAD_ID','OBJECT_TYPE','OPS_STATUS_CODE','OBJECT_NAME',\
                    'OWNER','LAUNCH_DATE','LAUNCH_SITE','DECAY_DATE','PERIOD','INCLINATION',\
                    'APOGEE','PERIGEE','RCS','DATA_STATUS_CODE']
    '''  
    Mean_Alltitude = (data['APOGEE'] + data['PERIGEE'])/2 # Compute the mean altitude
    Eccentricity = (data['APOGEE'] - data['PERIGEE'])/(Mean_Alltitude + Const.Re_V)/2 

    # Add column to dataframe
    data['MEAN_ALT'] = Mean_Alltitude
    data['ECC'] = Eccentricity
    full_of_true = np.ones_like(Mean_Alltitude,dtype=bool)
    
    # Set filter for 'COSPAR_ID' 
    if COSPAR_ID is not None:
        if type(COSPAR_ID) in [str,list]:
            COSPARID_flag = np.in1d(data['COSPAR_ID'],COSPAR_ID,assume_unique=True)
        else:
            raise Exception('Type of COSPAR_ID should be in str or list of str.')             
    else:
        COSPARID_flag = full_of_true
    
    # Set filter for 'NORADID' 
    if NORAD_ID is not None:
        if type(NORAD_ID) is int:
            NORADID_flag = np.in1d(data['NORAD_ID'],NORAD_ID,assume_unique=True)
        elif type(NORAD_ID) is str: 
            if '.' in NORAD_ID: 
                NORAD_ID = np.loadtxt(NORAD_ID,dtype = int)  
            else:
                NORAD_ID = int(NORAD_ID)
            NORADID_flag = np.in1d(data['NORAD_ID'],NORAD_ID,assume_unique=True)
        elif type(NORAD_ID) is list:
            NORADID_list = np.array(NORAD_ID).astype(int)       
            NORADID_flag = np.in1d(data['NORAD_ID'],NORADID_list,assume_unique=True)        
        else:
            raise Exception('Type of NORAD_ID should be in int, str, list of int, or list of str.')             
    else:
        NORADID_flag = full_of_true   
    
    # Set filter for 'OBJECT_TYPE'
    Payload_flag = data['OBJECT_TYPE'] == 'PAY'

    if PAYLOAD is None:
        Payload_flag = full_of_true
    else:
        if not PAYLOAD: Payload_flag = ~Payload_flag
        
    # Set filter for 'DECAYED' 
    Decayed_flag = data['OPS_STATUS_CODE'] == 'D'

    if DECAYED is None:
        Decayed_flag = full_of_true
    else:
        if not DECAYED: Decayed_flag = ~Decayed_flag  
        
    # Set filter for 'DECAY_DATE'
    if DECAY_DATE is not None:
        DecayDate_flag = (data['DECAY_DATE'] > DECAY_DATE[0]) & (data['DECAY_DATE'] < DECAY_DATE[1])
    else:
        DecayDate_flag = full_of_true

    # Set filter for 'PERIOD'
    if PERIOD is not None:
        OrbitalPeriod_flag = (data['PERIOD'] > PERIOD[0]) & (data['PERIOD'] < PERIOD[1])
    else:
        OrbitalPeriod_flag = full_of_true   

    # Set filter for 'INCLINATION'
    if INCLINATION is not None:
        Inclination_flag = (data['INCLINATION'] > INCLINATION[0]) & (data['INCLINATION'] < INCLINATION[1])
    else:
        Inclination_flag = full_of_true
       
    # Set filter for 'APOGEE'
    if APOGEE is not None:
        ApoAlt_flag = (data['APOGEE'] > APOGEE[0]) & (data['APOGEE'] < APOGEE[1])
    else:
        ApoAlt_flag = full_of_true
        
    # Set filter for 'PERIGEE'
    if PERIGEE is not None:
        PerAlt_flag = (data['PERIGEE'] > PERIGEE[0]) & (data['PERIGEE'] < PERIGEE[1])
    else:
        PerAlt_flag = full_of_true
        
    # Set filter for 'MEAN_ALT'
    if MEAN_ALT is not None:
        MeanAlt_flag = (Mean_Alltitude > MEAN_ALT[0]) & (Mean_Alltitude < MEAN_ALT[1])
    else:
        MeanAlt_flag = full_of_true    

    # Set filter for 'ECC'
    if ECC is not None:
        Ecc_flag = (Eccentricity > ECC[0]) & (Eccentricity < ECC[1])
    else:
        Ecc_flag = full_of_true       

    # Set filter for 'Country'
    if OWNER is not None:
        if type(OWNER) in [str,list]:
            Owner_flag = np.in1d(data['OWNER'],OWNER)
        else:
            raise Exception('Type of OWNER should be in str or list of str.') 
    else:
        Owner_flag = full_of_true   

    # Set filter for TLE status
    OrbitalStatus_flag = data['DATA_STATUS_CODE'].isnull()

    if TLE_STATUS is None:
        OrbitalStatus_flag = full_of_true
    else:
        if not TLE_STATUS: OrbitalStatus_flag = ~OrbitalStatus_flag

    # Combine filters
    combined_flag = COSPARID_flag & NORADID_flag & Payload_flag & Decayed_flag & DecayDate_flag & OrbitalPeriod_flag & Inclination_flag & ApoAlt_flag & PerAlt_flag & MeanAlt_flag & Ecc_flag & Owner_flag & OrbitalStatus_flag
    df = data[combined_flag]

    # Eeadjust the order of the columns 
    column_reorder = ['OBJECT_NAME','COSPAR_ID', 'NORAD_ID','OBJECT_TYPE','OPS_STATUS_CODE','DECAY_DATE',\
                      'PERIOD', 'INCLINATION','APOGEE','PERIGEE','MEAN_ALT','ECC',\
                      'LAUNCH_DATE','LAUNCH_SITE','RCS','OWNER','DATA_STATUS_CODE','ORBIT_CENTER','ORBIT_TYPE']
    df = df.reindex(columns=column_reorder)
    if TLE_STATUS: df = df.drop(columns=['DATA_STATUS_CODE'])
      
    # Sort     
    if sort is None:    
        df = df.sort_values(by=['NORAD_ID'])
    else:
        if sort[0] == '-': 
            ascending_flag = False
        else:
            ascending_flag = True
    
        if sort.__contains__('COSPAR_ID'):
            df = df.sort_values(by=['COSPAR_ID'],ascending=ascending_flag)
        elif sort.__contains__('NORAD_ID'):
            df = df.sort_values(by=['NORAD_ID'],ascending=ascending_flag)   
        elif sort.__contains__('DECAY_DATE'):
            df = df.sort_values(by=['DECAY_DATE'],ascending=ascending_flag)   
        elif sort.__contains__('PERIOD'):
            df = df.sort_values(by=['PERIOD'],ascending=ascending_flag)    
        elif sort.__contains__('INCLINATION'):
            df = df.sort_values(by=['INCLINATION'],ascending=ascending_flag) 
        elif sort.__contains__('APOGEE'):
            df = df.sort_values(by=['APOGEE'],ascending=ascending_flag)   
        elif sort.__contains__('PERIGEE'):
            df = df.sort_values(by=['PERIGEE'],ascending=ascending_flag) 
        elif sort.__contains__('MEAN_ALT'):
            df = df.sort_values(by=['MEAN_ALT'],ascending=ascending_flag) 
        elif sort.__contains__('ECC'):
            df = df.sort_values(by=['ECC'],ascending=ascending_flag)     
        elif sort.__contains__('LAUNCH_DATE'):
            df = df.sort_values(by=['LAUNCH_DATE'],ascending=ascending_flag) 
        elif sort.__contains__('LAUNCH_SITE'):
            df = df.sort_values(by=['LAUNCH_SITE'],ascending=ascending_flag)     
        elif sort.__contains__('RCS'):
            df = df.sort_values(by=['RCS'],ascending=ascending_flag)    
        elif sort.__contains__('OWNER'):
            df = df.sort_values(by=['OWNER'],ascending=ascending_flag)
        else:
            raise Exception("Avaliable options include 'COSPAR_ID', NORAD_ID', 'DECAY_DATE', 'PERIOD', 'INCLINATION', 'APOGEE', 'PERIGEE', 'MEAN_ALT', 'ECC', 'LAUNCH_DATE', 'LAUNCH_SITE', 'RCS', and 'OWNER'. Also, a negative sign '-' can be added ahead to the option to sort in descending order.")
    df = df.reset_index(drop=True)
    mode = 'celestrak_catlog'

    return SatCatlog(df,mode)

def parseQSMagFile():
    '''
    Read and parse the qs.mag file for getting noradid and standard(intrinsic) magnitude for satellites.
    '''
    qsfile = data_prepare.qs_file

    qsmag = np.genfromtxt(qsfile,skip_header=1,skip_footer=1,delimiter=[5,28,5],dtype=(int,str,float)) 
    df_qsmag = pd.DataFrame(qsmag).drop(columns=['f1']).rename(columns={"f0": "NORAD_ID", "f2": "StdMag"})
    return df_qsmag         

def targets_query(COSPAR_ID=None,NORAD_ID=None,PAYLOAD=None,OBJECT_CLASS=None,DECAYED=None,DECAY_DATE=None,PERIOD=None,INCLINATION=None,APOGEE=None,PERIGEE=None,MEAN_ALT=None,ECC=None,TLE_STATUS=None,MASS=None,SHAPE=None,LENGTH=None,HEIGHT=None,DEPTH=None,RCSMin=None,RCSMax=None,RCSAvg=None,OWNER=None,sort=None):
    """
    Query space targets that meet the requirements by setting a series of specific parameters from the the [DISCOS](https://discosweb.esoc.esa.int)(Database and Information System Characterising Objects in Space) database and the [CELESTRAK](https://celestrak.com) database.

    Usage: 
    satcatlog = targets_query(PAYLOAD=False,DECAYED=False,MEAN_ALT=[400,900],RCSAvg=[5,15])

    Parameters:
    COSPAR_ID     -> [str or list of str, optional, default = None] Target IDs by the in Committee On SPAce Research; if None, this option is ignored.
    NORAD_ID      -> [int, str, list, or filename(such as noradids.txt), optional, default = None] Target IDs by the North American Aerospace Defense Command; if None, this option is ignored.
    PAYLOAD       -> [bool, optional, fafault = None] Identify whether a target belongs to payload or not. If True, then targets belong to payload; if False, then non-payload; if None, then this option is ignored.
    OBJECT_CLASS  -> [str or list of str, optional, default = None] Classification of targets; avaliable options include 'Payload', 'Payload Debris', 'Payload Fragmentation Debris', 
    'Payload Mission Related Object', 'Rocket Body', 'Rocket Debris', 'Rocket Fragmentation Debris', 'Rocket Mission Related Object', 'Other Mission Related Object','Other Debris', Unknown', or any combination of them, 
    for examle, ['Rocket Body', 'Rocket Debris', 'Rocket Fragmentation Debris']; If None, this option is ignored.
    
    DECAYED       -> [bool, optional, default = None] it also called reentry; If False, targets are still in orbit by now; if True, then reentry; if None, this option is ignored.
    DECAY_DATE    -> [list of str with 2 elemnts, optional, default = None] Date of reentry; it must be in form of ['date1','date2'], such as ['2019-01-05','2020-05-30']; if None, then this option is ignored.
    PERIOD        -> [list of float with 2 elemnts, optional, default = None] Orbit period[minutes] of targets; it must be in form of [period1,period2], such as [100.0,200.0]; if None, this option is ignored.  
    INCLINATION   -> [list of float with 2 elemnts, optional, default = None] Orbit inclination[degrees] of targets; must be in form of [inc1,inc2], such as [45.0,80.0]; if None, this option is ignored.  
    APOGEE        -> [list of float with 2 elemnts, optional, default = None] Apogee Altitude[km] of targets; it must be in form of [apoalt1,apoalt2], such as [800.0,1400.0]; if None, this option is ignored.  
    PERIGEE       -> [list of float with 2 elemnts, optional, default = None] Perigee Altitude[km] of targets; it must be in form of [peralt1,peralt2], such as [300.0,400.0]; if None, this option is ignored.  
    MEAN_ALT      -> [list of float with 2 elemnts, optional, default = None] Mean Altitude[km] of targets; it must be in form of [meanalt1,meanalt2], such as [300.0,800.0]; if None, then option is ignored. 
    ECC           -> [list of float with 2 elemnts, optional, default = None] Eccentricity of targets; it must be in form of [ecc1,ecc2], such as [0.01,0.2]; if None, then option is ignored.   
    TLE_STATUS    -> [bool, optional, default = None] Identify whether a TLE is valid. If True, TLE is valid; if False, No Current Elements, No Initial Elements, or No Elements Available; if None, this option is ignored.
    MASS          -> [list of float with 2 elemnts, optional, default = None] Mass[kg] of a target; it must be in form of [m1,m2], such as [5.0,10.0]; if None, this option is ignored.
    SHAPE -> [str or list of str, optional, default = None] Shape of targets; commonly used options include 'Cyl', 'Sphere', 'Cone', 'Dcone', Pan', 'Ell', 'Dish', 'Cable', 'Box', 'Rod', 'Poly', 'Sail', 'Ant', 
    'Frust', 'Truss', 'Nozzle', and 'lrr'. Any combinations of them are also supported, for examle, ['Cyl', 'Sphere', 'Pan'] means 'or', and ['Cyl', 'Sphere', 'Pan', '+'] means 'and'; If None, this option is ignored.  
    LENGTH        -> [list of float with 2 elemnts, optional, default = None] Length[m] of a target; it must be in form of [l1,l2], such as [5.0,10.0]; if None, this option is ignored.
    HEIGHT        -> [list of float with 2 elemnts, optional, default = None] Height[m] of a target; it must be in form of [h1,h2], such as [5.0,10.0]; if None, this option is ignored.
    DEPTH         -> [list of float with 2 elemnts, optional, default = None] Depth[m] of a target; it must be in form of [d1,d2], such as [5.0,10.0]; if None, this option is ignored.
    RCSMin        -> [list of float with 2 elemnts, optional, default = None] Minimum Radar Cross Section[m2] of a target; it must be in form of [RCS1,RCS2], such as [0.5,2.0]; if None, this option is ignored.
    RCSMax        -> [list of float with 2 elemnts, optional, default = None] Maximum Radar Cross Section[m2] of a target; it must be in form of [RCS1,RCS2], such as [10.0,100.0]; if None, this option is ignored.
    RCSAvg        -> [list of float with 2 elemnts, optional, default = None] Average Radar Cross Section[m2] of a target; it must be in form of [RCS1,RCS2], such as [5,20]; if None, this option is ignored.
    OWNER       -> [str or list of str, optional, default = None] Satellite Ownership; country codes/names can be found at http://www.fao.org/countryprofiles/iso3list/en/; if None, this option is ignored.
    sort          -> [str, optional, default = None] sort by features of targets in a specific order, such as by mass; avaliable options include 'COSPAR_ID', NORAD_ID', 'OBJECT_CLASS', 'MASS', 'DECAY_DATE', 'SHAPE', 
    'LENGTH', 'HEIGHT', 'DEPTH', 'RCSMin', 'RSCMax', 'RCSAvg', 'PERIOD', 'INCLINATION', 'APOGEE', 'PERIGEE', 'MEAN_ALT', 'ECC', and 'OWNER'.
    If there is a negative sign '-' ahead, such as "-RCSAvg", it will be sorted in descending order. If None, then sort by NORADID by default.
    
    Outputs:
    satcatlog -> instance of class SatCatlog
    """
    # Query space targets from the CELESTRAK database
    df_celestrak = celestrak_query(COSPAR_ID,NORAD_ID,PAYLOAD,DECAYED,DECAY_DATE,PERIOD,INCLINATION,APOGEE,PERIGEE,MEAN_ALT,ECC,OWNER,TLE_STATUS).df.drop('OBJECT_NAME',axis=1)
    # Query space targets from the DISCOS database
    noradids = list(df_celestrak['NORAD_ID'])
    if len(noradids) > 1000: noradids = NORAD_ID
    print('Go through the DISCOS database ... ')    
    df_discos = discos_query(COSPAR_ID,noradids,OBJECT_CLASS,PAYLOAD,DECAYED,DECAY_DATE,MASS,SHAPE,LENGTH,HEIGHT,DEPTH,RCSMin,RCSMax,RCSAvg).df.dropna(subset=['NORAD_ID'])

    # Merge the CELESTRAK database and the DISCOS database
    df = pd.merge(df_celestrak, df_discos, on=['COSPAR_ID','NORAD_ID'],validate="one_to_one")

    # Merge the QSMAG database
    df_qsmag = parseQSMagFile()
    df = pd.merge(df, df_qsmag, on=['NORAD_ID'],how='left',validate="one_to_one")

    # Remove unwanted columns and readjust the order of the columns 
    df = df.drop(['RCS'],axis=1)
    column_reorder = ['OBJECT_NAME','COSPAR_ID','NORAD_ID','OBJECT_CLASS','OPS_STATUS_CODE','DECAY_DATE',\
                      'PERIOD', 'INCLINATION','APOGEE', 'PERIGEE','MEAN_ALT','ECC','DATA_STATUS_CODE','ORBIT_CENTER','ORBIT_TYPE',\
                      'MASS','SHAPE','LENGTH', 'HEIGHT','DEPTH','RCSMin', 'RCSMax', 'RCSAvg','StdMag',\
                      'LAUNCH_DATE','LAUNCH_SITE','OWNER']                                 
    df = df.reindex(columns=column_reorder)  
    if TLE_STATUS: df = df.drop(columns=['DATA_STATUS_CODE'])
         
    # Sort
    if sort is None:    
        df = df.sort_values(by=['NORAD_ID'])
    else:
        if sort[0] == '-': 
            ascending_flag = False
        else:
            ascending_flag = True
        
        if sort.__contains__('COSPAR_ID'):
            df = df.sort_values(by=['COSPAR_ID'],ascending=ascending_flag)
        elif sort.__contains__('NORAD_ID'):
            df = df.sort_values(by=['NORAD_ID'],ascending=ascending_flag)  
        elif sort.__contains__('DECAY_DATE'):
            df = df.sort_values(by=['DECAY_DATE'],ascending=ascending_flag)  
        elif sort.__contains__('PERIOD'):
            df = df.sort_values(by=['PERIOD'],ascending=ascending_flag)    
        elif sort.__contains__('INCLINATION'):
            df = df.sort_values(by=['INCLINATION'],ascending=ascending_flag) 
        elif sort.__contains__('APOGEE'):
            df = df.sort_values(by=['APOGEE'],ascending=ascending_flag)   
        elif sort.__contains__('PERIGEE'):
            df = df.sort_values(by=['PERIGEE'],ascending=ascending_flag) 
        elif sort.__contains__('MEAN_ALT'):
            df = df.sort_values(by=['MEAN_ALT'],ascending=ascending_flag) 
        elif sort.__contains__('ECC'):
            df = df.sort_values(by=['ECC'],ascending=ascending_flag)              
        elif sort.__contains__('MASS'):
            df = df.sort_values(by=['MASS'],ascending=ascending_flag)    
        elif sort.__contains__('LENGTH'):
            df = df.sort_values(by=['LENGTH'],ascending=ascending_flag)
        elif sort.__contains__('HEIGHT'):
            df = df.sort_values(by=['HEIGHT'],ascending=ascending_flag)
        elif sort.__contains__('DEPTH'):
            df = df.sort_values(by=['DEPTH'],ascending=ascending_flag)   
        elif sort.__contains__('RCSMin'): 
            df =  df.sort_values(by=['RCSMin'],ascending=ascending_flag)  
        elif sort.__contains__('RCSMax'): 
            df =  df.sort_values(by=['RCSMax'],ascending=ascending_flag)    
        elif sort.__contains__('RCSAvg'): 
            df =  df.sort_values(by=['RCSAvg'],ascending=ascending_flag) 
        elif sort.__contains__('StdMag'):
            df = df.sort_values(by=['StdMag'],ascending=ascending_flag)          
        elif sort.__contains__('LAUNCH_DATE'):
            df = df.sort_values(by=['LAUNCH_DATE'],ascending=ascending_flag)   
        elif sort.__contains__('OWNER'):
            df = df.sort_values(by=['OWNER'],ascending=ascending_flag)
        else:
            raise Exception("Avaliable options include 'COSPAR_ID', NORAD_ID', 'DECAY_DATE', 'PERIOD', 'INCLINATION', \
                'APOGEE', 'PERIGEE', 'MEAN_ALT', 'ECC', 'MASS','LENGTH','DEPTH','HEIGHT', 'RCSMin','RCSMax', 'RCSAvg',\
                'StdMag','LAUNCH_DATE',and 'OWNER'. Also, a negative sign '-' can be added to the option to sort in descending order.")
    df = df.reset_index(drop=True)
    mode = 'targets_catalog'

    return SatCatlog(df,mode)               