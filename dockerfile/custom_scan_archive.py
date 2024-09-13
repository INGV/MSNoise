import os
import subprocess

# Input file containing year_to_scan, network, channel, and no_scan_station
input_file = "scan_archive_script_params.txt"

# Initialize variables
year_to_scan = ""
network = ""
channel = ""
no_scan_station = ""

# Read the parameters from the input file
with open(input_file, 'r') as f:
    for line in f:
        line = line.strip()
        # Check if the line starts with "year_to_scan=", "network=", "channel=", or "no_scan_station="
        if line.startswith("year_to_scan="):
            year_to_scan = line.split("=", 1)[1]
        elif line.startswith("network="):
            network = line.split("=", 1)[1]
        elif line.startswith("channel="):
            channel = line.split("=", 1)[1]
        elif line.startswith("no_scan_station="):
            no_scan_station = line.split("=", 1)[1]

# Convert comma-separated years, networks, channels, and no_scan_station into lists
year_list = year_to_scan.split(',')
network_list = network.split(',')
channel_list = channel.split(',')
no_scan_station_list = no_scan_station.split(',')

# Loop through each combination of year and network
for year in year_list:
    for net in network_list:
        # Define the base network path
        base_network_path = f"/remote-sds-archive/{year}/{net}/"

        # Find all station folders within the network path
        try:
            station_folders = [f.path for f in os.scandir(base_network_path) if f.is_dir()]
        except FileNotFoundError:
            print(f"Path not found: {base_network_path}")
            continue

        for station_path in station_folders:
            # Extract the station name from the path
            station_name = os.path.basename(station_path)

            # Check if the station is in the no_scan_station list
            if station_name in no_scan_station_list:
                print(f"Skipping station: {station_name}")
                continue  # Skip this station

            # Loop through each channel and construct path
            for chan in channel_list:
                # Construct path with station and channel
                full_path = os.path.join(base_network_path, station_name, f"{chan}.D")

                # Check if the full path exists before executing the command
                if os.path.exists(full_path):
                    # Build and execute the msnoise scan_archive command
                    command = ["msnoise", "scan_archive", "--path", full_path, "--recursively"]
                    print(f"Running msnoise scan_archive for path: {full_path}")
                    
                    # Execute the command
                    subprocess.run(command, check=True)
                else:
                    print(f"Channel path not found: {full_path}")

