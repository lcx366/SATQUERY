from os import makedirs,path
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib import colors
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import random
from collections import Counter

from .query import _discos_query,_celestrak_query,_objects_query
from .data_download import download_tle

class SatCatalog(object):
    """
    class of SatCatalog

    Methods: 
        discos_query -> Given the geometric constraints of a spatial object, query the qualified spatial objects from the [DISCOS](https://discosweb.esoc.esa.int)(Database and Information System Characterising Objects in Space) database.
        celestrak_query -> Given the orbital constraints of a space object, query the qualified space objects from the [CELESTRAK](https://celestrak.com) database.
        objects_query -> Given the geometric and orbital constraints of a space object, query the qualified space objects from the [DISCOS](https://discosweb.esoc.esa.int)(Database and Information System Characterising Objects in Space) database and the [CELESTRAK](https://celestrak.com) database.
        to_csv -> Save the query results to a csv file.
        from_csv -> Load the csv file that records query results.
        hist2d -> Draw a 2D histogram. 
        hist1d -> Draw a histogram. 
        pie -> Draw a pie chart.
        get_tle -> Get the TLE data from [SPACETRACK](https://www.space-track.org) automatically.
    """

    def __init__(self,df,mode=None):
        self.df = df
        if mode is not None: self._mode = mode

    def __repr__(self):
    
        return 'instance of class SatCatalog'    

    def discos_query(COSPAR_ID=None,NORAD_ID=None,OBJECT_CLASS=None,PAYLOAD=None,DECAYED=None,DECAY_DATE=None,MASS=None,SHAPE=None,LENGTH=None,HEIGHT=None,DEPTH=None,RCSMin=None,RCSMax=None,RCSAvg=None,sort=None):
        """
        Given the geometric constraints of a spatial object, query the qualified spatial objects from the [DISCOS](https://discosweb.esoc.esa.int)(Database and Information System Characterising Objects in Space) database.

        Usage: 
            satcatalog = SatCatalog.discos_query(DECAYED=False,RCSAvg=[5,15])

        Inputs:
            COSPAR_ID -> [str or list of str, optional, default = None] object IDs defined by the Committee On SPAce Research; if None, this option is ignored. 
            NORAD_ID -> [int, str, list, or filename(such as 'noradids.txt'), optional, default = None] object IDs defined by the North American Aerospace Defense Command; if None, this option is ignored.
            OBJECT_CLASS -> [str, list of str, optional, default = None] Classification of objects; available options are 'Payload', 'Payload Debris', 'Payload Fragmentation Debris', 
            'Payload Mission Related Object', 'Rocket Body', 'Rocket Debris', 'Rocket Fragmentation Debris', 'Rocket Mission Related Object', 'Other Mission Related Object','Other Debris', Unknown', or any combination of them, 
            for example, ['Rocket Body', 'Rocket Debris', 'Rocket Fragmentation Debris']; If None, this option is ignored.  
            PAYLOAD -> [bool, optional, default = None] Whether an object is payload or not. If True, the object is a payload; if False, not a payload; if None, this option is ignored.
            DECAYED -> [bool, optional, default = None] Whether an object is  decayed(re-entry) or not; If False, the object is still in orbit by now; if True, then decayed; if None, this option is ignored.
            DECAY_DATE -> [list of str, optional, default = None] Date range of decay; it must be in form of ['date1','date2'], such as ['2019-01-05','2020-05-30']; if None, then this option is ignored.
            MASS -> [list of float, optional, default = None] Mass[kg] range of an object; it must be in form of [m1,m2], such as [5.0,10.0]; if None, this option is ignored.
            SHAPE -> [str or list of str, optional, default = None] Shape of an object; the usual choices include 'Cyl', 'Sphere', 'Cone', 'Dcone', Pan', 'Ell', 'Dish', 'Cable', 'Box', 'Rod', 'Poly', 'Sail', 'Ant', 
            'Frust', 'Truss', 'Nozzle', and 'lrr'. Any combination of them is also supported, for examle, ['Cyl', 'Sphere', 'Pan'] means 'or', and ['Cyl', 'Sphere', 'Pan', '+'] means 'and'; If None, this option is ignored.  
            LENGTH -> [list of float, optional, default = None] Length[m] range of an object; it must be in form of [l1,l2], such as [5.0,10.0]; if None, this option is ignored.
            HEIFHT -> [list of float, optional, default = None] Height[m] range of an object; it must be in form of [h1,h2], such as [5.0,10.0]; if None, this option is ignored.
            DEPTH -> [list of float, optional, default = None] Depth[m] range of an object; it must be in form of [d1,d2], such as [5.0,10.0]; if None, this option is ignored.
            RCSMin -> [list of float, optional, default = None] Minimum Radar Cross Section(RCS)[m2] of an object; if None, this option is ignored.
            RCSMax -> [list of float, optional, default = None] Maximum Radar Cross Section(RCS)[m2] of an object; if None, this option is ignored.
            RCSAvg -> [list of float, optional, default = None] Average Radar Cross Section(RCS)[m2] of an object; if None, this option is ignored.
            sort -> [str, optional, default = None] Sort according to attributes of spatial objects, such as mass; available options include 'COSPARID', NORADID', 'ObjectClass', 'DecayDate', 'Mass', 'Shape', 'Length', 'Height', 'Depth', 'RCSMin', 'RSCMax', and 'RCSAvg'.
            If the attribute is prefixed with a '-', such as '-Mass', it will be sorted in descending order. If None, the spatial objects are sorted by NORADID by default.
    
        Outputs:
            satcatalog -> instance of class SatCatalog containing the selected spatial objects
        """
        df = _discos_query(COSPAR_ID,NORAD_ID,OBJECT_CLASS,PAYLOAD,DECAYED,DECAY_DATE,MASS,SHAPE,LENGTH,HEIGHT,DEPTH,RCSMin,RCSMax,RCSAvg,sort)
        mode = 'discos_catalog'
        return SatCatalog(df,mode)  

    def celestrak_query(COSPAR_ID=None,NORAD_ID=None,PAYLOAD=None,DECAYED=None,DECAY_DATE=None,PERIOD=None,INCLINATION=None,APOGEE=None,PERIGEE=None,MEAN_ALT=None,ECC=None,OWNER=None,TLE_STATUS=None,sort=None):
        """
        Given the orbital constraints of a space object, query the qualified space objects from the [CELESTRAK](https://celestrak.com) database.

        Usage:
            satcatalog = SatCatalog.celestrak_query(DECAYED=False,MEAN_ALT=[400,900])

        Inputs:
            COSPAR_ID -> [str or list of str, optional, default = None] object IDs defined by the Committee On SPAce Research; if None, this option is ignored. 
            NORAD_ID -> [int, str, list, or filename(such as 'noradids.txt'), optional, default = None] object IDs defined by the North American Aerospace Defense Command; if None, this option is ignored.
            PAYLOAD -> [bool, optional, default = None] Whether an object is payload or not. If True, the object is a payload; if False, not a payload; if None, this option is ignored.
            DECAYED -> [bool, optional, default = None] Whether an object is  decayed(re-entry) or not; If False, the object is still in orbit by now; if True, then decayed; if None, this option is ignored.
            DECAY_DATE -> [list of str, optional, default = None] Date range of decay; it must be in form of ['date1','date2'], such as ['2019-01-05','2020-05-30']; if None, then this option is ignored.
            PERIOD -> [list of float, optional, default = None] Orbital period[minutes] range of a space object; it must be in form of [period1,period2], such as [100.0,200.0]; if None, this option is ignored.  
            INCLINATION -> [list of float, optional, default = None] Range of inclination[degrees] of a space object; it must be in form of [inc1,inc2], such as [45.0,80.0]; if None, this option is ignored.  
            APOGEE -> [list of float, optional, default = None] Range of Apogee Altitude[km]; it must be in form of [apoalt1,apoalt2], such as [800.0,1400.0]; if None, this option is ignored.  
            PERIGEE -> [list of float, optional, default = None] Range of Perigee Altitude[km]; it must be in form of [peralt1,peralt2], such as [300.0,400.0]; if None, this option is ignored.  
            MEAN_ALT -> [list of float, optional, default = None] Mean Altitude[km] of objects; it must be in form of [meanalt1,meanalt2], such as [300.0,800.0]; if None, then option is ignored. 
            ECC -> [list of float, optional, default = None] Range of Eccentricity; it must be in form of [ecc1,ecc2], such as [0.01,0.2]; if None, then option is ignored.   
            OWNER -> [str or list of str, optional, default = None] Ownership of a space object; and country codes/names can be found at http://www.fao.org/countryprofiles/iso3list/en/; if None, this option is ignored.
            TLE_STATUS -> [bool, optional, default = None] Whether a TLE is valid. If False, it means No Current Elements, No Initial Elements, or No Elements Available; if None, this option is ignored.
            sort -> [str, optional, default = None] Sort according to attributes of a spatial object, such as MEAN_ALT; available options include 'COSPAR_ID', NORAD_ID', 'DECAY_DATE', 'PERIOD', 'INCLINATION', 'APOGEE', 'PERIGEE', 'MEAN_ALT', 'ECC',and 'OWNER'.
            If the attribute is prefixed with a '-', such as '-DecayDate', it will be sorted in descending order. If None, the spatial objects are sorted by NORADID by default.
    
        Outputs:
            satcatalog -> instance of class SatCatalog containing the selected spatial objects
        """    
        df = _celestrak_query(COSPAR_ID,NORAD_ID,PAYLOAD,DECAYED,DECAY_DATE,PERIOD,INCLINATION,APOGEE,PERIGEE,MEAN_ALT,ECC,OWNER,TLE_STATUS,sort)
        mode = 'celestrak_catalog'
        return SatCatalog(df,mode)

    def objects_query(COSPAR_ID=None,NORAD_ID=None,PAYLOAD=None,OBJECT_CLASS=None,DECAYED=None,DECAY_DATE=None,PERIOD=None,INCLINATION=None,APOGEE=None,PERIGEE=None,MEAN_ALT=None,ECC=None,TLE_STATUS=None,MASS=None,SHAPE=None,LENGTH=None,HEIGHT=None,DEPTH=None,RCSMin=None,RCSMax=None,RCSAvg=None,OWNER=None,sort=None):
        """
        Given the geometric and orbital constraints of a space object, query the qualified space objects from the [DISCOS](https://discosweb.esoc.esa.int)(Database and Information System Characterising Objects in Space) database and the [CELESTRAK](https://celestrak.com) database.

        Usage: 
            satcatalog = SatCatalog.objects_query(PAYLOAD=False,DECAYED=False,MEAN_ALT=[400,900],RCSAvg=[5,15])

        Inputs:
            COSPAR_ID -> [str or list of str, optional, default = None] object IDs defined by the Committee On SPAce Research; if None, this option is ignored. 
            NORAD_ID -> [int, str, list, or filename(such as 'noradids.txt'), optional, default = None] object IDs defined by the North American Aerospace Defense Command; if None, this option is ignored.
            OBJECT_CLASS -> [str, list of str, optional, default = None] Classification of objects; available options are 'Payload', 'Payload Debris', 'Payload Fragmentation Debris', 
            'Payload Mission Related Object', 'Rocket Body', 'Rocket Debris', 'Rocket Fragmentation Debris', 'Rocket Mission Related Object', 'Other Mission Related Object','Other Debris', Unknown', or any combination of them, 
            for example, ['Rocket Body', 'Rocket Debris', 'Rocket Fragmentation Debris']; If None, this option is ignored.  
            DECAYED -> [bool, optional, default = None] Whether an object is  decayed(re-entry) or not; If False, the object is still in orbit by now; if True, then decayed; if None, this option is ignored.
            DECAY_DATE -> [list of str, optional, default = None] Date range of decay; it must be in form of ['date1','date2'], such as ['2019-01-05','2020-05-30']; if None, then this option is ignored.
            PERIOD -> [list of float, optional, default = None] Orbital period[minutes] range of a space object; it must be in form of [period1,period2], such as [100.0,200.0]; if None, this option is ignored.  
            INCLINATION -> [list of float, optional, default = None] Range of inclination[degrees] of a space object; it must be in form of [inc1,inc2], such as [45.0,80.0]; if None, this option is ignored.  
            APOGEE -> [list of float, optional, default = None] Range of Apogee Altitude[km]; it must be in form of [apoalt1,apoalt2], such as [800.0,1400.0]; if None, this option is ignored.  
            PERIGEE -> [list of float, optional, default = None] Range of Perigee Altitude[km]; it must be in form of [peralt1,peralt2], such as [300.0,400.0]; if None, this option is ignored.  
            MEAN_ALT -> [list of float, optional, default = None] Mean Altitude[km] of objects; it must be in form of [meanalt1,meanalt2], such as [300.0,800.0]; if None, then option is ignored. 
            ECC -> [list of float, optional, default = None] Range of Eccentricity; it must be in form of [ecc1,ecc2], such as [0.01,0.2]; if None, then option is ignored.   
            TLE_STATUS -> [bool, optional, default = None] Whether a TLE is valid. If False, it means No Current Elements, No Initial Elements, or No Elements Available; if None, this option is ignored.
            MASS -> [list of float, optional, default = None] Mass[kg] range of an object; it must be in form of [m1,m2], such as [5.0,10.0]; if None, this option is ignored.
            SHAPE -> [str or list of str, optional, default = None] Shape of an object; the usual choices include 'Cyl', 'Sphere', 'Cone', 'Dcone', Pan', 'Ell', 'Dish', 'Cable', 'Box', 'Rod', 'Poly', 'Sail', 'Ant', 
            'Frust', 'Truss', 'Nozzle', and 'lrr'. Any combination of them is also supported, for examle, ['Cyl', 'Sphere', 'Pan'] means 'or', and ['Cyl', 'Sphere', 'Pan', '+'] means 'and'; If None, this option is ignored.  
            LENGTH -> [list of float, optional, default = None] Length[m] range of an object; it must be in form of [l1,l2], such as [5.0,10.0]; if None, this option is ignored.
            HEIFHT -> [list of float, optional, default = None] Height[m] range of an object; it must be in form of [h1,h2], such as [5.0,10.0]; if None, this option is ignored.
            DEPTH -> [list of float, optional, default = None] Depth[m] range of an object; it must be in form of [d1,d2], such as [5.0,10.0]; if None, this option is ignored.
            RCSMin -> [list of float, optional, default = None] Minimum Radar Cross Section(RCS)[m2] of an object; if None, this option is ignored.
            RCSMax -> [list of float, optional, default = None] Maximum Radar Cross Section(RCS)[m2] of an object; if None, this option is ignored.
            RCSAvg -> [list of float, optional, default = None] Average Radar Cross Section(RCS)[m2] of an object; if None, this option is ignored.
            OWNER -> [str or list of str, optional, default = None] Ownership of a space object; and country codes/names can be found at http://www.fao.org/countryprofiles/iso3list/en/; if None, this option is ignored.
            sort -> [str, optional, default = None] Sort according to attributes of a spatial object, such as by mass; available options include 'COSPAR_ID', NORAD_ID', 'OBJECT_CLASS', 'MASS', 'DECAY_DATE', 'SHAPE', 
            'LENGTH', 'HEIGHT', 'DEPTH', 'RCSMin', 'RSCMax', 'RCSAvg', 'PERIOD', 'INCLINATION', 'APOGEE', 'PERIGEE', 'MEAN_ALT', 'ECC', and 'OWNER'.
            If the attribute is prefixed with a '-', such as "-RCSAvg", it will be sorted in descending order. If None, the spatial objects are sorted by NORADID by default.
    
        Outputs:
            satcatalog -> instance of class SatCatalog containing the selected spatial objects
        """    

        df = _objects_query(COSPAR_ID,NORAD_ID,PAYLOAD,OBJECT_CLASS,DECAYED,DECAY_DATE,PERIOD,INCLINATION,APOGEE,PERIGEE,MEAN_ALT,ECC,TLE_STATUS,MASS,SHAPE,LENGTH,HEIGHT,DEPTH,RCSMin,RCSMax,RCSAvg,OWNER,sort)
        mode = 'objects_catalog'
        return SatCatalog(df,mode) 

    def to_csv(self,dir_catalog=None):
        """
        Save the query results to a csv file.

        Usage:
            file_catalog = satcatalog.to_csv()

        Inputs:
            dir_catalog -> [str,optional,default=None] Path to save the csv file

        Outputs:
            file_catalog -> [str] Path of the csv file
        """
        df = self.df
        mode = self._mode

        if dir_catalog is None: dir_catalog = 'satcatalogs/' 
        if not path.exists(dir_catalog): makedirs(dir_catalog)   

        date_str = datetime.utcnow().strftime("%Y%m%d")
        file_catalog = dir_catalog + '{:s}_{:s}.csv'.format(mode,date_str)
        df.to_csv(file_catalog,index = False) # Save the pandas dataframe to a csv-formatted file

        return file_catalog   

    def from_csv(csv_file):
        """
        Load the csv file that records query results.

        Usage:
            satcatalog = SatCatalog.from_csv('satcatalog.csv')

        Inputs:
            csv_filr -> [str] Path of the csv file

        Outputs:
            satcatalog -> [str] instance of class SatCatalog
        """
        df = pd.read_csv(csv_file) 
        return SatCatalog(df)      

    def hist2d(self,x,y,num_bins=50,dir_fig=None):
        """
        Draw a 2D histogram. 

        Usage:
            file_fig = satcatalog.hist2d(x,y)

        Inputs:
            x -> column names for the x-axis
            y -> column names for the y-axis
            num_bins -> [int,optional,default=50] the number of bins for the two dimensions
            dir_fig -> [str,optional,default=None] Path to save the histogram

        Outputs:
        file_fig -> [str] Path of the histogram
        """
        df = self.df

        if  dir_fig is None: dir_fig = 'satcatalogs/' 
        if not path.exists(dir_fig): makedirs(dir_fig)  

        fig, ax = plt.subplots(tight_layout=True,dpi=300)

        # the histogram of the data
        df_x,df_y = df[x],df[y]

        hist = ax.hist2d(df_x, df_y,bins=num_bins,density=True,norm=colors.LogNorm(),cmap='Oranges')
        ax.set_xlabel('{:s}'.format(x))
        ax.set_ylabel('{:s}'.format(y))
        file_fig = dir_fig + '{:s}-{:s}.png'.format(x,y)
        plt.savefig(file_fig,bbox_inches = 'tight')

        return file_fig  

    def hist1d(self,xs,num_bins = 50,dir_fig=None):
        """
        Draw a histogram. 

        Usage:
            file_fig = satcatalog.hist1d(xs)

        Inputs:
            xs -> list of column names, such as ['StdMag','LAUNCH_DATE']
            num_bins -> [int,optional,default=50] the number of bins
            dir_fig -> [str,optional,default=None] Path to save the histogram

        Outputs:
            file_fig -> [str] Path of the histogram
        """

        df = self.df

        if dir_fig is None: dir_fig = 'satcatalogs/' 
        if not path.exists(dir_fig): makedirs(dir_fig)  

        if type(xs) is list and len(xs) > 1:
            n_xs = len(xs)

            fig, ax = plt.subplots(1, n_xs,dpi=300)
            fig.tight_layout(pad=2)

            for i in range(n_xs):
                df_x = df[xs[i]]
                if xs[i] in ['LAUNCH_DATE','DECAY_DATE']: 
                    df_x = df_x.astype("datetime64")
                    ax[i].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m')) 
                    ax[i].tick_params(axis='x', rotation=30)
                n, bins, patches = ax[i].hist(df_x, num_bins)
                ax[i].set_xlabel('{:s}'.format(xs[i]))
            file_fig = dir_fig+'{:s}.png'.format('_'.join(xs))   
        else:
                
            fig, ax = plt.subplots(1, 1,dpi=300)
            fig.tight_layout(pad=2)

            if type(xs) is list: xs = xs[0]

            df_x = df[xs]

            if xs in ['LAUNCH_DATE','DECAY_DATE']: 
                df_x = df_x.astype("datetime64")   
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
                ax.tick_params(axis='x', rotation=30)

            n, bins, patches = ax.hist(df_x, num_bins)
            ax.set_xlabel('{:s}'.format(xs))
            file_fig = dir_fig+'{:s}.png'.format(xs)  
                
        plt.savefig(file_fig,bbox_inches = 'tight')

        return file_fig

    def pie(self,x,prominent=None,cutoff=50,dir_fig=None):
        """
        Draw a pie chart.

        Usage:
            file_fig = satcatalog.pie(x)

        Inputs:
            x -> list of column names, such as ['StdMag','LAUNCH_DATE']
            prominent -> [str,optional,default=None] Highlights of pie charts. If none, the highlights is random.
            cutoff -> [int,default=50] Below this value it is classified as 'other'
            dir_fig -> [str,optional,default=None] Path to save the pie chart
        Outputs:
            file_fig -> [str] path of histogram
        """

        if dir_fig is None: dir_fig = 'satcatalogs/' 
        if not path.exists(dir_fig): makedirs(dir_fig) 

        if x not in ['OWNER','LAUNCH_SITE','OBJECT_CLASS','SHAPE']: 
            raise Exception("Statistical variables should in ['OWNER','LAUNCH_SITE','OBJECT_CLASS','SHAPE'] for pie chart.")

        df_x = self.df[x]
                
        x_fre = pd.DataFrame(Counter(df_x).items(),columns=[x,'fre'])
        condition = x_fre['fre'] > cutoff
        most_fre = x_fre[condition]

        other_sum = sum(x_fre[~condition]['fre'])
        new_row = {x:['Other'], 'fre':[other_sum]}
        other_fre = pd.DataFrame(new_row)
        x_fre = pd.concat([most_fre,other_fre],ignore_index=True)

        labels,counts = x_fre[x],x_fre['fre']
        explode = np.zeros_like(labels)

        if prominent is None: prominent = random.choice(labels)
        prominent_index = labels.index[labels == prominent].tolist()[0]
        explode[prominent_index] = 0.15

        fig, ax = plt.subplots(dpi=300)
        fig.tight_layout(pad=2)

        ax.pie(counts, labels=labels, explode=explode,autopct='%.1f%%',startangle=26)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        file_fig = dir_fig+'{:s}.png'.format(x)  
        plt.savefig(file_fig,bbox_inches = 'tight')
        return file_fig

    def get_tle(self,mode='keep',dir_TLE='TLE/'):
        """
        Get the TLE data from [SPACETRACK](https://www.space-track.org) automatically.

        Usage: 
            tle_file = satcatalog.get_tle()

        Inputs:
            mode -> [str,optional,default='keep'] Either 'keep' the files stored in the TLE directory or 'clear' the TLE directory 
            dir_TLE -> [str,optional,default='TLE/'] Path to save TLE

        Outputs: 
            tle——file  -> [str] Path of the TLE file
        """
        noradids = list(self.df['NORAD_ID'])
        file_tle = download_tle(noradids,mode=mode,dir_TLE=dir_TLE)
        return file_tle
            