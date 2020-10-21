# Field Staff Data Repository User Interface

## Prerequisites

Ensure that both redis and postgres to be installed locally. 

The FSDR-Service needs to be running locally before running the UI. You also need to insert data into the FSDR\_Service database. Once added, you will also need to add a username and password into the 'user_authentication' table in order to access the UI.

## Running

1. Clone the master repository to local then open command/terminal and change the directory to where the project
   folder is located
2. Run `docker-compose build` and then `docker-compose up`
3. Run `pipenv install`
4. Change the directory to the `../scripts` directory and then run `bash load_templates.sh`. This will install
   all the project templates locally. Note: this step maybe optional
5. Change the directory back to the root project folder and run `python3 run.py`. The UI should now be running

## Copyright
Copyright (C) 2019 Crown Copyright (Office for National Statistics)
