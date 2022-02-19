# locations of the shower table files
import os


class config():
    pth,_ = os.path.split(__file__)
    jenniskens_shower_table_npy = os.path.join(pth, 'ShowerLookUpTable.npy')
    jenniskens_shower_table_file = os.path.join(pth, 'ShowerLookUpTable.txt')
    iau_shower_table_npy = os.path.join(pth, 'streamfulldata.npy')
    iau_shower_table_file = os.path.join(pth, 'streamfulldata.csv')
