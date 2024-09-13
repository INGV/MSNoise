FROM ubuntu:latest

USER root

# System packages 
RUN apt-get update \ 
    && apt-get install -yq sudo wget jq vim inetutils-ping openssh-server net-tools gnupg lsb-release cron \
    && apt install apt-transport-https curl -y \
    && mkdir -p /etc/apt/keyrings \
    && curl -o /etc/apt/keyrings/mariadb-keyring.pgp 'https://mariadb.org/mariadb_release_signing_key.pgp' \
    && apt update \
    && apt install mariadb-server -y 

# Create user msnoise with home directory and add to sudo group
RUN useradd -ms /bin/bash msnoise && echo 'msnoise:msnoise' | chpasswd && adduser msnoise sudo

# Copy SQL script to create schema
COPY create_schema_user_and_grants.sql /home/msnoise

# Allow passwordless sudo for msnoise user
RUN echo 'msnoise ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers.d/msnoise \
    && chmod 0440 /etc/sudoers.d/msnoise

# Create necessary directories and setup SSH (run as root)
RUN mkdir /var/run/sshd \
    && echo 'X11Forwarding yes' >> /etc/ssh/sshd_config \
    && echo 'X11UseLocalhost no' >> /etc/ssh/sshd_config \
    && echo 'AllowAgentForwarding yes' >> /etc/ssh/sshd_config \
    && echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config \
    && sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

# Switch to msnoise user after system configuration
USER msnoise

WORKDIR /home/msnoise

# Install Python packages (can be done as msnoise user)
RUN sudo chown -R msnoise:msnoise /home/msnoise

RUN sudo apt-get install python3-pip -y \ 
    && pip3 install http://msnoise.org/master.zip --break-system-packages \
    && pip install https://github.com/obspy/obspy/archive/master.zip --break-system-packages \
    && python3 -m pip install tables --break-system-packages \ 
    && pip3 install pyqt5 --break-system-packages \ 
    && pip install cftime --break-system-packages 

# Cron to keep alive msnoise admin web interface
RUN crontab -l | { cat; echo "* * * * * cd /home/msnoise && /usr/bin/python3 /home/msnoise/kill_and_restart_msnoise.py >> /home/msnoise/log/cron_log.log 2>&1"; } | crontab - 

# Make dir for script log
RUN mkdir log

# Add code to .bash_profile to source .bashrc
RUN echo 'if [ -f ~/.bashrc ]; then\n  . ~/.bashrc\nfi' >> /home/msnoise/.bash_profile \
    && echo 'export PATH="/home/msnoise/.local/bin:$PATH"' >> /home/msnoise/.bashrc

# Add MySQL environment variables to .bashrc
RUN echo 'export MYSQL_USER=msnoise' >> /home/msnoise/.bashrc \
    && echo 'export MYSQL_PASSWORD=msnoise' >> /home/msnoise/.bashrc \
    && echo 'export MYSQL_DATABASE=msnoise' >> /home/msnoise/.bashrc \
    && echo 'export MYSQL_ROOT_PASSWORD=msnoise' >> /home/msnoise/.bashrc

# Copy scripts to /home/msnoise
COPY README custom_scan_archive.py generate_interferogram_files.py scan_archive_script_params.txt update_table_stations_with_lat_lon_elev.py create_schema_user_and_grants.sql kill_and_restart_msnoise.py /home/msnoise

# Expose the necessary ports
EXPOSE 5000
EXPOSE 6901
EXPOSE 22

# Start MariaDB and SSHD together (run as root)
CMD sudo service ssh start && sudo service cron start && sudo mariadbd-safe 
