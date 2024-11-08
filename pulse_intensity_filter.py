import uproot
import numpy as np
import os
import matplotlib.pyplot as plt
import datetime
import pandas as pd

def get_time():
    return datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

if not os.path.exists('res_pulse_intensity_filter'):
    os.makedirs('res_pulse_intensity_filter')
path = 'res_pulse_intensity_filter/' + get_time()
if not os.path.exists(path):
    os.makedirs(path)
    # print("creating")
    print(path + "\n")
    # png and svg paths
    os.makedirs(path + '/png')
    os.makedirs(path + '/svg')


def plot(filename, source_dir):
    # open root file from PS
    file_ps = uproot.open("ps_runs.root")
    # get tree
    tree_ps = file_ps["PKUP"]
    psTime_tree = tree_ps.arrays('psTime')
    PulseIntensity = tree_ps.arrays('PulseIntensity')

    # open root file from EXPERIMENT
    file_experiment = uproot.open(source_dir + "/" + filename)
    # get tree
    tree_experiment = file_experiment["clusters_detector"]

    # get arrays
    time_0 = tree_experiment.arrays("time0")
    time_0_algo = tree_experiment.arrays("time0_algo")

    # create lists for conversioin to ns and for plotting
    time_0_list = time_0["time0"].tolist()
    time_0_list = [x + 1729797739 * 1e+9 for x in time_0_list] # convert to UNIX time
    time_0_algo_list = time_0_algo["time0_algo"].tolist()
    psTime_list = psTime_tree["psTime"].tolist()
    PulseIntensity_list = PulseIntensity['PulseIntensity'].tolist()
    trigger_time = [int((time0 - time0_algo)/1e6)*1e6 for time0, time0_algo in zip(time_0_list, time_0_algo_list)]

    # cerate a pandas data frame
    data = {'time0': time_0_list, 'time0_algo': time_0_algo_list, 'trigger_time': trigger_time}
    df = pd.DataFrame(data)

    data_ps = {'psTime': psTime_list, 'PulseIntensity': PulseIntensity["PulseIntensity"].tolist()}
    df_ps = pd.DataFrame(data_ps)

    # calcukate start and end of the cut for psTime data
    # get fist trigger time
    start = df["trigger_time"].iloc[0]
    # get last trigger time
    end = df["trigger_time"].iloc[-1]

    # UNIX time in ns when the computer was last connected to the internet
    last_connected = 1729704600 * 1e+9
    # time difference between the last connected time and the start of the experiment
    time_diff_start = start - last_connected
    # time difference between the last connected time and the end of the experiment
    time_diff_end = end - last_connected

    print("time_diff in ns from last connected to network to experiment start:", time_diff_start)
    print("time_diff in ns from last connected to network to experiment end:", time_diff_end)
    # per second from last connected to network to experiment start, the time shift is 6.486254917 ns per second
    time_shift_per_s = 6486.254917
    cut_start = start + ((time_diff_start/1e+9) * time_shift_per_s)
    cut_end = end + ((time_diff_end/1e+9) * time_shift_per_s)
    print("cut_start:", cut_start/1e+9)
    print("cut_end:", cut_end/1e+9)

    # make cut for psTime data
    events = df_ps.query('psTime >= ' + str(cut_start) + ' and psTime <= ' + str(cut_end))
    print(events)

    # get num of unique trigger_time values in df
    unique_trigger_time = df["trigger_time"].nunique()
    # list of unique trigger_time values
    unique_trigger_time_list = df["trigger_time"].unique()
    print("Number of unique trigger_time values:", unique_trigger_time)
    print(df)

    # create hist of trigger_time values vs hist of psTime values in comparison in one plot
    fig, ax = plt.subplots()
    ax.hist(unique_trigger_time_list, bins=100, color='blue', label='trigger_time', alpha=0.5)
    ax.hist(events["psTime"], bins=100, color='red', label='psTime', alpha=0.5)
    ax.set_xlabel('unix time [ns]')
    ax.set_ylabel('count')
    ax.set_title('trigger_time vs psTime\n' + filename)
    ax.legend()
    plt.savefig(path + '/png/' + "trigger_time_vs_psTime" + '.png', dpi=500)
    plt.savefig(path + '/svg/' + "trigger_time_vs_psTime" + '.svg', dpi=500)
    plt.show()
    plt.close()

    # calculate the time diff to last connected to network for every unique trigger_time value
    shifted_trigger_time_list = []
    shift_amount_list = []
    for time in unique_trigger_time_list:
        time_diff = time - last_connected
        print("time_diff in ns from last connected to network to trigger_time:", time_diff)
        shifted_time = time + ((time_diff/1e9) * time_shift_per_s)
        shifted_trigger_time_list.append(shifted_time)
        print("old time:", time)
        print("new time:", shifted_time)
        shift_amount = shifted_time - time
        shift_amount_list.append(shift_amount)
        print("shift amount:", shift_amount)
        print("\n")

    # create hist of shifted_trigger_time values vs hist of psTime values in comparison in one plot
    fig, ax = plt.subplots()
    ax.hist(shifted_trigger_time_list, bins=100, color='blue', label='shifted_trigger_time', alpha=0.5)
    ax.hist(events["psTime"], bins=100, color='red', label='psTime', alpha=0.5)
    ax.set_xlabel('unix time [ns]')
    ax.set_ylabel('count')
    ax.set_title('shifted_trigger_time vs psTime\n' + filename)
    ax.legend()
    plt.savefig(path + '/png/' + "shifted_trigger_time_vs_psTime" + '.png', dpi=500)
    plt.savefig(path + '/svg/' + "shifted_trigger_time_vs_psTime" + '.svg', dpi=500)
    plt.show()
    plt.close()

    # plot the unique_trigger_time and shifted_trigger_time_list in one plot and plot the shift amount with them
    fig, ax1 = plt.subplots()
    ax1.plot(unique_trigger_time_list, color='blue', label='trigger_time')
    ax1.plot(shifted_trigger_time_list, color='red', label='shifted_trigger_time')
    ax1.set_xlabel('index')
    ax1.set_ylabel('unix time [ns]')
    ax1.set_title('trigger_time vs shifted_trigger_time and shift amount\n' + filename)
    ax1.legend()

    ax2 = ax1.twinx()
    ax2.plot(shift_amount_list, color='green', label='shift_amount')
    ax2.set_ylabel('shift amount [ns]')
    #ax2.legend()

    plt.savefig(path + '/png/' + "trigger_time_vs_shifted_trigger_time" + '.png', dpi=500)
    plt.savefig(path + '/svg/' + "trigger_time_vs_shifted_trigger_time" + '.svg', dpi=500)
    plt.show()
    plt.close()

    # calculate difference of shifted_trigger_time_list and trigger_time
    diff_list = []
    for i in range(len(shifted_trigger_time_list)):
        diff_list.append(shifted_trigger_time_list[i] - unique_trigger_time_list[i])
    print(diff_list)

    # plot diff list vs shift_amount_list
    fig, ax = plt.subplots()
    ax.plot(diff_list, color='blue', label='diff_list')
    ax.plot(shift_amount_list, color='red', label='shift_amount_list')
    ax.set_xlabel('index')
    ax.set_ylabel('time [ns]')
    ax.set_title('diff_list vs shift_amount_list\n' + filename)
    ax.legend()
    plt.savefig(path + '/png/' + "diff_list_vs_shift_amount_list" + '.png', dpi=500)
    plt.savefig(path + '/svg/' + "diff_list_vs_shift_amount_list" + '.svg', dpi=500)
    plt.show()
    plt.close()


    # get low and high intenisty values from PulseIntensity_list
    target_list_low = []
    target_list_high = []
    for i in range(len(PulseIntensity_list)):
        if 0.15e13 < PulseIntensity_list[i] < 0.4e13:
            target_list_low.append(psTime_list[i])
        if 0.8e13 < PulseIntensity_list[i] < 1.0e13:
            target_list_high.append(psTime_list[i])

    # plot the histogram of low intensity values
    plt.hist(target_list_low, bins=250, color='blue')
    plt.xlabel('UNIX Time [ns]')
    plt.ylabel('count')
    plt.title("Pulse Intensity between 0.15e13 and 0.4e13 vs time\n" + filename)
    plt.savefig(path + '/png/' + "Pulse_Intensity_between_0.15e13_and_0.4e13_vs_time" + '.png', dpi=500)
    plt.savefig(path + '/svg/' + "Pulse_Intensity_between_0.15e13_and_0.4e13_vs_time" + '.svg', dpi=500)
    plt.show()
    plt.close()

    # plot the histogram of high intensity values
    plt.hist(target_list_high, bins=250, color='red')
    plt.xlabel('UNIX Time [ns]')
    plt.ylabel('count')
    plt.title("Pulse Intensity between 0.8e13 and 1.0e13 vs time\n" + filename)
    plt.savefig(path + '/png/' + "Pulse_Intensity_between_0.8e13_and_1.0e13_vs_time" + '.png', dpi=500)
    plt.savefig(path + '/svg/' + "Pulse_Intensity_between_0.8e13_and_1.0e13_vs_time" + '.svg', dpi=500)
    plt.show()
    plt.close()

    # compare the two histograms
    plt.hist(target_list_low, bins=250, color='blue', alpha=0.5, label='low intensity')
    plt.hist(target_list_high, bins=250, color='red', alpha=0.5, label='high intensity')
    plt.xlabel('UNIX Time [ns]')
    plt.ylabel('count')
    plt.title("Comparison of Pulse Intensity between 0.15e13 and 0.4e13 and 0.8e13 and 1.0e13\n" + filename)
    plt.legend()
    plt.savefig(path + '/png/' + "Comparison_of_Pulse_Intensity_between_0.15e13_and_0.4e13_and_0.8e13_and_1.0e13" + '.png', dpi=500)
    plt.savefig(path + '/svg/' + "Comparison_of_Pulse_Intensity_between_0.15e13_and_0.4e13_and_0.8e13_and_1.0e13" + '.svg', dpi=500)
    plt.show()
    plt.close()



    # plot psTime vs index
    fig, ax = plt.subplots()
    ax.plot(psTime_list, color='blue')
    ax.set_xlabel('index')
    ax.set_ylabel('time [ns]')
    ax.set_title('psTime vs index\n' + filename)
    plt.savefig(path + '/png/' + "psTime_vs_index" + '.png', dpi=500)
    plt.savefig(path + '/svg/' + "psTime_vs_index" + '.svg', dpi=500)
    plt.show()
    plt.close()



    # get all event for which time0_algo is smaller than 10ms
    events = df.query('time0_algo < 10e6 and time0_algo > 1e6')
    print(events)
    # plot the histogram of the events
    plt.hist(events["time0_algo"], color='blue', bins=250, histtype='step')
    plt.xlabel('time [ns]')
    plt.ylabel('count')
    plt.title("time0_algo < 10ms and > 1ms\n" + filename)
    plt.savefig(path + '/png/' + "time0_algo_smaller_10ms_and_bigger_1ms" + '.png', dpi=500)
    plt.savefig(path + '/svg/' + "time0_algo_smaller_10ms_and_bigger_1ms" + '.svg', dpi=500)
    plt.show()
    plt.close()


    # match psTime with trigger_time and created matched df from it incliding the PulseIntensity and time0_algo values
    matched_df = pd.DataFrame()
    for i in range(len(events)):
        print("i:", i)
        event = events.iloc[i]
        # get shift amount
        shift_amount = (event["trigger_time"] - last_connected)/1e9 * time_shift_per_s
        psTime_min = event["trigger_time"] - shift_amount
        psTime_max = event["trigger_time"] + shift_amount
        matched_event = df_ps.query('psTime >= ' + str(psTime_min) + ' and psTime <= ' + str(psTime_max))
        # get best match
        best_match = matched_event.iloc[0]
        # add PulseIntensity and time0_algo to the event
        event["PulseIntensity"] = best_match["PulseIntensity"]
        event["time0_algo"] = event["time0_algo"]
        matched_df = matched_df._append(event)

    print("matched", matched_df)

    # get all events for which PulseIntensity is between 0.15e13 and 0.4e13
    events_low = matched_df.query('PulseIntensity > 0.15e13 and PulseIntensity < 0.4e13')
    # get all events for which PulseIntensity is between 0.8e13 and 1.0e13
    events_high = matched_df.query('PulseIntensity > 0.8e13 and PulseIntensity < 1.0e13')
    # plot the histogram of the events in comparison
    plt.hist(events_low["time0_algo"], bins=250, color='blue', label='low intensity', histtype='step')
    plt.hist(events_high["time0_algo"], bins=250, color='red', label='high intensity', histtype='step')
    plt.xlabel('time [ns]')
    plt.ylabel('count')
    plt.title("Comparison of time0_algo for Pulse Intensity between 0.15e13 and 0.4e13 and 0.8e13 and 1.0e13\n" + filename)
    plt.legend()
    plt.savefig(path + '/png/' + "Comparison_of_time0_algo_for_Pulse_Intensity_between_0.15e13_and_0.4e13_and_0.8e13_and_1.0e13" + '.png', dpi=500)
    plt.savefig(path + '/svg/' + "Comparison_of_time0_algo_for_Pulse_Intensity_between_0.15e13_and_0.4e13_and_0.8e13_and_1.0e13" + '.svg', dpi=500)
    plt.show()
    plt.close()















plot("Gd157_n_tof_5200V_6mVfC_40mV_DDR_masked_00003_20241025013905_20241107011232_algo_7_tof.root", "new_root")






