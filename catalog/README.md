# Item Catalog Web App Project

BY Ponnam Sai Sree

This web app is a project for the Udacity [FSND Course](https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004).

## Project overview
This project shows the webapp it allows only user who created the data to edit/delete and add details.If a new user logged in he cannot edit/delete/add other users data but he can view.A new user can add a new branch and he can enter data there his data cannot be edit/delete/add data by other users.

## Skills Required
1. Python
2. HTML
3. CSS
4. OAuth
5. Flask Framework
6. DataBaseModel

## Files Contain folder
This project contains the files:
main.py
setup_file.py
data_init.py
images folder contains output images
templates folder contains html files
static folder contains css files
client_secrets.json file.

## How to run ItemCatalog Project

Install Vagrant & VirtualBox
- Create Vagrant file `vagrant init ubuntu/xenial64`
- Connect to VirtualMachine `vagrant up`
- Login to VirtualMachine `vagrant ssh`
- Exit from current directory  `cd ..`
- Again exit directory `cd ..`
- Change directory path `cd vagrant`
- Change Project directory `cd catalog`
- To see list of files `ls -l`

## In This Project Main files 

- In this project contains `main.py` contains routes and json endpoints.
- `setup_file.py` contains the database models and tablenames it creates a database file with table.
- `data_init.py` contains the sample data and insert into the database.

### we need to install some modules and python

- Update `sudo apt-get update`
- Install Python `sudo apt-get install python`
- Install pip `sudo apt-get install python-pip`
- Import module `pip install flask`
- Import module`pip install sqlalchemy`
- Import module `pip install oauth2client`
- Import module `pip install httplib2`
- After installing modules we have to run `python setup_file.py` to create database models 
- Next run `python data_init.py` to insert sample data.
- Next run `python main.py` to execute project

							
##Creating API and OAuth client-id 
we have to create a new API and client-id.
To create client id : (https://console.developers.google.com)
- goto to credentials
- create credentials
- Click API KEY
- to create client id we have to create oAuth constent screen
- create OAuth client ID
- Application type(web application)
- Enter name(ApssdcSite)
- Authorized JavaScript origins (http://localhost:8000)
- Authorized redirect URIs = (http://localhost:8000/login) && (http://localhost:8000/gconnect)
- create
- download client_data.json and place it in the folder 


## JSON Endpoints

The following are to check JSON endpoints:

allBanksJSON: `/ApssdcSite/JSON`
    - Displays the whole  and team details

categoriesJSON: '/ApssdcSite/apssdc_Name/JSON'
    - Displays the apssdc names and its id
	
detailsJSON:
'/ApssdcSite/apssdc/JSON'

	- It displays all team details in banks

categorydetailsJSON:
 '/ApssdcSite/<path:apssdcname>/apssdc/JSON'
 
    - It displays the details in a apssdc

DetailsJSON:
'/ApssdcSite/<path:apssdcname>/<path:teamdetails_name>/JSON'

    - It displays the details that the apssdc name and teamdetails_name matches


