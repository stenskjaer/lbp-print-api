FROM python:onbuild

# Latex setup
RUN apt-get update
RUN apt-get install -y texlive-full latexmk

# Java
RUN apt-get update && apt-get install -y default-jre

EXPOSE 5000

CMD python service.py

