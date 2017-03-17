FROM python:onbuild


ENV FLASK_APP=service.py
ENV FLASK_DEBUG=True

EXPOSE 5000

CMD python service.py

