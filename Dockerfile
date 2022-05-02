FROM ubuntu:21.10

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
    libxml2-dev libxslt-dev python3.9 python3-pip 

# texlive install
RUN apt-get install -y xzdec texlive-full latexmk

# texlive update and install reledmac
RUN tlmgr init-usertree
#RUN tlmgr option repository http://mirror.ctan.org/systems/texlive/tlnet

#RUN tlmgr option repository https://mirrors.tuna.tsinghua.edu.cn/CTAN/systems/texlive/tlnet
#RUN tlmgr repository set https://mirrors.tuna.tsinghua.edu.cn/CTAN/systems/texlive/tlnet
RUN tlmgr repository add ftp://tug.org/historic/systems/texlive/2020/tlnet-final
RUN tlmgr repository list
RUN tlmgr repository remove http://mirror.ctan.org/systems/texlive/tlnet
RUN tlmgr option repository ftp://tug.org/historic/systems/texlive/2020/tlnet-final
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

# install saxon
RUN mkdir -p /usr/share/java/saxon
RUN curl -L -o /usr/share/java/saxon/saxon.zip https://downloads.sourceforge.net/project/saxon/Saxon-HE/10/Java/SaxonHE10-8J.zip && \
    unzip /usr/share/java/saxon/saxon.zip -d /usr/share/java/saxon && \
    rm -rf /usr/share/java/saxon/noticies /usr/share/java/saxon/lib \
      /usr/share/java/saxon/saxon10-8-test.jar /usr/share/java/saxon/saxon108-unpack.jar /usr/share/java/saxon/saxon.zip

RUN printf '#!/bin/bash\nexec java  -jar /usr/share/java/saxon/saxon9he.jar "$@"' > /bin/saxon
RUN chmod +x /bin/saxon

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

#CMD gunicorn -w 1 -b 0.0.0.0:5000 app:app
CMD gunicorn --reload -w 1 -b 0.0.0.0:5000 app:app
