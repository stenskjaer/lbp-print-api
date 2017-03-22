**This is not ready for production!**

# Installing

Download the repo:
```
git clone https://github.com/stenskjaer/lbp_print-web-app.git
```

Build the docker image:
```
docker build -t lbp-print .
```

In development and testing, run with debugging: 
```
docker run -p 5000:5000 lbp-print
```

Now the app should be available on [localhost:5000](http://localhost:5000).

# TODO 
## Before production
- [x] Add description of the app and LBP context.
- [ ] User feedback during processing.
- [x] wsgi interface
- [ ] Nginx setup?
- [ ] Proper form input validation.

## Nice to have
- [ ] Tests
- [ ] Resource download cache.

