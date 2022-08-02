# Controller

For now it just creating repos.
## How to test it:
- build image
  ```sh
  docker build . -t controller
  ```
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

  example
  ```sh
  docker run --rm controller -t yourpersonaltokenxyz -w test123 -r small -e dev -p infra-sandbox-352609 -l gcp,airee -k key -c cert -s test-mm-terra
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
