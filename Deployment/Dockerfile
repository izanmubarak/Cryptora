############################################################
# Dockerfile to build Cryptora
# Based on Ubuntu
############################################################

# Set the base image to Ubuntu
FROM ubuntu:latest

# File Author / Maintainer (Put your name here!)
MAINTAINER Anonymous

# Get basic tools (Python, pip, git)
RUN apt update
RUN apt install -y python2.7 python-pip
RUN apt install -y git

# Set time zone to allow for historical pricing to work (timezone strings at https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)
ENV TZ=America/New_York
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get install -y tzdata
RUN ln -fs /usr/share/zoneinfo/America/New_York /etc/localtime
RUN dpkg-reconfigure --frontend noninteractive tzdata

# Download Cryptora
RUN git clone https://github.com/izanmubarak/Cryptora.git

# "cd" (essentially) into the Cryptora folder
WORKDIR Cryptora

# Install Cryptora dependencies
RUN python -m pip install -r requirements.txt