############################################################
# Dockerfile to build Cryptora
# Based on Python 3.12 slim
############################################################

FROM python:3.12-slim

# File Author / Maintainer (Put your name here!)
LABEL maintainer="Anonymous"

# Install git
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

# Set time zone to allow for historical pricing to work
ENV TZ=America/New_York
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Download Cryptora
RUN git clone https://github.com/izanmubarak/Cryptora.git

# "cd" (essentially) into the Cryptora folder
WORKDIR Cryptora

# Install Cryptora dependencies
RUN pip install --no-cache-dir -r requirements.txt
