FROM ubuntu:19.04

# set environment encoding and system dependencies
RUN apt-get update && apt-get install -y \
    # system utils
    wget curl git \
    # tectonic deps
    libfontconfig1-dev libgraphite2-dev libharfbuzz-dev libicu-dev libssl-dev zlib1g-dev \
    # python and libxml
    libxml2-dev libxslt-dev python3.7-dev python3-pip 

# Install rust
RUN curl -f -L https://static.rust-lang.org/rustup.sh -O \
    && sh rustup.sh -y
# Install tectonic
RUN $HOME/.cargo/bin/cargo install tectonic

# Java
RUN apt-get install -y default-jre

# App directory and install
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# Create necessary dirs that are excluded via .gitignore
RUN mkdir upload static static/output logs cache

# Copy in the app content
COPY requirements.txt /usr/src/app/
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

COPY texmf/ /root/texmf

EXPOSE 80

CMD gunicorn -w 1 -b 0.0.0.0:5000 app:app
