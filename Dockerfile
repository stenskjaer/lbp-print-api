FROM ubuntu:19.10

# set environment encoding and some base utils
ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

# set environment encoding and system dependencies
RUN apt-get update && apt-get install -y \
    # system utils
    wget curl git \
    # tectonic deps
    libfontconfig1-dev libgraphite2-dev libharfbuzz-dev libicu-dev libssl-dev zlib1g-dev \
    # python and libxml
    libxml2-dev libxslt-dev python3.7-dev python3-pip 

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


# # Install rust
# RUN curl -f -L https://static.rust-lang.org/rustup.sh -O \
#     && sh rustup.sh -y
# # Install tectonic
# RUN $HOME/.cargo/bin/cargo install tectonic

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
