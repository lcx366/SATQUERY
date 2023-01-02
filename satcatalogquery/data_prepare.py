from .data_download import download_satcat, download_qsmag

def satcat_load():
    """
    load the sats catalog file from CelesTrak
    """
    global sc_file

    sc_file = download_satcat()

def qsmag_load():
    """
    load the standard(intrinsic) magnitude for satellites
    """
    global qs_file

    qs_file = download_qsmag()


