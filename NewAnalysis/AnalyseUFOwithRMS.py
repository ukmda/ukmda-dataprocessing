#
# analyse a JPG using RMS
#
import sys, os
sys.path.append('c:/users/mark/documents/projects/meteorhunting/RMS')
import RMS.ConfigReader as cr
from RMS.DetectStarsAndMeteors import detectStarsAndMeteors

def AnalyseUFOwithRMS(config, ff_directory, ff_name):
    """
    """
    flat_struct=None
    dark=None
    mask=None
    _, star_list, meteor_list = detectStarsAndMeteors(ff_directory, ff_name, config, flat_struct, dark, mask)

    print(star_list)
    print(meteor_list)
    
if __name__ == '__main__':

    ff_directory='c:/users/mark/documents/projects/meteorhunting/ukmon-shared/newanalysis/test_data'
    ff_name='M20200514_232502_TACKLEY_NE.avi'
    config = '.config'

    config = cr.loadConfigFromDirectory(config, ff_directory)

    AnalyseUFOwithRMS(config, ff_directory, ff_name)