#
# analyse a UFO dataset using RMS
#
import sys, os, argparse
sys.path.append('c:/users/mark/documents/projects/meteorhunting/RMS/')
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
    ### COMMAND LINE ARGUMENTS
    # Init the command line arguments parser
    arg_parser = argparse.ArgumentParser(description="Analyses a UFO avi with RMS.")

    arg_parser.add_argument('ff_path', nargs='+', metavar='FILE_PATH', type=str, \
        help='Full path and name of the file to analyse')

    arg_parser.add_argument('-c', '--config', nargs=1, metavar='CONFIG_PATH', type=str, \
        help="Path to a config file which will be used instead of the default one.")
    
    # Parse the command line arguments
    cml_args = arg_parser.parse_args()

    #########################

    ff_directory, ff_name = os.path.split(cml_args.ff_path[0])

    print(ff_directory, ff_name)
    config = cr.loadConfigFromDirectory(cml_args.config[0], ff_directory)
    print("loaded config \n\n\n")
    
    AnalyseUFOwithRMS(config, ff_directory, ff_name)