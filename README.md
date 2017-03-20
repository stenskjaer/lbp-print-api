# Installing

Build the docker image:
```
docker build -t lbp-print .
```

In development and testing, run with debugging: 
```
docker run -p 5000:5000 -e FLASK_APP=service.py -e FLASK_DEBUG=True lbp-print
```

**There is not yet a implementation for production!**