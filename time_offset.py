from scapy.all import rdpcap, UDP
import os
import matplotlib.pyplot as plt
import datetime
import uproot
import numpy as np

# get time
def get_time():
    return datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")


if not os.path.exists('res_time_offset'):
    os.makedirs('res_time_offset')
path = 'res_time_offset/' + get_time()
if not os.path.exists(path):
    os.makedirs(path)
    # print("creating")
    print(path + "\n")
    # png and svg paths
    os.makedirs(path + '/png')
    os.makedirs(path + '/svg')

list_PulseT = []

def t_from_pcang(filename):
    # Load the pcapng file
    packets = rdpcap("pcapng/" + filename)  # Replace with your file name
    # Iterate over packets to find UDP payloads
    for packet in packets[:]:
        if UDP in packet:
            # Extract the UDP payload
            udp_payload = bytes(packet[UDP].payload)
            # convert to hex
            # Print or process the payload
            #print("UDP Payload:", udp_payload)
            # locate Cookie   0x455353 in the payload
            cookie = udp_payload.find(b'\x00\x00\x45\x53\x53\x48')
            #print("Cookie found at:", cookie)
            # print the cookie
            #print("Cookie:", udp_payload[cookie:cookie + 6].hex())
            PulseT = int.from_bytes(udp_payload[10:14], "little")
            num_cycles = int.from_bytes(udp_payload[14:18], "little")
            t_cycle_ns = num_cycles * 11.35686096363
            t_total = PulseT*1e9 + t_cycle_ns
            print("PulseT in s", PulseT)
            if t_total not in list_PulseT:
                if list_PulseT != []:
                    if t_total > max(list_PulseT):
                        print("Difference", t_total - list_PulseT[-1])
                        list_PulseT.append(t_total)
                else:
                    list_PulseT.append(t_total)
            #print("clock_cycles", num_cycles)
            #print("time in ns from cycle", t_cycle_ns)
            #print("t_total ns", t_total)
            print("UNIX time", float(t_total/1e9))


# get all files
t_from_pcang("5_02_GdNat.pcapng")
print("Unique PulseT", list_PulseT)
print("Number of unique PulseT", len(list_PulseT))
diff_PulseT = []
for i in range(len(list_PulseT)-1):
    diff_PulseT.append(list_PulseT[i+1] - list_PulseT[i])

print("Average PuleT difference", sum(diff_PulseT)/len(diff_PulseT))



# create hist from pulse difference
plt.hist(diff_PulseT, bins=100)
plt.xlabel('PulseT difference')
plt.ylabel('Counts')
plt.title('PulseT difference')
plt.savefig(path + '/png/PulseT_difference.png', dpi=500)
plt.savefig(path + '/svg/PulseT_difference.svg', dpi=500)
plt.show()
plt.close()


# plot the unique PulseT as histogram
plt.hist(list_PulseT, bins=100)
plt.xlabel('PulseT')
plt.ylabel('Counts')
plt.title('PulseT')
plt.savefig(path + '/png/PulseT.png', dpi=500)
plt.savefig(path + '/svg/PulseT.svg', dpi=500)
plt.show()
plt.close()






# --------------------------------------------------------------------
# ROOT FILE
# --------------------------------------------------------------------

# Get the tree in the ROOT file
root_file = "ps_runs_new.root"
tree = uproot.open(root_file)["PKUP"]

psTime = tree.arrays('psTime')
PulseIntensity = tree.arrays('PulseIntensity')
psTime_list = psTime['psTime'].tolist()
PulseIntensity_list = PulseIntensity['PulseIntensity'].tolist()


serach_max = max(list_PulseT) - 6.144e8
serach_min = min(list_PulseT) - 6.144e8
print("Search max", serach_max)
print("Search min", serach_min)
# get all psTimes within the range of min and max
target_list = []
target_intensity = []
for i in range(len(psTime_list)):
    if serach_min < psTime_list[i] < serach_max:
        target_list.append(psTime_list[i])
        target_intensity.append(PulseIntensity_list[i])

    if psTime_list[i] > serach_max:
        break


