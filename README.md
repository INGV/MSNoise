# Docker Compose File and Dockerfile for MSNoise
## Content

This repository contains the Dockerized implementation of the open-source package MSNoise, a Python library for monitoring seismic velocity changes (dv/v) using ambient seismic noise correlation, in addition to some customized solutions to offer a better user experience..

## How to Proceed

# Build image
Go into dockerfile folder and build image by running command

     docker build -t msnoise:latest . 

and go back to the previous folder .

### Starting the Containers
From within this folder, by running the command

```
docker compose up -d
```

the container with the service defined in the file will be created.

By running the command

```
docker compose ps
```

you should expect to find a row in the command output with the name of the container and other fields, including the STATUS with the value 'UP'.

If that's not the case, there may have been some errors, meaning the container was not instantiated correctly.

By running the command


```
docker compose ps -a
```

you should find in the row related to the container a STATUS of type 'Exited'.

At this point, you can run the command

```
docker compose logs  
```

to try to understand the reason that prevented the container from being instantiated correctly.

### Stopping and Removing the Containers

From within this folder, run the command

```
docker compose down
```

In this way, all containers instantiated based on the docker-compose.yml file will be stopped and removed, including the networks defined in the file. Only the volumes in the folder /var/lib/docker/volumes will remain.

The command

```
docker compose stop
```

stops the container without removing it.

For any further information, refer to the official Docker Compose documentation at https://docs.docker.com/compose/reference/.


## Accessing the Container

Once the container is instantiated, you can access it with

```
docker exec -it msnoise bash
```

or via ssh

```
ssh -X msnoise@localhost -p 1001
```

password msnoise . 

## MSNoise GUI

Docker binds port 5000 between the host and the container itself, so by typing **http://localhost:5000** into your browser, you can access the graphical interface from which you can configure the parameters needed for processing or check the progress of jobs.

If port 5000 is already in use on your machine, you can assign another one by editing the docker-compose.yml file in the **ports** section, changing the port value to the left of the colon.

# How to start msnoise and generate interferograms

1. From msnoise project folder execute 
	
        sudo mariadb < create_schema_user_and_grants.sql

to create schema and assign grants to msnoise data base user.

2. Execute
        
        msnoise db init

will appear a prompt, select 2 for mysql and press enter for all others option. 
For the password type 'msnoise'. If these operations are successful a file db.ini will be added in the 
project folder.

3. Set the start and end date from the configuration web interface - from a cli in the container type 'msnoise admin'
to start the embedded web server and in you broser type 'localhost:5000' to reach the web interface - or from the container CLI with 'msnoise config set startdate=$startdate ' command.
Also set cron days. Those option are needed by the msnoise scan_archive command.

4. To dynamically scan archive you must set property values for year, network, channel etc. into the scan_archive_script_params.txt . These properties
will be used by the custom_scan_archive.py .

5. Execute 

        python3 custom_scan_archive.py  

In this way the table data_availability will be populated with station's file path and other details . 
You can always use the data base from its cli typing in the container cli 'mariadb'. In this way a prompt of mariadb will appear. To use msnoise data base type 'use msnoise'. Remember to put always ';' at the end of every data base statement. If you want to show the content of data_availability table just type 'select * from data_availability;', same for other tables . If you want to see all the tables of the msnoise database 'show tables;' .

6. Now is possible to populate stations table with data retrieved from data_availability table executing

        msnoise populate --fromDA

7. Update stations table with latitude, longitute and elevation data retrieved from stations' station.xml files or from fdsn web service with

	python3 update_table_stations_with_lat_lon_elev.py

If one of the station is not found on fdsn web server you can put station's inventory file in the folder /inventories-for-station-not-on-fdsn folder with the format station_{net}_{sta}_inventory.xml .

8. Update jobs tabledd with 
        
        msnoise new_jobs --init

9. Add filters into filters table with 

        msnoise db execute "insert into filters (ref, low, mwcs_low, high, mwcs_high, mwcs_wlen, mwcs_step, used) values (1, 0.1, 0.1, 1.0, 1.0, 12.0, 4.0, 1)"

You can also add filters from web interface configuration page.

10. Start cross correlation computation (it could take a long time)

        msnoise cc compute_cc

11. Run in sequence 
       
        msnoise cc stack -r, msnoise reset STACK, msnoise cc stack -m

12. Now it's possible to generate an interefrogram image for each station pair running

        python3 generate_interferogram_files.py

A folder msnoise_interferograms$timestamp will be created with all interferograms into /msnoise-outcome-files folder mapped with a folder with same name on host file system to let you take data produced inside container
.

# Tips and tricks

### Cron jobs

A cron job has been set to execute the script kill_and_restart_msnoise.py every minute, which restarts the graphical interface every minute as it is often subject to freezes that prevent its normal use.

Also, if at any point during processing you think it is necessary to start over, in addition to deleting the output folders generated by the processing, delete all jobs with status I (in progress), remember to run the command 


        msnoise db execute “update data_availability set flag=‘M’ where flag=‘A’”

which makes all stations' archive files available again for new processing.

## Scripts

### update_table_stations_with_lat_lon_elev.py

To automate the filling of the stations table with latitude, longitude, and altitude data, we created a Python script called **update_table_stations_with_lat_lon_elev.py** . For each station in the archive, this script queries the INGV or EIDA database to download the relevant dataless file and extract the longitude, latitude, and elevation values.

If the dataless file is not present in the remote archive but is in your possession, you can add it to the folder **/inventories-for-station-not-on-fdsn** .





# Acknowledgements / Credits

The core processing engine of this project is based on the open-source package **MSNoise**. We gratefully acknowledge the work of the original developers.

* **MSNoise:** 
    * **Scientific Citation:** Lecocq, T., C. Caudron, et F. Brenguier (2014), MSNoise, a Python Package for Monitoring Seismic Velocity Changes Using Ambient Seismic Noise, Seismological Research Letters, 85(3), 715‑726, doi:10.1785/0220130073..
    * **Official Repository:** https://github.com/ROBelgium/MSNoise

# Licence

This project is released under EUPL v1.1 .