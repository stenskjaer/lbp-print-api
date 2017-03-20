FROM python:onbuild

# Latex setup
RUN apt-get update
RUN apt-get install -y xzdec texlive-xetex latexmk
RUN tlmgr init-usertree
RUN tlmgr option repository "ftp://tug.org/historic/systems/texlive/2015/tlnet-final"
RUN tlmgr install reledmac libertine

# Java
RUN apt-get update && apt-get install -y default-jre

EXPOSE 5000

CMD python service.py

