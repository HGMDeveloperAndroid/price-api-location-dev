# 3b-geo-api
Microservice Rest-Full for get scans for determined coordinates polygon


## Prerequisites
+ [Python 3.6](https://www.python.org/downloads/release/python-360/)
+ [Virtualenv](https://virtualenv.pypa.io/en/latest/)
* [MySql 5.7+](https://dev.mysql.com/downloads/mysql/5.7.html)
* [Flask 1.1.2](https://flask.palletsprojects.com/en/1.1.x/)


## Setup
1. Create virtualenv
```
virtualenv venv
```

2. Activate virtualenv
```
source venv/bin/activate
```

3. Install requirements
```
pip install requirements.txt
```

4. Run API in local
```
flask run
```

5. Visit `http://localhost:5000`

## Environments
ENVIRONMENT | STATIC URL | SSH SERVER
------------ | ------------- | -------------
Local | [http://localhost:5000](http://localhost:5000) | N/a
Development | [https://qnp1e4hkg1.execute-api.us-east-2.amazonaws.com/dev](https://qnp1e4hkg1.execute-api.us-east-2.amazonaws.com/dev) | AWS Lambda
QA | [https://3blocations.bnomio.dev](https://3blocations.bnomio.dev) | EC2 AWS

## Deploy to AWS Lambda

* Deploy to environment
```
zappa deploy <environment>
```

* Update environment
```
zappa update <environment>
```

* Show errors for environment
```
zappa tail <environment>
```

## Other

* Set FLASK_APP to local environment
```
export FLASK_APP=app.run.py
```

* Set FLASK_ENV to local environment
```
export FLASK_ENV=development
```
