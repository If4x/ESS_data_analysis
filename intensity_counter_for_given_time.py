import uproot
import pandas as pd
import matplotlib.pyplot as plt
import os
import datetime
from scipy.integrate import trapezoid as trapz


# get time
def get_time():
    return datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")


filename = "ps_runs.root"

# create a res folder
if not os.path.exists('res'):
    os.makedirs('res')
path = 'res/' + get_time() + "_" + filename
if not os.path.exists(path):
    print("creating")
    print(path)
    os.makedirs(path)
    # png and svg paths
    os.makedirs(path + '/png')
    os.makedirs(path + '/svg')


# Get the tree in the ROOT file
tree = uproot.open(filename)["PKUP"]
print("test")

# Now get the branches of interest
PulseIntensity = tree.arrays('PulseIntensity')
psTime = tree.arrays('psTime')
# Create a pandas data frame, which is used to apply the cuts
PulseIntensity_list = PulseIntensity['PulseIntensity'].tolist()
psTime_list = psTime['psTime'].tolist()

# Create a pandas data frame, which is used to apply the cuts
data = {'PulseIntensity': PulseIntensity_list, 'psTime': psTime_list}
df = pd.DataFrame(data)
def plot(start, end):
    # Get only the events, which 'survive' the cut
    events = df.query('psTime > ' + str(start*1000000000) + ' and psTime < ' + str(end*1000000000))

    integral = trapz(events['PulseIntensity'])

    # print("Integral:", integral)

    # number of start, end and num of events and mean
    print("\nfrom", start, "to", end)
    print("Number of events:", len(events))
    print("mean", integral/len(events))

    # --------------------------------------------------------------------
    # PLOT THE DATA
    # --------------------------------------------------------------------

    # Create the plot of the positions
    plt.hist(events['PulseIntensity'], bins=1000, range=(0, 1e13), color='blue')
    # Some labels
    plt.xlabel('PulseIntensity [protons per bunch]')
    plt.ylabel('count')
    plt.title('PulseIntensity count from ' + str(start) + 's to ' + str(end) + 's')

    # Save the plot and show it
    plt.savefig(path + '/png/' + "PulseIntensity_count_from_" + str(start*1000000000) + "ns_to_" + str(
        end*1000000000) + 'ns.png', dpi=500)
    plt.savefig(path + '/svg/' + "PulseIntensity_count_from_" + str(start * 1000000000) + "ns_to_" + str(
        end * 1000000000) + 'ns.svg', dpi=500)
    #plt.show()
    plt.close()



# start and end times from date_extractor.py in seconds, later converted into nanoseconds
times = [
    [1729840096.72937, 1729843044.55999],
    [1729843044.68361, 1729845481.19381],
    [1729845481.37521, 1729847130.14010],
    [1729797739.40546, 1729799304.41297],
    [1729799304.66007, 1729800523.70628],
    [1729801234.77148, 1729801959.67736],
    [1729801973.09962, 1729805035.16085],
    [1729805035.24105, 1729809544.70162],
    [1729809544.73806, 1729813145.74511],
    [1729813145.87142, 1729815262.60251],
    [1729815262.63506, 1729817360.51475],
    [1729817360.68143, 1729819457.73706],
    [1729819457.76884, 1729823355.27460],
    [1729823355.30451, 1729826639.62261],
    [1729826639.65881, 1729828691.59112],
    [1729828691.63098, 1729831033.95082],
    [1729831033.98866, 1729833362.52349],
    [1729833362.65571, 1729835854.31258],
    [1729835854.61360, 1729838335.83530],
    [1729838335.86145, 1729838555.42731],
    [1729851279.89043, 1729854186.17467],
    [1729854186.20408, 1729856578.93663],
    [1729856578.96874, 1729859190.91687],
    [1729847734.58315, 1729851006.19678]
]

# --------------------------------------------------------------------
# PLOT THE DATA
# --------------------------------------------------------------------

for pair in times:
    plot(pair[0], pair[1])
    # pass


# --------------------------------------------------------------------
# HISTOGRAM OF THE TIME DIFFERENCE BETWEEN EACH INTENSITY BETWEEN 0.15e13 AND 0.4e13
# --------------------------------------------------------------------

# get all times when the intensity is between 0.15e13 and 0.4e13
target_list = []
for i in range(len(PulseIntensity_list)):
    if 0.15e13 < PulseIntensity_list[i] < 0.4e13:
        target_list.append(psTime_list[i])
#print(target_list)
#print(len(target_list))

# get difference between each time
diff_list = []
for i in range(len(target_list)-1):
    diff_list.append((target_list[i+1] - target_list[i])/1e9)
#print(diff_list)
#print(len(diff_list))
#print(sum(diff_list)/len(diff_list))

# plot the histogram of the differences
plt.hist(diff_list, bins=100, range=(0,50), color='blue')
plt.xlabel('Time difference [s]')
plt.ylabel('count')
plt.title("Time difference between each intensity between 0.15e13 and 0.4e13")
plt.savefig(path + '/png/' + "Time_difference_between_each_intensity_between_0.15e13_and_0.4e13.png", dpi=500)
plt.savefig(path + '/svg/' + "Time_difference_between_each_intensity_between_0.15e13_and_0.4e13.svg", dpi=500)
plt.show()
plt.close()


# --------------------------------------------------------------------
# HISTOGRAM OF THE TIME DIFFERENCE BETWEEN EACH INTENSITY BETWEEN 0.8e13 AND 1.0e13
# --------------------------------------------------------------------

# get all times where the intensity is between 0.8e13 and 1.0e13
target_list_high = []
for i in range(len(PulseIntensity_list)):
    if 0.8e13 < PulseIntensity_list[i] < 1.0e13:
        target_list_high.append(psTime_list[i])
#print(target_list)
#print(len(target_list))

# get difference between each time
diff_list_high = []
for i in range(len(target_list_high)-1):
    diff_list_high.append((target_list_high[i+1] - target_list_high[i])/1e9)
#print(diff_list)
#print(len(diff_list))
#print(sum(diff_list)/len(diff_list))

# plot the histogram of the differences
plt.hist(diff_list_high, bins=100, range=(0,50), color='red')
plt.xlabel('Time difference [s]')
plt.ylabel('count')
plt.title("Time difference between each intensity between 0.8e13 and 1.0e13")
plt.savefig(path + '/png/' + "Time_difference_between_each_intensity_between_0.8e13_and_1.0e13.png", dpi=500)
plt.savefig(path + '/svg/' + "Time_difference_between_each_intensity_between_0.8e13_and_1.0e13.svg", dpi=500)
plt.show()
plt.close()


# --------------------------------------------------------------------
# COMPARISON OF THE TWO HISTOGRAMS
# --------------------------------------------------------------------

plt.hist(diff_list, bins=100, range=(0,50), color='blue', alpha=0.5, label='0.15e13 to 0.4e13')
plt.hist(diff_list_high, bins=100, range=(0,50), color='red', alpha=0.5, label='0.8e13 to 1.0e13')
plt.xlabel('Time difference [s]')
plt.ylabel('count')
plt.title("Comparison of the time difference between each intensity")
plt.legend()
plt.savefig(path + '/png/' + "Comparison_of_the_time_difference_between_each_intensity.png", dpi=500)
plt.savefig(path + '/svg/' + "Comparison_of_the_time_difference_between_each_intensity.svg", dpi=500)
plt.show()
