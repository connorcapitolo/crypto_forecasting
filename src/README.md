# Crypto Forecasting App 
Authors: Connor Capitolo, David Assaraf, Tale Lokvenec, Jiahui Tang

For a view of the GitHub repo used for development, [see here](https://github.com/AC215/cypbros-app). This provides a full commit history as well as the work of each team member.

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
- makes sure that it is able to re-spin new processes for online fetching when Binance kills the live process because of too many API calls.
- write data to the postgres database 

### api-service
- API allows for getting the data from the database in the backend to the frontend based on user input
    -  performs the querying of the PostgreSQL database to obtain historical minute-by-minute data
    -  obtains the model from a GCS bucket for prediction
    -  adds new pairs (e.g. BNBBTC) to the backend *symbols* table based on a user request

### frontend-react
- REACT framework so that a user can easily select the pair (e.g. BNBBTC) they want to view, and get a graph that provides real-time minute-by-minute predictions

### deployment
- yml scripts for automatically starting up a VM instance on GCP, uploading containers to GRC, adding the containers from GCR to the VM, and running the crypto forecasting app on the GCP VM (in the cloud)
    - contains both scripts for both Ansible and Kubernetes

### secrets (not on GitHub)
- this should only be stored locally as this is private to your particular instance and should not be shared with others
- allows for connecting to GCS (Google Container Storage), GCP (Google Cloud Provider), and GCR (Google Cloud Registry) for deployment




## Step-by-step Guide for Deployment of Crypto Forecasting App

**These instructions directly follow the detailed, step-by-step guidelines from [Mushroom App - Deployment to GCP](https://github.com/dlops-io/mushroom-app/tree/06-deployment)**

**These instructions assume you are working from a non-Windows machine**

### Clone Repository

From your command line

```
git clone https://github.com/AC215/cypbros-app.git
cd cypbros-app
```

### Enabling APIs and Creating *Secrets* Folder

**the *secrets* folder should only be stored locally as it provides information to access your GCP account**

From the command line at the top-level directory of the package

```
mkdir secrets
```

### Saving `deployment.json`, `gcp-service.json`, and `bucket-reader.json` to *Secrets* folder

1. Search for each of these in the GCP search bar and click *enable* to utilize these APIs needed for deployment:
    - Compute Engine API
    - Service Usage API
    - Cloud Resource Manager API
    - Google Container Registry API
    - Kubernetes Engine API

2. Go to GCP Console, search for "Service Accounts" from the top search box. or go to: "IAM & Admins" > "Service accounts" from the top-left menu and click  on *Create Service Account* 
    - name it "deployment" and then click done


![Screen Shot 2021-12-09 at 7 15 53 PM](https://user-images.githubusercontent.com/37121874/145501890-62fc398f-6f90-435d-b92a-0053f42765c2.png)


3. On the right hand side under the "Actions" column click the vertical ... and select "Create key"; a prompt for "Create private key for "deployment"" will appear

4. select "JSON" and click create; this will download a Private key json file to your computer
- rename the json key file to **deployment.json** and copy this json file into the *secrets* folder you just created

5. Perform the same steps again from your Service Account for a **gcp-service.json**
    - the only difference is this time when you are creating the service account, under Step 2 of *Grant this service account access to project (optional)*, select the role "Storage Object Viewer"

![Screen Shot 2021-12-09 at 7 21 38 PM](https://user-images.githubusercontent.com/37121874/145501943-593bb24c-a022-4ae6-af9d-a0a5eda0b679.png)


6. Perform the same steps again from your Service Account for a **bucket-reader.json**
    - the only difference is this time when you are creating the service account, under Step 2 of *Grant this service account access to project (optional)*, select the role "Storage Object Viewer"



### Start Deployment Docker Container

From the command line at the top-level directory of the package

```
cd src/deployment
sh docker-shell.sh
```

Once the container has spun up

- Check versions of tools: 

```
gcloud --version 
kubectl version --client
```
- Check if make sure you are authenticated to GCP: 

```
gcloud auth list
```

<img width="617" alt="Screen Shot 2021-12-10 at 3 00 06 PM" src="https://user-images.githubusercontent.com/37121874/145634338-b0cb6180-baa3-4054-9339-e13fd909d089.png">


### SSH Setup

Configure the OS Login for Service Account

```
gcloud compute project-info add-metadata --project crypto-forecasting-app --metadata enable-oslogin=TRUE
```

Create SSH key for service account

```
cd /secrets
ssh-keygen -f ssh-key-deployment
cd /app
```

Provide public SSH keys for VM instances

```
gcloud compute os-login ssh-keys add --key-file=/secrets/ssh-key-deployment.pub
```

From the output of the above command keep note of the username. Here is an example output

```
- accountId: crypto-forecasting
    gid: '3906553998'
    homeDirectory: /home/sa_100110341521630214262
    name: users/deployment@ac215-project.iam.gserviceaccount.com/projects/ac215-project
    operatingSystemType: LINUX
    primary: true
    uid: '3906553998'
    username: sa_100110341521630214262
```

Take the *username* from your output, and replace it with the *ansible_user* variable in the `inventory.yml` file

<img width="380" alt="Screen Shot 2021-12-10 at 3 02 28 PM" src="https://user-images.githubusercontent.com/37121874/145634554-5c734ae7-089c-4406-a0de-3f7851dfb335.png">


### Build and Push Docker Containers to GCR


```
ansible-playbook deploy-docker-images.yml -i inventory.yml
```

Update the `.docker-tag` from the *stdout_lines* of the *Print tag* Ansible task
- this will be used for when deploying your Docker containers from GCR to your VM

<img width="336" alt="Screen Shot 2021-12-10 at 3 04 17 PM" src="https://user-images.githubusercontent.com/37121874/145634725-852a1767-897c-4905-8fd6-39b81a815377.png">



### Create the VM on GCP

```
ansible-playbook deploy-create-instance.yml -i inventory.yml --extra-vars cluster_state=present
```

Once the command runs successfully

- Go to GCP and check that your VM instance is up on the Compute Engine --> VM Instances
- Get the IP address of the compute instance from GCP Console and update the *hosts* in `inventory.yml` file

<img width="236" alt="Screen Shot 2021-12-10 at 3 06 55 PM" src="https://user-images.githubusercontent.com/37121874/145635007-b9ea384e-79c7-4817-bd00-e8ba30d0c43c.png">


- Check that your persistent disk is on GCP through Compute Engine --> Disks

### Add in all the necessary packages to the newly-created VM

```
ansible-playbook deploy-provision-instance.yml -i inventory.yml
```

Once the command runs successfully, locate your VM instance on GCP and click on the `SSH` button on the right-hand side

- this should open a new browser window that puts you at your VM's terminal
run the command `sudo docker --version` to see the Docker version on your VM
- other downloaded packages are pip, setuptools, and more


### Deploy the Docker containers on the VM


```
ansible-playbook deploy-setup-containers.yml -i inventory.yml
```


Check that there are four images running in the VM instance by SSHing in and running from its Terminal `sudo docker image ls`

![Screen Shot 2021-11-28 at 8 21 47 PM](https://user-images.githubusercontent.com/37121874/143795092-9937c2d5-bdd2-45be-94e8-143d4605f6f0.png)

Check that there are four containers running in the VM instance by SSHing in and running from its Terminal `sudo docker container ls`

![Screen Shot 2021-11-28 at 8 23 52 PM](https://user-images.githubusercontent.com/37121874/143795168-2e26e05b-b276-4434-b9a9-cba5159961fa.png)


Look at the logs of api-service by running `sudo docker container logs api-service -f` in VM Terminal to confirm they look similar to this

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

Look at the logs of worker-service by running `sudo docker container logs worker-service -f` in VM Terminal to confirm they look similar to this

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

- `ctrl+c` out of the log on your VM

Can enter into container utilizing interactive terminal like this

```
sudo docker exec -it api-service /bin/bash
```

View the Postgres Database

```
sudo docker run --rm -it -v /conf/db:/db -e DATABASE_URL=postgres://cryp:bros@postgres:5432/crypbrosdb?sslmode=disable --network crypbros --entrypoint /bin/sh amacneil/dbmate
psql postgres://cryp:bros@postgres:5432/crypbrosdb
```

<img width="1189" alt="Screen Shot 2021-12-12 at 11 05 05 PM" src="https://user-images.githubusercontent.com/37121874/145750720-7e1f0638-a6c4-4e65-a7fa-73015d15dbfc.png">


  
### Setup Webserver on Compute Instance

From your command line on your local machine inside the *deployment* container

```
ansible-playbook deploy-setup-webserver.yml -i inventory.yml
```

   
Copy the External IP (either from Terminal or from GCP Compute Enginer page), and **paste** it into the browser to view the web app!
- For some reason, doesn't work to just click on the External IP from the GCP Compute Engine page

The start-up screen should look like this

![Screen Shot 2021-12-13 at 11 36 17 AM](https://user-images.githubusercontent.com/37121874/145851940-50eb1541-cc96-4bfc-bcd2-e5706a611d1f.png)



**Please note that it will take a couple hours after start-up for you to start properly using the web app. This is because the backend queries Binance to extra all previous history for these particular symbols.**

### Delete Compute Instance

```
ansible-playbook deploy-create-instance.yml -i inventory.yml --extra-vars cluster_state=absent
```

**Please note that for the current setup, this will delete the VM but NOT the persistent disk. In order to do that from GCP Compute Engine go to *Disks* on the left-hand side (under *Storage* section), find your particular persistent disk, and subsequently delete it.**


## Step-by-Step Guide for Deployment of Crypto Forecasting App with Kubernetes and CloudSQL

**The assumption is you have previously followed the steps for deployment specified above as a number of these steps depend on this set-up.**

### Enable GCP APIs

Search for each of these in the GCP search bar and click *enable* to utilize these APIs needed for deployment:
- Google Cloud SQL Admin API
- Service Networking API
    
### Update *deployment* Service Account

Search for IAM in the GCP search bar, and find where you previously created *deployment* service account. Click on *Add Another Role* and enable **Cloud SQL Admin.** 

<img width="1241" alt="Screen Shot 2021-12-12 at 10 42 16 PM" src="https://user-images.githubusercontent.com/37121874/145748921-46f364f3-d7f8-409c-a8f1-7308e56770c9.png">


### Start Deployment Docker Container

From the command line at the top-level directory of the package

```
cd src/deployment
sh docker-shell.sh
```

### Check your SQL Databases Running

```
gcloud sql instances list
```

If you have not used CloudSQL before or do not have any databases previously running, you should see `Listed 0 items.`

### Create CloudSQL Database

```
gcloud sql instances create crypbros-db-01 --database-version=POSTGRES_13 --cpu=2 --memory=7680MB --region=us-central
```

Example output

<img width="813" alt="Screen Shot 2021-12-13 at 12 10 39 PM" src="https://user-images.githubusercontent.com/37121874/145857147-b895f825-6f9c-4c7a-908e-6b44251d0d5c.png">


### Set Password to Connect From Container to CloudSQL

```
gcloud sql users set-password postgres --instance=crypbros-db-01 --password=welcome123
```
### Manually Enable Service Networking API

Search for SQL in the GCP Search bar, and select the instance you just created

Click on *Connections* on the left-hand side bar, select **Private IP**, *default* network, and then specify *Use an automatically allocated IP range* if it is an option
- this command will take a couple minutes to complete

<img width="1123" alt="Screen Shot 2021-12-12 at 10 52 21 PM" src="https://user-images.githubusercontent.com/37121874/145749707-e83c5b7d-98bf-429a-8a65-9a13a1f4c90f.png">

You can check that the above command worked by running `gcloud beta sql instances patch crypbros-db-01 --project=crypto-forecasting-app --network=projects/crypto-forecasting-app/global/networks/default --no-assign-i`

When running `gcloud sql instances list`, you should now see that *PRIVATE_ADDRESS* is specified instead of *PRIMARY_ADDRESS*

<img width="799" alt="Screen Shot 2021-12-13 at 12 24 09 PM" src="https://user-images.githubusercontent.com/37121874/145859189-27efa23e-1191-43af-95c3-63c79d7b5ada.png">


### Update `deploy-setup-cloud-sql.yml` and `deploy-k8s-cluster.yml` with Private IP

In **Run DB migrations using dbmate** task of `deploy-setup-cloud-sql.yml`, update the IP after *welcome123@*

![Screen Shot 2021-12-13 at 12 23 32 PM](https://user-images.githubusercontent.com/37121874/145859105-3b67e2e2-a800-4442-8c3d-648e8eef5678.png)


In **Create Deployment for API Service** task of `deploy-k8s-cluster.yml`, update the IP after *welcome123@*

![Screen Shot 2021-12-13 at 12 25 01 PM](https://user-images.githubusercontent.com/37121874/145859310-82535326-a2da-4179-bb42-9d94e96e32ce.png)


In **Create Deployment for Worker Service** task of `deploy-k8s-cluster.yml`, update the IP after *welcome123@*


### Configure CloudSQL With DBMate Migration Scripts

```
ansible-playbook deploy-setup-cloud-sql.yml -i inventory.yml
```

### Deploy Kubernetes Cluster

```
ansible-playbook deploy-k8s-cluster.yml -i inventory.yml --extra-vars cluster_state=present
```

This step will take approximately 10 minutes.

### View the Web App

From the terminal output of the *Debug vars* task, copy the **nginx_ingress_ip**

<img width="289" alt="Screen Shot 2021-12-12 at 10 59 17 PM" src="https://user-images.githubusercontent.com/37121874/145750274-660de048-5c9b-4bce-9b52-46eef3552fed.png">

Go to `http://<YOUR INGRESS IP>.sslip.io` to view the Crypto Forecasting App!




<img width="687" alt="Screen Shot 2021-12-14 at 10 09 07 AM" src="https://user-images.githubusercontent.com/6150979/146024685-4c2ea27f-4658-4459-a110-c4291c17126c.png">


















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

## Re-Deploying Docker Containers On GCP

**You will need to follow the previous step-by-step guide on full deployment to production before using these instructions.**

*Note that when re-deploying, it should take around 10-15 minutes to get everything up and running again; when deploying for the first time, it takes about 1.5-2 hours since it's over an hour for the containers to be built and pushed to GCR*

Kill and remove running docker containers on VM following this [article](https://typeofnan.dev/how-to-stop-all-docker-containers/): `sudo docker kill $(sudo docker ps -q)`

Remove the network and images from the VM: `sudo docker system prune -a`

If you have made any updates locally, make sure to push or stash those changes. Additionally, you should make sure that these files and folders are no longer present:
- api-logging.log
- worker-logging.log
- model-experiments/

It also important that your machine name, persistent-disk, and VM are correct in `inventory.yml`

You also need to make sure that the symbols you want to be automatically downloaded to the database are correctly (un)commented within *run()* of `service_david.py`

You also need to make sure that the you are fetching 1M observations within *fetch_price_history_async()* of `run_historical.py`

You also need to make sure that the model fetching time is correct within *TrackerService()* of `tracker.py`

Rebuild and redeploy the images
```
ansible-playbook deploy-docker-images.yml -i inventory.yml
```
- Update the *deployment/.docker-tag* from the *stdout_lines* of the *Print tag* Ansible task

Deploy the Docker containers on the VM
```
ansible-playbook deploy-setup-containers.yml -i inventory.yml
```
- don't need to create the compute instance or provision the server (adding all the necessary files like Docker, etc.) since this has been done previously

Set up the web server on the compute instance: 
```
ansible-playbook deploy-setup-webserver.yml -i inventory.yml
```
 
Copy the External IP (either from Terminal or from GCP Compute Enginer page), and **paste** it into the browser to view the web app!
- For some reason, doesn't work to just click on the External IP from the GCP Compute Engine page

Delete the VM
```
ansible-playbook deploy-create-instance.yml -i inventory.yml --extra-vars cluster_state=absent
```

Please note that for the current setup, this will delete the VM but NOT the persistent disk. In order to do that from GCP Compute Engine go to *Disks* on the left-hand side (under *Storage* section), find your particular persistent disk, and subsequently delete it.










## Monitoring the VM deployment instance Using SSH and VSCode

In order to monitor the data fetching, the logs happening in the API, you can either ssh to the VM using the GCP portal or connect your VSCode IDE to the VM using SSH. We will here outline the steps in order for you to do so:

- Requirements:
    - Having a GCP instance running
    - Having VSCode installed in your computer
    - Have gcloud sdk installed, [gcloud](https://cloud.google.com/sdk/install)

- Run `gcloud init`
- Setup ssh keys on your computer and add them to the VM instance
- Install extension Remote-SSH on VSCode
- On the Command palette, type `remote-ssh` and click the *Add New Host* option
- Enter the following command: `ssh -i ~/.ssh/[KEY FILENAME] [USER NAME]@[External IP]`. KEY FILENAME and USER NAME are what you typed in step #2. External IP can be found from your GCP Compute Engine VM Instances page and is unique to each VM. Another prompt pops up, asking you to Select SSH configuration file to update. Just click the first one, and you should see Host Added! at the bottom right-hand corner of your VSCode window.
- Open up the Command Palette and type `remote-ssh again`. This time click on *Connect to Host*. Then select the IP address of your VM from the list that pops up.

## Modeling

The modeling portion of this project is organized as follows:

------------
      .
      ├── models
      │   ├── LSTM_BNBBTC_13-12-2021
      │   └── LSTM_BNBUSDT_13-12-2021
      │   └── LSTM_BTCUSDT_13-12-2021
      |   └── LSTM_ETHBTC_13-12-2021
      |   └── LSTM_ETHUSDT_13-12-2021
      ├── notebooks
      │   ├── LSTM_Modeling_FINAL.ipynb
      │   └── LSTM_Modeling_Milesotne3.ipynb
      │   └── initial_EDA_and_modeling.ipynb

--------

The `notebooks` directory contains the notebooks used to iterate over the data preprocessing and modeling pipeline and subsequently produce the final models used in production. The `models` directory contains the most up-to-date models used in production.

### Modeling Infrastructure

- Original models creation happens in Google Colaboratory Notebook
- Models are uploaded to the GCS bucket
- From the GCS bucket, the API queries for the best model to use for real-time predictions
- The models are re-trained on new, incoming data asyncronously on daily basis
- The raw data obtained from the GCS bucket goes to a preprocessing pipeline before being fed to the model (more information on the preprocessing pipeline in subsequent sections)
- The training architecture and the data preprocessing pipeline are common for all pairs. The only major difference is the raw data fed into the preprocessing pipeline.
- Future steps: automated model training pipeline utilizing VertexAI that independently initializes model training once a user enters a new symbol through the frontend API

### Dataset(s)

Dataset(s)

- Historical data queried from Binance API (dtype: candlesticks)
- Real time data updating from Binance through a web socket (dtype: candlesticks)

Dataset(s) Size

- Number of datasets: 1,612 (one dataset per pair)
- Size of dataset per pair (~0.3Gb)
- Total dataset(s) size (~500Gb)

Dataset(s) Features

- Open Time: Candle Open Time
- Open: Open Price in Quote Asset Units
- High: High Price in Quote Asset Units
- Low: Low Price in Quote Asset Units
- Close: Close Price in Quote Asset Units
- Volume: Total Traded Volume in Base Asset Units
- Close Time: Candle Close Time
- Quote Asset Volume: Total Traded Volume in Quote Asset Units
- Number of Trades: Total Number of Trades
- Taker Buy Base Asset Volume: Taker (Matching Existing Order) Buy Base Asset Volume
- Taker Buy Quote Asset Volume: Taker (matching Existing Order) Buy Quote Asset Volume
- Ignore: Safe to Ignore

Initial EDA and modeling performed on the BTC-USDT pair. The model in the final deliverable is extended to 5 pairs (BTC-USDT, BNB-BTC, BNB-USDT, ETH-BTC, ETH-USDT). New model training currently possible through the GCS-Google Colaboratory pipeline. However, new model training should be manually executed.

### Modeling Decisions

- 80-10-10 train-validation-test split (HP tuning models)
- 100-0-0 train-validation-test split (Models pushed to GCS)
- Feature Engineering for the Tensorflow Modeling:
    - Remove *Close Time, Open Time, NA*
    - Time-based features
    - Statistical features
    - Domain knlowedge-based features
    - Log-transform data (numerical features)
    - Standardize data (whole dataset)
- Metrics: Mean Squared Error (MSE), Mean Absolute Error (MAE)
- Prediction: standardized `mid_price_true - mid_price_baseline`

Baseline - Persistent Model:

- For Multi-input, Single-output predicts the Close Price of the next time step to be the same as the Close Price of the current time step
- For Multi-input, Multi-output predicts the Close Price of the next X time steps to be the same as the Close Price of the current time step

Second Iteration - LSTM on Raw Standardized Features:

- For Multi-input, Single-output predicts the Close Price of the next time step based on the input features of the previous X time steps
- For Multi-input, Single-output predicts the Close Price of the X next time steps based on the input features of the previous X time steps

Final Model - LSTM on Engineered Features

- Feature Engineering on input data: Log-transformed, Standardized, Time-based features, Statistical features, Domain knowledge - based features)
- Feature Engineering on output data: Transformed the output feature to standardized `mid_price_true - mid_price_baseline`
