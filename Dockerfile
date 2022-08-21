FROM ubuntu:22.04

# set environment encoding and some base utils
ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

# set environment encoding and system dependencies
RUN apt update
RUN apt upgrade -y
# system utils
RUN apt install -y wget curl git
# tectonic deps
RUN apt install -y libfontconfig1-dev libgraphite2-dev libharfbuzz-dev libicu-dev libssl-dev zlib1g-dev
# Python
RUN apt install -y libxml2-dev libxslt-dev python3 python3-pip

RUN cd /tmp
RUN wget https://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz
RUN zcat install-tl-unx.tar.gz | tar xf -
#RUN cd install-tl-*
#RUN perl ./install-tl --no-interaction --scheme=small
RUN perl ./install-tl-*/install-tl --no-interaction --scheme=small

#ENV PATH="$PATH:/usr/local/texlive/2022/bin/aarch64-linux"
ENV PATH="$PATH:/usr/local/texlive/2022/bin/x86_64-linux"
#RUN echo "PATH=$PATH:/usr/local/texlive/2022/bin/aarch64-linux">>/etc/environment

RUN tlmgr install latexmk imakeidx reledmac babel-latin xargs bigfoot xstring titlesec csquotes gitinfo2 fontaxes mweights libertine draftwatermark

# # Install rust
# RUN curl -f -L https://static.rust-lang.org/rustup.sh -O \
#     && sh rustup.sh -y
# # Install tectonic
# RUN $HOME/.cargo/bin/cargo install tectonic

# Java
RUN apt install -y default-jre
# zip unzip
RUN apt install zip unzip

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
## TODO remove --reload flag in production
#CMD gunicorn --reload -w 1 -b 0.0.0.0:5000 app:app
CMD gunicorn -w 1 -b 0.0.0.0:5000 app:app
