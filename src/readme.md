# Guidelines Demo

This web application can show off the coolness of the TMR and TMR4I ontologies developed by Veruska Zamborlini in detecting interactions between the recommendations of medical guidelines

## Setup

* Make sure you have `pip` and `virtualenv` installed (`easy_install pip`, `pip install virtualenv`)
* Go to the directory in which you cloned this Git repository, and install a virtual environment: `virtualenv .`
* Activate the virtual environment: `source bin/activate`
* Install the required packages: `pip install -r requirements.txt`
* Make sure you have a properly installed Stardog server running, with **security disabled** (`stardog-admin server start --disable-security`)
* Go to the `src` directory, and run `create-stardog.sh` and then `reset-stardog.sh`
* Inside the `src` directory, run `python run.py`
* Go to `http://localhost:5000` and have fun!