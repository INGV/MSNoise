import pymysql
import datetime
import subprocess
import datetime
import os
import shutil
import re

# Database connection parameters
Host = "localhost"
User = "msnoise"
Password = "msnoise"
database = "msnoise"

# Connect to the database
conn = pymysql.connect(host=Host, user=User, password=Password, database=database)

# Create a cursor object
cur = conn.cursor()

# Fetch net, sta, and used_location_code from the database
query = "SELECT net, sta, used_location_codes FROM stations"
cur.execute(query)
rows = cur.fetchall()

# Close the database connection after fetching the data
conn.close()

# Generate net.sta format for all rows, handling multiple location codes
net_sta_list = []
for net, sta, loc_codes in rows:
    if loc_codes and loc_codes != '--':  # If location codes exist and aren't just '--'
        # Split location codes if there are multiple (comma-separated)
        loc_code_list = loc_codes.split(',')
        for loc_code in loc_code_list:
            net_sta = f"{net}.{sta}.{loc_code.strip()}"  # Strip any whitespace
            net_sta_list.append(net_sta)
    else:
        net_sta = f"{net}.{sta}"  # No location code, just net and station
        net_sta_list.append(net_sta)

# Generate the current timestamp in the desired format (DDMMYYYY-HH:MM:SSS)
timestamp = datetime.datetime.now().strftime("%d%m%Y-%H%M%S")

# Generate and execute commands for each pair of net.sta
for i in range(len(net_sta_list)):
    net_sta1 = net_sta_list[i]
    for j in range(i + 1, len(net_sta_list)):
        net_sta2 = net_sta_list[j]

        # Define the command to generate interferogram, with timestamp in the filename
        command = f"msnoise cc plot interferogram {net_sta1} {net_sta2} -o interferogram_{net_sta1}-{net_sta2}_{timestamp}.png"

        # Print the command for debugging purposes
        print(f"Executing command: {command}")

        # Execute the command
        subprocess.run(command, shell=True, check=True)

print("All commands executed successfully")

## Rename and move interferogram files

# Path to the folder containing the original files
original_folder_path = './'

# Function to rename and move 'interferogram' files to a new folder
def rename_and_move_interferogram_files(original_folder_path):
    # Ensure the folder path exists
    if not os.path.isdir(original_folder_path):
        print(f"The folder path '{original_folder_path}' does not exist.")
        return

    # Create a timestamp for the new folder
    timestamp = datetime.datetime.now().strftime("%d%m%Y")

    # Create the new folder with the timestamp
    outcome_folder = "/msnoise-outcome-files" # Folder mapped with same folder on host file system at /home/sysop/dockerApps/docker-compose/msnoise-2.0/msnoise-outcome-files
    new_folder_name = f"{outcome_folder}/msnoise_interferogram_{timestamp}"
    new_folder_path = os.path.join(original_folder_path, new_folder_name)
    os.makedirs(new_folder_path, exist_ok=True)

    # Iterate over all files in the original folder
    for filename in os.listdir(original_folder_path):
        old_filepath = os.path.join(original_folder_path, filename)

        # Only process files that start with "interferogram " and skip directories
        if os.path.isfile(old_filepath) and filename.startswith("interferogram "):
            # Remove the redundant "interferogram " from the filename
            new_filename = re.sub(r'^interferogram\s+', '', filename)

            # Define the new file path in the new folder
            new_filepath = os.path.join(new_folder_path, new_filename)

            # Rename and move the file
            shutil.move(old_filepath, new_filepath)

            # Print the operation for confirmation
            print(f"Renamed and moved: {filename} -> {new_filename}")

    print(f"All interferogram files have been renamed and moved to {new_folder_path}")

# Run the function to rename and move files
rename_and_move_interferogram_files(original_folder_path)

