import uproot
import pandas as pd
import matplotlib.pyplot as plt
import os
import datetime

# get time
def get_time():
    return datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

# CREATE A RES FOLDER AND SUBFOLDERS
if not os.path.exists('res_analysis'):
    os.makedirs('res_analysis')
path = 'res_analysis/' + get_time()
if not os.path.exists(path):
    os.makedirs(path)
    # print("creating")
    print(path + "\n")
    # png and svg paths
    os.makedirs(path + '/png')
    os.makedirs(path + '/svg')


def plot(filename):
    print("Plotting: " + filename + "\n")

    # Get the tree in the ROOT file
    tree = uproot.open("root_analysis/" + filename)["clusters_detector"]

    #time = tree.arrays('time')
    pos_x = tree.arrays('pos0')
    pos_y = tree.arrays('pos1')
    time0_algo = tree.arrays('time0_algo')

    # Create a pandas data frame, which is used to apply the cuts
    #time_list = time['time'].tolist()
    pos_x_list = pos_x['pos0'].tolist()
    pos_y_list = pos_y['pos1'].tolist()
    time0_algo_list = time0_algo['time0_algo'].tolist()


    # Create a pandas data frame, which is used to apply the cuts
    data = {'x': pos_x_list, 'y': pos_y_list, 'time0_algo': time0_algo_list}
    df = pd.DataFrame(data)

    # HEATMAP PLOT OF COUNTS IN THE X-Y PLANE FOR EVENTS THAT HAVE POS > 100 AND POS < 156
    # get events with x and y positions in the range of 100 to 156
    events = df.query('x > 0 and x < 255 and y > 0 and y < 255')
    x = events['x']
    y = events['y']
    # create hist 2d plot with max value of 120000 with automatic range due to masking of sensor during experiment
    plt.hist2d(x, y, bins=100, vmax=5000)
    plt.colorbar()
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('x-y plane' + '\n' + filename)
    plt.savefig(path + '/png/x_y_plane_' + filename + '.png', dpi=500)
    plt.savefig(path + '/svg/x_y_plane_' + filename + '.svg', dpi=500)
    plt.show()
    plt.close()


# plot("root_analysis/GdNat_n_tof_5200V_6mVfC_40mV_DDR_masked_00000_20241025121439_20241106114908_algo_7_tof.root")
# get files from root_analysis folder
for filename in os.listdir('root_analysis'):
    if filename.endswith(".root"):
        plot(filename)
