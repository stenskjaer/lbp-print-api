FROM ubuntu:16.10

# set environment encoding and some base utils
ENV LANG C.UTF-8
RUN apt-get update && apt-get install -y wget curl git

# should we add --no-install-recommends?

# texlive install
RUN apt-get install -y xzdec texlive-xetex latexmk

# texlive update and install packages
RUN tlmgr init-usertree
RUN tlmgr option repository http://mirror.ctan.org/systems/texlive/tlnet
RUN tlmgr update --self
RUN tlmgr install reledmac libertine

# Java
RUN apt-get install -y default-jre

# Python and pip
RUN apt-get install -y python3.6
RUN curl https://bootstrap.pypa.io/get-pip.py | python3.6

# App directory and install
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# Copy in the app content
COPY requirements.txt /usr/src/app/
RUN python3.6 -m pip install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

# Create necessary dirs that are excluded via .gitignore
RUN mkdir -p /upload && mkdir -p /static/output

EXPOSE 5000

CMD gunicorn --worker-class eventlet -w 1 -b 0.0.0.0:5000 service:app