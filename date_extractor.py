import dpkt
import os


def get_pcapng_time_range(file_path):
    # Open the file in binary read mode
    with open(file_path, 'rb') as f:
        pcapng = dpkt.pcapng.Reader(f)

        # Initialize the first and last timestamps
        last_timestamp = None
        first_timestamp = None

        # set the first packet as the first packet
        first_packet = next(pcapng)
        first_timestamp = first_packet[0]
        # Iterate over packets and only keep the last one
        for timestamp, buf in pcapng:
            last_timestamp = timestamp

        return first_timestamp, last_timestamp


source_dir = 'pcapng'
for file in os.listdir(source_dir):
    try:
        file_path = source_dir + '/' + file
        start, end = get_pcapng_time_range(file_path)
        print(file, start, end)
    except:
        print(file, "-", "-")

