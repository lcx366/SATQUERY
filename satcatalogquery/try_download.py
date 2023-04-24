import wget

def wget_download(url,dir_file,desc=None):
    """
    Download files by wget command

    Inputs:
        url -> [str]
        dir_file -> [str] Path to save the files downloaded
        desc -> [str,optional,default=None] Log description for file downloading 
    Outpits:
        wget_out -> [str] Path of the files downloaded

    """
    if desc: print(desc)
    wget_out = wget.download(url,dir_file)
    print()

    return wget_out     