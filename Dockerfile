FROM ubuntu:19.04

# set environment encoding and some base utils
ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y wget curl git

# should we add --no-install-recommends?

# texlive install
RUN apt-get install -y xzdec texlive-full latexmk

# texlive update and install reledmac
RUN tlmgr init-usertree
RUN tlmgr option repository http://mirror.ctan.org/systems/texlive/tlnet
RUN tlmgr update --self
RUN tlmgr install reledmac

# Manual install libertine
RUN wget http://mirrors.ctan.org/install/fonts/libertine.tds.zip
WORKDIR /texmf
RUN unzip /libertine.tds.zip
RUN texhash
RUN updmap --user --enable Map=libertine.map

# Java
RUN apt-get install -y default-jre

# Python and pip
RUN apt-get install -y python3.6 python3-pip

# App directory and install
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# Create necessary dirs that are excluded via .gitignore
RUN mkdir upload static static/output logs cache

# Copy in the app content
COPY requirements.txt /usr/src/app/
RUN python3.6 -m pip install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

COPY texmf/ /root/texmf

EXPOSE 80

CMD gunicorn --worker-class eventlet -w 1 -b 0.0.0.0:80 service:app
