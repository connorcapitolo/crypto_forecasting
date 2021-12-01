# Crypto Forecasting App 
Authors: Connor Capitolo, David Assaraf, Tale Lokvenec, Jiahui Tang

## Problem Definition

The current state of the crypto market is extremely volatile. Due to lack of experience and involvement from traditional actors, there is a lack of systematic investment strategies in the crypto environment; therefore, there is an opportunity to extract value from an accurate prediction of the price dynamics of pairs. 

## Objectives

1. Bridging the lack of structure dealing with crypto exchanges in building a scalable and modular database architecture that will gather various features from different exchanges (starting with Binance) for ‘pairs’ (a ‘pair’ refers for instance to the dynamics of the market for BTC vs USDT)

2. Building a predictive ML/DL model using real-time predictions that will enable us to gain insights as to how the market is evolving over time in order to inform trading decision making  


## Prerequisites
### Install Docker 
Install `Docker Desktop`

#### Ensure Docker Memory
- To make sure we can run multiple container go to Docker>Preferences>Resources and in "Memory" make sure you have selected > 4GB
    - If you do not do this, will get a `FATAL ERROR: Ineffective mark-compacts near heap limit Allocation failed - JavaScript heap out of memory` when trying to run Frontend

### Install VSCode  
Follow the [instructions](https://code.visualstudio.com/download) for your operating system.  
If you already have a preferred text editor, skip this step.  

Project Organization
------------
      .
      ├── LICENSE
      ├── Makefile
      ├── README.md
      ├── models
      ├── notebooks
      ├── references
      ├── requirements.txt
      ├── setup.py
      ├── src
      │   ├── __init__.py
      │   └── database-server
      │   └── common
      |   └── worker-service
      │   └── api-service
      │   └── frontend-react
      │   └── deployment
      ├── submissions
      │   ├── milestone1_crypto_forecasting.pdf
      │   ├── milestone2_crypto_forecasting.pdf
      │   ├── milestone3_crypto_forecasting.pdf
      │   └── milestone4_crypto_forecasting.pdf
      ├── misc
          ├── milestone2_src
      └── test_project.py

--------

## Description of Various Components of Crypto Forecasting App

### database-server
- used in development mode (with an equivalent for production) that stores the PostgreSQL database with the three tables: *symbols*, *price_history*, *top_of_book*
    - *symbols*: contains information about the pairs. This table basically contains the logs for our work: the pais that are being queried, their unique identifier, and the last timestamp at which we have some data for this pair. This last field allows us to fetch the missing data when the worker goes down
    - *price_history*: all historical Candles for each pair
    - *top_of_book*: contains the best bid/ask prices for every pair at every minute

### common
- dataaccess: scripts related to querying the three tables (*symbols*, *price_history*, *top_of_book*) in the Postgres database
- datacollector: scripts related to querying data (both historical and live stream) from the Binance API to be placed in the Postgres database

### worker-service
- makes sure that we have the most up-to-date data in the PostgreSQL database; leverages multiprocessing in order to be able to fetch historical data for a new symbol while streaming online data at the same time
    - when receiving a new pair (e.g. BNBUSDT), it will call the Binance API to get all historical data up to the present moment (historical fetching)
    - for the pairs with complete historical data, fetch two types of online data: candle and top of book

### api-service
- API allows for getting the data from the database in the backend to the frontend based on user input
    -  performs the querying of the PostgreSQL database to obtain historical minute-by-minute data
    -  obtains the model from a GCS bucket (*to do*) for prediction
    -  adds new pairs (e.g. BNBBTC) to the backend *symbols* table based on a user request

### frontend-react
- REACT framework so that a user can easily select the pair (e.g. BNBBTC) they want to view, and get a graph that provides real-time minute-by-minute predictions

### deployment
- yml scripts for automatically starting up a VM instance on GCP, uploading containers to GRC, adding the containers from GCR to the VM, and running the crypto forecasting app on the GCP VM (in the cloud)
    - contains both scripts for both Ansible and Kubernetes

## Example Development Workflow

**When running on your local computer for development, always make sure to run database-server first as api-service and worker-service rely on it!**

First step from the top-level directory is to enter the source code folder (everything will be based on being inside this folder)
- `cd src`

### Run Database Server
-  `cd database-server`
- Start docker shell `sh ./docker-shell.sh`
- Check migration status: `dbmate status` (if this doesn't exist, nothing should show here or it should throw an error such as `Error: pq: database "crypbrosdb" does not exist`)
    - if the database tables are set up previously, you can do `dbmate drop` to start from scratch
- Set up the database tables: `dbmate up`
- To enter Postgres database: `psql postgres://cryp:bros@crypbrosdb-server:5436/crypbrosdb`
    - this may take a minute to work; you may get an error such as `Error: dial tcp 172.18.0.2:5436: connect: connection refused` at first
- We have three tables: *symbols*, *price_history*, *top_of_book*
    - Can view *symbols* table with`select * from symbols;` (don't forget semicolon at the end). Interesting fields to see there: updated_at, dynamic attribute 
    - Can view *price_history* table with `select * from price_history where symbol_id=1 LIMIT 5;`
    - Can view *top_of_book* table with `select * from price_history where symbol_id=1 LIMIT 5;`
        - none of these should contain anything at this point


### Create a new migration script
dbmate new base_tables

#### Running Migrations ([dbmate commands](https://github.com/amacneil/dbmate))
```
dbmate --help    # print usage help
dbmate new       # generate a new migration file
dbmate up        # create the database (if it does not already exist) and run any pending migrations
dbmate create    # create the database
dbmate drop      # drop the database
dbmate migrate   # run any pending migrations
dbmate rollback  # roll back the most recent migration
dbmate down      # alias for rollback
dbmate status    # show the status of all migrations (supports --exit-code and --quiet)
dbmate dump      # write the database schema.sql file
dbmate wait      # wait for the database server to become available
```

### Run API Service (can be started up simultaneously as Worker in a new Terminal window)
- `cd api-service`
- Start docker shell `sh ./docker-shell.sh`
- To run development api service run `uvicorn_server` from the docker shell
- View the API service by going to `http://0.0.0.0:9600/`
- View the REST API options (GET/POST requests) to play around with at `http://0.0.0.0:9600/docs`
- After spinning up the worker, you will be able to add new symbols through the RESTAPI


### Run Worker Service (can be started up simultaneously as API in a new Terminal window)
- `cd worker-service`
- Start docker shell `sh ./docker-shell.sh`
- To run development worker service run `worker` from the docker shell

You should now see something similar to this in the Terminal (since we add by defaults the symbols *BNBBTC, BTCUSDT*) as worker is trying to pull the historical data from the Binance API before adding it to the live stream

```
Starting Worker Service with NUM_PROCESSES: 4                                                                                       
Running                                                                                                                                                                                              Symbols: [{'id': 1, 'name': 'BNBBTC', 'status': 0, 'timestamp': None}]                                                                       
Fetching history for {'id': 1, 'name': 'BNBBTC', 'status': 0, 'timestamp': None, 'current_status': 'created'}                                
status = :status, updated_at = EXTRACT(EPOCH FROM clock_timestamp()) * 1000                                                                  
fetch_price_history                                                                                                                          
fetch_price_history_async                                                                                                                    
Live stream: {}                                                                                                                              
History stream: {1: {'id': 1, 'name': 'BNBBTC', 'status': 1, 'timestamp': None, 'current_status': 'running'}}                                
Symbols: {1: {'id': 1, 'name': 'BNBBTC', 'status': 1, 'timestamp': None, 'current_status': 'running'}}                                       
timestamp_end: 1500004800000                                                                                                                 
==============================================                                                                                               
Fetch timestamps: BNBBTC 1500004800000 1500604800000                                                                                         
==============================================                                                                                               
Querying candles data from _____ until present time, with a frequency update of 1m                                                           
Fetched 10001 lines of data in 7.788289785385132 seconds
len(bars): 10001
Symbols: [{'id': 1, 'name': 'BNBBTC', 'status': 1, 'timestamp': None}] 
Live stream: {}
History stream: {1: {'id': 1, 'name': 'BNBBTC', 'status': 1, 'timestamp': None, 'current_status': 'running'}}
Symbols: {1: {'id': 1, 'name': 'BNBBTC', 'status': 1, 'timestamp': None, 'current_status': 'running'}}
timestamp = :timestamp, updated_at = 1500604800000

```

### Run Frontend-React
- `cd frontend-react`
- Start docker shell `sh ./docker-shell.sh`
- Run the command `yarn install`
- After installation (this may take some time), run the command `yarn start`
- On the browser, go to `http://localhost:3000/`


### At this point, you should see our Crypto Forecasting Web App!

## Re-Deploying App On GCP with Ansible 

*For deploying from scratch to GCP with Ansible, please follow the [detailed step-by-step instructions outlined here](https://github.com/dlops-io/mushroom-app/tree/06-deployment)*
- **you will need to perform this originally in order to obtain the *secrets* folder**

*Notes that when re-deploying, it should take around 10-15 minutes to get everything up and running again; when deploying for the first time, it takes about 1.5-2 hours since it's over an hour for the containers to be built and pushed to GCR*

- Kill and remove running docker containers on VM following this [article](https://typeofnan.dev/how-to-stop-all-docker-containers/): `sudo docker kill $(sudo docker ps -q)`
- Remove the network and images from the VM: `sudo docker system prune -a`
- Rebuild and redeploy the images
    - From *deployment* docker shell, run 
    ```
    ansible-playbook deploy-docker-images.yml -i inventory.yml
    ```
- Update the *deployment/.docker-tag* from the *stdout_lines* of the *Print tag* Ansible task
- Deploy the Docker containers on the VM
  ```
  ansible-playbook deploy-setup-containers.yml -i inventory.yml
  ```
    - don't need to create the compute instance or provision the server (adding all the necessary files like Docker, etc.) since this has been done previously
- Check that there are four images running in the VM instance by SSHing in and running from its Terminal `sudo docker image ls`

![Screen Shot 2021-11-28 at 8 21 47 PM](https://user-images.githubusercontent.com/37121874/143795092-9937c2d5-bdd2-45be-94e8-143d4605f6f0.png)

- Check that there are four containers running in the VM instance by SSHing in and running from its Terminal `sudo docker container ls`

![Screen Shot 2021-11-28 at 8 23 52 PM](https://user-images.githubusercontent.com/37121874/143795168-2e26e05b-b276-4434-b9a9-cba5159961fa.png)


- Look at the logs of api-service by running `sudo docker container logs api-service -f` in VM Terminal to confirm they look similar to this
    - Should look like this:
    ```
    Container is running!!!
    The following commands are available:
        uvicorn_server
            Run the Uvicorn Server
    2021-11-22 16:44:27.464495: W tensorflow/stream_executor/platform/default/dso_loader.cc:64] Could not load dynamic library 'libcudart.so.11.0'; dlerror: libcudart.so.11.0: cannot open 
    shared object file: No such file or directory
    2021-11-22 16:44:27.464538: I tensorflow/stream_executor/cuda/cudart_stub.cc:29] Ignore above cudart dlerror if you do not have a GPU set up on your machine.
    INFO:     Started server process [8]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    INFO:     Uvicorn running on http://0.0.0.0:9000 (Press CTRL+C to quit)
    ```
    - `ctrl+c` out of the log
- Look at the logs of worker-service by running `sudo docker container logs worker-service -f` in VM Terminal to confirm they look similar to this
    - Should look like this:
    ```
    Container is running!!!
    The following commands are available:
        worker
            Run the Worker Service
    Starting Worker Service with NUM_PROCESSES: 1
    Running
    Live stream: {}
    History stream: {}
    Symbols: {}
    fetch_online_data started
    Resetting
    Startup
    Working with []
    hh
    hey
    hey
    hey2
    History stream: {}
    Symbols: {}
    History stream: {}
    Symbols: {}
    History stream: {}
    Symbols: {}
    History stream: {}
    Symbols: {}
    History stream: {}
    Symbols: {}
    History stream: {}
    Symbols: {}
    History stream: {}
    Symbols: {}
    History stream: {}
    Symbols: {}
    History stream: {}
    Symbols: {}
    History stream: {}
    Symbols: {}
    ```
    - `ctrl+c` out of the log
- Going back to the *deployment* Docker shell on local machine, set up the web server on the compute instance: 
   ```
   ansible-playbook deploy-setup-webserver.yml -i inventory.yml
   ```
   - The output should look similar to this:

   <img width="1419" alt="Screen Shot 2021-11-28 at 8 27 18 PM" src="https://user-images.githubusercontent.com/37121874/143795325-c5dc7c14-4f50-4a45-b938-9774f0313077.png">


   
- Copy the External IP (either from Terminal or from GCP Compute Enginer page), and **paste** it into the browser to view the web app!
    - For some reason, doesn't work to just click on the External IP from the GCP Compute Engine page

![Screen Shot 2021-11-30 at 12 15 38 PM](https://user-images.githubusercontent.com/37121874/144095334-048a6b3b-3872-4b73-858f-5b2776f91a22.png)

## Step-by-step Guide for Deployment of Kubernetes Cluster

These instructions directly follow the detailed, step-by-step guidelines from [Deploy Mushroom App to K8s Cluster](https://github.com/dlops-io/mushroom-app/tree/08-mushroom-app-k8s-deployment)
- **you must ensure that you have the *secrets* folder stored locally (should not be pushed to Github), which can be found by following [this guide](https://github.com/dlops-io/mushroom-app/tree/06-deployment)**

### API's to enable in GCP for Project
Search for each of these in the GCP search bar and click *enable* to utilize these APIs:

- Compute Engine API
- Service Usage API
- Cloud Resource Manager API
- Google Container Registry API
- Kubernetes Engine API

### Start Deployment Docker Container

From the top-level directory in your command line: 
- `cd src/deployment`
- `sh docker-shell.sh` (must be using a non-Windows device)
- Check versions of tools: `gcloud --version` `kubectl version --client`
- Check if make sure you are authenticated to GCP: `gcloud auth list`

### Build and Push Docker Containers to GCR
This step is only required if you have NOT already done this

```
ansible-playbook deploy-docker-images.yml -i inventory.yml
```

### Deploy to Kubernetes Cluster

We will use Ansible to create and deploy the crypto forecasting app into a Kubernetes Cluster; this step should take around 5-10 minutes to complete

```
ansible-playbook deploy-k8s-cluster.yml -i inventory.yml --extra-vars cluster_state=present
```

Example of the start of the output in the command line:

<img width="1415" alt="Screen Shot 2021-11-30 at 11 41 00 AM" src="https://user-images.githubusercontent.com/37121874/144089611-c4d028cd-a50f-4f9b-a428-3dbb6890ac94.png">

### View the App!

- Copy the *nginx_ingress_ip* from *Create Cluster* task
- Go to `http://<YOUR INGRESS IP>.sslip.io`

Output:


![Screen Shot 2021-11-30 at 11 45 16 AM](https://user-images.githubusercontent.com/37121874/144090246-8a70d009-2ba2-4778-bddf-26c35d7f396d.png)
