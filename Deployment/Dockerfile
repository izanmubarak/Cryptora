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

# Download Cryptora
RUN git clone https://github.com/izanmubarak/Cryptora.git

# "cd" (essentially) into the Cryptora folder
WORKDIR Cryptora

# Install Cryptora dependencies
RUN python -m pip install -r requirements.txt