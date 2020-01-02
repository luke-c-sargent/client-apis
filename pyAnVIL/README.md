

# pyAnVIL: terra + gen3

A python client integration of gen3 and terra
* gen3==2.0.1
* firecloud==0.16.24

## Use cases

As an AnVIL data analyst, I need to retrieve the:
* namespace
* workspaces
* workspace schema
* workspace entities
from terra

> As an AnVIL informaticist, in order to create cross project cohorts, I would like to query across those projects


> As an AnVIL informaticist, having created a cross project cohort, in order to derive novel results, I would like to run a workflow using files from that cross project cohort

> As an AnVIL data analyst, I need those projects mapped to the AnVIL schema (Note, the schema is a future deliverable)

## Setup

After cloning this repository

```
$ python3 -m anvil.show_projects
WARNING:root:Unable to determine/refresh application credentials
Go to the following link in your browser:

    https://accounts.google.com/o/oauth2/auth?....


Enter verification code:

Credentials saved to file: [/home/xxxx/.config/gcloud/application_default_credentials.json]

```

# Setup


* set up virtual env

```
export VIRTUALENVWRAPPER_PYTHON=/usr/local/bin/python3
export WORKON_HOME=$HOME/.virtualenvs
export PROJECT_HOME=$HOME/client-apis/pyAnVIL
source ~/bin/virtualenvwrapper.sh

# only once
mkvirtualenv pyAnVIL --python=$VIRTUALENVWRAPPER_PYTHON

workon pyAnVIL
```



## Authorization Setup

* reset google credentials if necessary, ensure access to google

```
rm $HOME/.config/gcloud/application_default_credentials.json
gcloud auth login
```

* terra Setup
  * account setup:
    * using same gmail account, login to https://bvdp-saturn-dev.appspot.com/#profile
    * under "IDENTITY & EXTERNAL SERVERS", login to gen3 services
  * retrieve default credentials by executing terra and refreshing default credentials:
    ```
    python3  tests/integration/setup_terra_test_credentials.py
    # follow prompt and paste in verification code
    ```
  * api endpoint
    * configure the api endpoint
    ```
    cat ~/.fissconfig
    [DEFAULT]
    root_url=https://firecloud-orchestration.dsde-dev.broadinstitute.org/
    debug=True
    ```
    * verify
    ```
    fissfc config
    >>> ....
    root_url	https://firecloud-orchestration.dsde-dev.broadinstitute.org/
    ```

## Test authorization

    ```
    python3 -m pytest --user_email <GMAIL ACCOUNT>  --log-level DEBUG  --gen3_endpoint <GEN3_ENDPOINT>  tests/integration/test_auth.py
    ```
