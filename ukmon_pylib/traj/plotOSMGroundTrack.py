import argparse
from importlib.resources import path
import numpy as np
import os
#import cartopy.crs as ccrs
#import cartopy.io.img_tiles as cimgt

import matplotlib.pyplot as plt
from wmpl.Utils.Math import meanAngle
from wmpl.Utils.PlotMap_OSM import OSMMap
from wmpl.Utils.Plotting import savePlot
from wmpl.Utils.Pickling import loadPickle

# Text size of image legends
LEGEND_TEXT_SIZE = 6


def plotOSMGroundMap(traj, file_name, output_dir, show_plot=False, save_results=True):
    # marker type, size multiplier
    markers = [
        ['x', 2 ],
        ['+', 8 ],
        ['o', 1 ],
        ['s', 1 ],
        ['d', 1 ],
        ['v', 1 ],
        ['*', 1.5 ],
        ]

    ######################################################################################################

    ### Plot lat/lon of the meteor using OSM ###
    ######################################################################################################

    # initialise obs so that the next statement works
    obs = traj.observations[0]
    # Calculate mean latitude and longitude of all meteor points
    met_lon_mean = meanAngle([x for x in obs.meas_lon for obs in traj.observations])
    met_lat_mean = meanAngle([x for x in obs.meas_lat for obs in traj.observations])


    # Put coordinates of all sites and the meteor in the one list
    lat_list = [obs.lat for obs in traj.observations]
    lat_list.append(met_lat_mean)
    lon_list = [obs.lon for obs in traj.observations]
    lon_list.append(met_lon_mean)

    # Put edge points of the meteor in the list
    lat_list.append(traj.rbeg_lat)
    lon_list.append(traj.rbeg_lon)
    lat_list.append(traj.rend_lat)
    lon_list.append(traj.rend_lon)
    lat_list.append(traj.orbit.lat_ref)
    lon_list.append(traj.orbit.lon_ref)

    # Init the map
    m = OSMMap(lat_list, lon_list, border_size=50, color_scheme='light')


    # Plot locations of all stations and measured positions of the meteor
    for i, obs in enumerate(sorted(traj.observations, key=lambda x:x.rbeg_ele, reverse=True)):

        # Extract marker type and size multiplier
        marker, sm = markers[i%len(markers)]

        # Plot stations
        m.scatter(obs.lat, obs.lon, s=sm*10, label=str(obs.station_id), marker=marker)

        # Plot measured points
        m.plot(obs.meas_lat[obs.ignore_list == 0], obs.meas_lon[obs.ignore_list == 0], c='r')

        # Plot ignored points
        if np.any(obs.ignore_list != 0):
            m.scatter(obs.meas_lat[obs.ignore_list != 0], obs.meas_lon[obs.ignore_list != 0], c='k', \
                marker='x', s=5, alpha=0.5)



    # Plot a point marking the final point of the meteor
    m.scatter(traj.rend_lat, traj.rend_lon, c='k', marker='+', s=50, alpha=0.75, label='Lowest height')


    # If there are more than 10 observations, make the legend font smaller
    legend_font_size = LEGEND_TEXT_SIZE
    if len(traj.observations) >= 10:
        legend_font_size = 5

    plt.legend(loc='upper left', prop={'size': legend_font_size})

    if save_results:
        savePlot(plt, file_name + '_OSM_ground_track.' + traj.plot_file_type, output_dir)

    if show_plot:
        plt.show()

    else:
        plt.clf()
        plt.close()  


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description="""Plot the OSM ground track map.""",
        formatter_class=argparse.RawTextHelpFormatter)

    arg_parser.add_argument('traj_path', type=str, help="Path to a trajectory pickle file.")

    arg_parser.add_argument('-s', '--show_plot', action='store_true', help='Show the graph onscreen.')
    arg_parser.add_argument('-r', '--save_results', action='store_true', help='save the graph.')


    # Parse the command line arguments
    cml_args = arg_parser.parse_args()

    traj = loadPickle(*os.path.split(cml_args.traj_path))

    save_results=cml_args.save_results
    show_plot=cml_args.show_plot

    output_dir, file_name = os.path.split(cml_args.traj_path)
    file_name, _ = os.path.splitext(file_name)
    file_name = file_name[:file_name.find('traj')]
    
    plotOSMGroundMap(traj, file_name, output_dir, show_plot=show_plot, save_results=save_results)
