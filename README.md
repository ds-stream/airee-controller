# Controller

- Create a new repository
- Launch an infrastructure pause
- Infrastructure resumption after pausing
- Removal of working infrastructure

## How to run:
- build image
  ```sh
  docker build . -t controller
  ```
### Create new repository
- run docker with proper args.

  -h, --help            show this help message and exit  
  -t TOKEN, --token TOKEN | GitHub PAT needed to create repositories and deploy keys - <b>Required</b>  
  -w WORKSPACE, --workspace WORKSPACE | workspace name - <b>Required</b>  
  -e {prd,dev,uat}, --env {prd,dev,uat} | environment name (for future purposes) - default='dev'  
  -r {small,standard,large}, --tier {small,standard,large} | environment size (maps to VM sizes, etc.) - <b>Required</b>  
  -b BRANCH, --branch BRANCH | template repositories branch to be used, optional parameter, default = main  
  -p PROJECT, --project PROJECT | GCP project - <b>Required</b>  
  -l GHRLABELS, --ghrlabels GHRLABELS | GitHub Actions runner labels - default='airflow'  
  -g GHORG, --ghorg GHORG | GitHub organization - <b>Required</b>  
  -s TFBUCKEND, --tfbuckend TFBUCKEND | Terraform GCS bucket name to store TF state - <b>Required</b>  
  -k KEY, --key KEY | private key needed for SSL/TLS in Airflow Webserver  
  -c CERT, --cert CERT | certificate needed for SSL/TLS in Airflow Webserver  
  -d DOMAIN, --domain DOMAIN | name of domain in GCP Project  
  -z DNSZONNE, --dnszone DNSZONE | name of dns-zone service in GCP Project  
  -n NFSDAGS, --nfsdags NFSDAGS {yes, no} | Flag if DAGs will be keeped on NFS, otherwise DAGs will be in image - default='yes'  

  example
  ```sh
  docker run --rm controller create -t yourpersonaltokenxyz -w test123 -r small -e dev -p gcp-ds-stream -l gcp,airee -k key -c cert -s test-mm-terra -g ds-stream
  ```
### Start pause
- run docker with proper args.

  -h, --help            show this help message and exit  
  -t TOKEN, --token TOKEN | GitHub PAT needed to perform actions in the repository and deploy keys - <b>Required</b>  
  -w WORKSPACE, --workspace WORKSPACE | workspace name - <b>Required</b>  
  -e {prd,dev,uat}, --env {prd,dev,uat} | environment name - <b>Required</b>
  -g GHORG, --ghorg GHORG | GitHub organization - <b>Required</b>    

  example
  ```sh
  docker run --rm controller pause -t yourpersonaltokenxyz -w test123 -e dev -g ds-stream
  ```
### Start full infrastructure
- run docker with proper args.

  -h, --help            show this help message and exit  
  -t TOKEN, --token TOKEN | GitHub PAT needed to perform actions in the repository and deploy keys - <b>Required</b>  
  -w WORKSPACE, --workspace WORKSPACE | workspace name - <b>Required</b>  
  -e {prd,dev,uat}, --env {prd,dev,uat} | environment name - <b>Required</b>
  -g GHORG, --ghorg GHORG | GitHub organization - <b>Required</b>    

  example
  ```sh
  docker run --rm controller start -t yourpersonaltokenxyz -w test123 -e dev -g ds-stream
  ```
### Destroy infrastructure
- run docker with proper args.

  -h, --help            show this help message and exit  
  -t TOKEN, --token TOKEN | GitHub PAT needed to perform actions in the repository and deploy keys - <b>Required</b>  
  -w WORKSPACE, --workspace WORKSPACE | workspace name - <b>Required</b>  
  -e {prd,dev,uat}, --env {prd,dev,uat} | environment name - <b>Required</b>
  -g GHORG, --ghorg GHORG | GitHub organization - <b>Required</b>    

  example
  ```sh
  docker run --rm controller destroy -t yourpersonaltokenxyz -w test123 -e dev -g ds-stream
  ```
## push to gcr

```sh
docker tag controller:latest gcr.io/dsstream-airflowk8s/controller:latest
docker push gcr.io/dsstream-airflowk8s/controller
```

## push to azure cr

on azure portal terminal:
```sh
az acr login -n airflowkubernetesui.azurecr.io --expose-token
```
on local:
```sh
docker login airflowkubernetesui.azurecr.io --username 00000000-0000-0000-0000-000000000000 --password __generated_token__
docker tag controller:latest airflowkubernetesui.azurecr.io/controller:latest
docker push airflowkubernetesui.azurecr.io/controller
```

## run o aks:
e.g.
```sh
az aks get-credentials --resource-group airflow_kubernetes_ui --name airflow_kubernetes_ui_test
kubectl run init-app1 --image=airflowkubernetesui.azurecr.io/controller:latest --restart=Never -i --rm -- -t GH_token -w test13 -r small
```

## Pydoc

All modules, functions, class and methods have pydoc using [google python style](https://github.com/google/styleguide/blob/gh-pages/pyguide.md#38-comments-and-docstrings)
# airflow-controller


---
## :wave: Hi, we're DSStream
We are an experienced GenAI & Data consulting company founded in 2017, focused on analytics data management, AI, and innovative solutions for global brands from all over the world.

 ## :eyes: We're interested in
- **[Advanced Analytics & Data Science](https://dsstream.com/services/advanced-analytics)**
- **[Machine Learning & MLOps](https://dsstream.com/services/mlops)**
- **[Generative AI & AI Solutions](https://dsstream.com/services/genai)**
- **[Data Engineering & Cloud Solutions](https://dsstream.com/services/data-engineering)**
- **[Apache Airflow Managed Services](https://dsstream.com/services/airflow)**

 ## :seedling: We're currently developing
- Custom GenAI tools and solutions
- MLOps best practices across multiple cloud platforms
- Data pipeline automation and scaling solutions
- Feature store optimization and model execution workflows
- Standardized ML workflows with automated deployment

## :handshake: We're looking to collaborate on
- GenAI-driven business initiatives
- Data transformation projects
- Cloud migration and optimization
- Custom software engineering challenges
- Machine learning implementation across various industries

 ## :clipboard: About us
DS STREAM has grown into a leading GenAI & Data consulting company with an interdisciplinary team of over 150 seasoned experts equipped with more than 130 certifications from top technology partners, including Google, Microsoft Azure, and Databricks.
 ## :zap: Few facts
- Our team has delivered projects across FMCG, retail, e-commerce, healthcare, telco, finance, and logistics sectors
- We follow a technology-agnostic approach to provide tailored solutions
- DS STREAM is ISO/IEC 27001:2013 certified, ensuring top-tier data security

## :mailbox: Reach us
- Website: dsstream.com
- Email: growth@dsstream.com
- Phone: +48 22 417 34 33
- Headquarters:
:round_pushpin:Poland: Grochowska 306/308, 03-840 Warsaw
:round_pushpin:USA: 1209 Orange St, Wilmington, DE 19801
