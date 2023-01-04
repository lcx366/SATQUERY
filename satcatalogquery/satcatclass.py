from os import makedirs,path
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib import colors
import matplotlib.dates as mdates
import pandas as pd

from .data_download import download_tle

class SatCatlog(object):

    def __init__(self,df,mode):
        self.df = df
        self._mode = mode

    def __repr__(self):
    
        return 'instance of class SatCatlog'    

    def save(self,dir_catalog=None):
        df = self.df
        mode = self._mode

        if dir_catalog is None: dir_catalog = 'satcatalogs/' 
        if not path.exists(dir_catalog): makedirs(dir_catalog)   

        date_str = datetime.utcnow().strftime("%Y%m%d")
        file_catalog = dir_catalog + '{:s}_{:s}.csv'.format(mode,date_str)
        df.to_csv(file_catalog,index = False) # Save the pandas dataframe to a csv-formatted file

        return file_catalog   

    def from_csv(csv_file,mode='external'):
        df = pd.read_csv(csv_file) 
        return SatCatlog(df,mode)      

    def statistics2d(self,x,y,num_bins=50,dir_fig=None):
        """
        x -> columns name in self.df
        y -> columns name in self.df

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
        plt.savefig(file_fig)

        return file_fig  

    def statistics1d(self,xs,num_bins = 50,dir_fig=None):
        """
        xs -> list of columns name in self.df, such as ['StdMag','LAUNCH_DATE']
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
                    ax[i].tick_params(axis='x', rotation=30)
                    ax[i].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
                n, bins, patches = ax[i].hist(df_x, num_bins) # ,density=True,histtype='step',cumulative=True
                ax[i].set_xlabel('{:s}'.format(xs[i]))
            file_fig = dir_fig+'{:s}.png'.format('_'.join(xs))   
        else:
                
            fig, ax = plt.subplots(1, 1,dpi=300)
            fig.tight_layout(pad=2)

            if type(xs) is list: xs = xs[0]

            df_x = df[xs]

            if xs in ['LAUNCH_DATE','DECAY_DATE']: 
                df_x = df_x.astype("datetime64")
                ax.tick_params(axis='x', rotation=30)
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            n, bins, patches = ax.hist(df_x, num_bins) # ,density=True,histtype='step',cumulative=True
            ax.set_xlabel('{:s}'.format(xs))
            file_fig = dir_fig+'{:s}.png'.format(xs)  
                
        plt.savefig(file_fig)

        return file_fig

    def get_tle(self,mode='keep',dir_TLE='TLE/'):
        noradids = list(self.df['NORAD_ID'])
        file_tle = download_tle(noradids,mode=mode,dir_TLE=dir_TLE)
        return file_tle
            