import numpy as np
from os import path,makedirs,remove
from pathlib import Path
from datetime import datetime,timedelta
from zipfile import ZipFile
from glob import glob
from spacetrack import SpaceTrackClient
from colorama import Fore
from time import sleep

from .try_download import wget_download

def download_satcat():
    """
    Download or update the satellites catalog file from www.celestrak.com

    Usage: 
    scfile = download_satcat()
    
    Outputs: 
    scfile -> [str] Local path of the satellites catalog file
    """
    home = str(Path.home())
    direc = home + '/src/satcat-data/'
    
    scfile = direc + 'satcat.csv'
    url = 'https://celestrak.com/pub/satcat.csv'

    if not path.exists(direc): makedirs(direc)
    if not path.exists(scfile):
        desc = 'Downloading the latest satellite catalog from CelesTrak'
        wget_out = wget_download(url,scfile,desc)
    else:
        modified_time = datetime.fromtimestamp(path.getmtime(scfile))
        if datetime.now() > modified_time + timedelta(days=7):
            remove(scfile)
            desc = 'Updating the satellite catalog from CELESTRAK'
            wget_out = wget_download(url,scfile,desc) 
        else:
            print('The satellite catalog in {:s} is already the latest.'.format(direc))    
    return scfile

def download_qsmag():
    """
    Download or update the file which records the standard(intrinsic) magnitude for satellites from https://www.prismnet.com/~mmccants/programs/qsmag.zip
    
    Usage: 
    qsfile = download_qsmag()
    
    Outputs: 
    qsfile -> [str] Local path of the qs.mag file
    """
    home = str(Path.home())
    direc = home + '/src/satcat-data/'
    
    qsfile_zip = direc + 'qsmag.zip'
    qsfile = direc + 'qs.mag'
    url = 'https://www.prismnet.com/~mmccants/programs/qsmag.zip'

    if not path.exists(direc): makedirs(direc)
    if not path.exists(qsfile):
        desc = 'Downloading the latest qs.mag data from the Mike McCants Satellite Tracking Web Pages'
        wget_out = wget_download(url,qsfile_zip,desc)
    else:
        modified_time = datetime.fromtimestamp(path.getmtime(qsfile))
        if datetime.now() > modified_time + timedelta(days=180):
            remove(qsfile)
            desc = 'Updating the qs.mag data from the Mike McCants Satellite Tracking Web Pages'
            wget_out = wget_download(url,qsfile_zip,desc) 
        else:
            print('The qs.mag data in {:s} is already the latest.'.format(direc))    

    if path.exists(qsfile_zip):
        # unzip qsmag file
        with ZipFile(qsfile_zip, 'r') as zip_ref:
            zip_ref.extractall(direc)
        remove(qsfile_zip)    

    return qsfile

def download_tle(noradids,mode='keep',dir_TLE='TLE/'):
    """
    Download the TLE/3LE data from [SPACETRACK](https://www.space-track.org) automatically

    Usage: 
    tlefile = tle_download(noradids)
    tlefile = tle_download(noradids,'clear')
    tlefile = tle_download('satno.txt')

    Inputs:
    noradids -> [str, int, list of str/int] NORADID of space targets. 
    It can be a single NORADID, list of NORADID, or a file containing a set of NORADID.
    The form and format of the file is as follows:
    #satno
    12345
    23469
    ...

    Parameters:
    mode -> [str,default='keep'] either keep the files stored in TLE directory or clear the TLE directory 

    Outputs: 
    tlefile  -> [str] Path of TLE/3LE file.
    """
    # Check whether a list is empty or not
    if not noradids: raise Exception('noradids is empty.')

    if type(noradids) is list:
        if type(noradids[0]) is int: noradids = [str(i) for i in noradids]    
    else:
        noradids = str(noradids)
        if '.' in noradids: # noradids as a file
            noradids = list(set(np.loadtxt(noradids,dtype=str)))
        else:
            noradids = [noradids]    
    
    # Set the maximum of requested URL's length with a single access 
    # The setup prevents exceeding the capacity limit of the server
    n = 500
    noradids_parts = [noradids[i:i + n] for i in range(0, len(noradids), n)]  
    part_num = len(noradids_parts)    
    
    # username and password for Space-Track
    home = str(Path.home())
    direc = home + '/src/spacetrack-data/'
    loginfile = direc + 'spacetrack-login'

    if not path.exists(direc): makedirs(direc)
    if not path.exists(loginfile):
        username = input('Please input the username for Space-Track(which can be created at https://www.space-track.org/auth/login): ')
        password = input('Please input the password for Space-Track: ')
        outfile = open(loginfile,'w')
        for element in [username,password]:
            outfile.write('{:s}\n'.format(element))
        outfile.close()
    else:
        infile = open(loginfile,'r')
        username = infile.readline().strip()
        password = infile.readline().strip()
        infile.close()
    
    # save TLE data to files  
    fileList_TLE = glob(dir_TLE+'*')
    if path.exists(dir_TLE):
        if mode == 'clear':
            for file in fileList_TLE:
                remove(file)
    else:
        makedirs(dir_TLE) 

    valid_ids,j = [],1
    date_str = datetime.utcnow().strftime("%Y%m%d")
    filename_tle = dir_TLE + 'tle_{:s}.txt'.format(date_str)
    file_tle = open(filename_tle,'w')  

    st = SpaceTrackClient(username, password)
    for part in noradids_parts:
        desc = 'Downloading TLE data: Part {:s}{:2d}{:s} of {:2d}'.format(Fore.BLUE,j,Fore.RESET,part_num)
        print(desc,end='\r')
        lines_tle = st.tle_latest(norad_cat_id=part,ordinal=1,iter_lines=True,format='tle')    
        for line in lines_tle:
            words = line.split()
            if words[0] == '2': valid_ids.append(words[1].lstrip('0'))
            file_tle.write(line+'\n')
        sleep(j+5) 
        j += 1   
    file_tle.close()

    missed_ids = list(set(noradids)-set(valid_ids))
    if missed_ids: 
        missed_ids_filename = dir_TLE + 'missed_ids_{:s}.txt'.format(date_str)
        desc = '{:s}Note: space targets with unavailable TLE are stored in {:s}.{:s} '.format(Fore.RED,missed_ids_filename,Fore.RESET)
        print(desc) 
        np.savetxt(missed_ids_filename,missed_ids,fmt='%s')

    return filename_tle     