print("Target list", target_list)


# plot psTime vs index and pulseIntensity vs index in one plot
fig, ax1 = plt.subplots()
ax2 = ax1.twinx()

color = 'tab:blue'
ax1.set_ylabel('PulseIntensity', color=color)
ax1.plot(target_intensity, color=color)
ax1.tick_params(axis='y', labelcolor=color)


color = 'tab:red'
ax2.set_xlabel('Index')
ax2.set_ylabel('psTime', color=color)
ax2.plot(target_list, color=color)
ax2.tick_params(axis='y', labelcolor=color)

fig.tight_layout()
plt.title('psTime and PulseIntensity vs Index')
plt.savefig(path + '/png/psTime_and_PulseIntensity_vs_Index.png', dpi=500)
plt.savefig(path + '/svg/psTime_and_PulseIntensity_vs_Index.svg', dpi=500)
plt.show()
plt.close()



# create comparison hist of the two lists
plt.hist(target_list, bins=250, range=(serach_min, serach_max),color='red', alpha=0.5, label='ROOT')
plt.hist(list_PulseT, bins=250, range=(serach_min, serach_max), color='blue', alpha=0.5, label='pcapng')
plt.xlabel('Time')
plt.ylabel('Counts')
plt.title('Comparison of ROOT and pcapng Time')
plt.legend()
plt.savefig(path + '/png/Comparison_of_ROOT_and_pcapng_Time.png', dpi=500)
plt.savefig(path + '/svg/Comparison_of_ROOT_and_pcapng_Time.svg', dpi=500)
plt.show()
plt.close()

# calculate difference between each item in list_PulseT and target_list
diff_list = []
min_length = min(len(list_PulseT), len(target_list))
index_shift = []
search_window = min_length
for i in range(min_length):
    c_diff = []
    # left window
    for j in range(search_window-1):
        try:
            c_diff.append(abs(list_PulseT[i-j-1] - target_list[i]))
        except IndexError:
            c_diff.append(np.inf)
    # center index
    c_diff.append(abs(list_PulseT[i] - target_list[i]))
    # right window
    for j in range(search_window-1):
        try:
            c_diff.append(abs(list_PulseT[i+j+1] - target_list[i]))
        except IndexError:
            c_diff.append(np.inf)
    x = min(c_diff)
    diff_list.append(x)
    index_shift.append(c_diff.index(x) - search_window)

print("Difference list", diff_list)
print("Index shift", index_shift)
# average shift
print("Average shift", sum(index_shift)/len(index_shift))

# average difference
average_diff = sum(diff_list)/len(diff_list)
print("Average difference", average_diff)

# create plot of the difference
plt.plot(diff_list)
plt.xlabel('Index')
plt.ylabel('Difference')
plt.title('Difference between ROOT and pcapng Time')
plt.savefig(path + '/png/Difference_between_ROOT_and_pcapng_Time.png', dpi=500)
plt.savefig(path + '/svg/Difference_between_ROOT_and_pcapng_Time.svg', dpi=500)
plt.show()
plt.close()



# create new comparison hist of ROOT and pcapng Time but with the average difference
root_list_with_diff = []
for i in range(len(target_list)):
    root_list_with_diff.append(target_list[i] - average_diff)
plt.hist(root_list_with_diff, bins=250, range=(serach_min, serach_max),color='red', alpha=0.5, label='ROOT')
plt.hist(list_PulseT, bins=250, range=(serach_min, serach_max), color='blue', alpha=0.5, label='pcapng')
plt.xlabel('Time')
plt.ylabel('Counts')
plt.title('Comparison of ROOT and pcapng Time with average difference' + '\n' + 'Average difference: ' + str(average_diff))
plt.legend()
plt.savefig(path + '/png/Comparison_of_ROOT_and_pcapng_Time_with_average_difference.png', dpi=500)
plt.savefig(path + '/svg/Comparison_of_ROOT_and_pcapng_Time_with_average_difference.svg', dpi=500)
plt.show()
plt.close()
