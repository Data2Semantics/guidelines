# Guidelines Demo

This web application can show off the coolness of the TMR and TMR4I ontologies developed by Veruska Zamborlini in detecting interactions between the recommendations of medical guidelines.

This repository also contains the `metis` application that runs with Swish. You can find a separate readme file in that directory. 

## Setup (using Docker)

* Make sure you have docker installed on your system (<http://docker.com>)
* Open up a terminal window and clone or download this repository to a location of your choice:

```
git clone https://github.com/Data2Semantics/guidelines.git
```
* Change into the `guidelines` directory
* Download the latest version of Stardog from <https://stardog.com>
* Copy the zipfile for the latest version of Stardog into this directory (e.g. `stardog-5.0-beta.zip`).
* Also copy the `stardog-license-key.bin` file into this directory
* From the command line run `docker-compose build` to create the Docker images

### Starting (using Docker)

* Change into the `guidelines` directory and run `docker-compose up`
* Go to `http://localhost:5000` and have fun!

## Setup (from source)

* Make sure you have `pip` and `virtualenv` installed (`easy_install pip`, `pip install virtualenv`)
* Go to the directory in which you cloned this Git repository, and install a virtual environment: `virtualenv .`
* Activate the virtual environment: `source bin/activate`
* Install the required packages: `pip install -r requirements.txt`
* Make sure you have a properly installed Stardog server running, with **security disabled** (`stardog-admin server start --disable-security`)
* Go to the `src` directory, and run `create-stardog.sh` and then `reset-stardog.sh`

### Starting (from source)

* Inside the `src` directory, run `python run.py`
* Go to `http://localhost:5000` and have fun!
