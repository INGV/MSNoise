ROM mambaorg/micromamba:1.5.8

USER root

WORKDIR /home/msnoise

ENV DEBIAN_FRONTEND="noninteractive"

COPY --chown=$MAMBA_USER:$MAMBA_USER env.yaml /home/msnoise/env.yaml

RUN micromamba create -y -f /home/msnoise/env.yaml \
    &&  micromamba clean --all --yes

ENV ENV_NAME=msnoise

ARG MAMBA_DOCKERFILE_ACTIVATE=1

RUN sed -i 's/import scipy.fftpack._fftpack as sff/import scipy.fftpack as sff/g' /opt/conda/envs/msnoise/lib/python3.9/site-packages/msnoise/api.py

# System packages 
RUN apt-get update \
    && apt-get install -yq sudo wget jq vim inetutils-ping openssh-server net-tools gnupg lsb-release \
    && apt install apt-transport-https curl -y \
    && mkdir -p /etc/apt/keyrings \
    && curl -o /etc/apt/keyrings/mariadb-keyring.pgp 'https://mariadb.org/mariadb_release_signing_key.pgp' \
    && apt update \
    && apt install mariadb-server -y

COPY create_schema_user_and_grants.sql /home/msnoise

# Setup ssh access
#RUN mkdir /var/run/sshd
#RUN echo 'msnoise:msnoise' | chpasswd
#RUN echo X11Forwarding yes >> /etc/ssh/sshd_config
#RUN echo X11UseLocalhost no >> /etc/ssh/sshd_config
#RUN echo AllowAgentForwarding yes >> /etc/ssh/sshd_config
#RUN echo PermitRootLogin yes >> /etc/ssh/sshd_config
# SSH login fix. Otherwise user is kicked off after login
#RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd 

EXPOSE 5000

EXPOSE 6901

EXPOSE 22

#CMD ["/usr/sbin/sshd","-D"]
CMD "mariadbd-safe"
