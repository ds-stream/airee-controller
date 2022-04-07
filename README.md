# Controller

For now it just creating repos.
## How to test it:
- build image
  ```sh
  docker build . -t controller
  ```
- run docker with proper args.  
  usage: docker run --rm controller -t TOKEN -w WORKSPACE -r {app,workspace_data,infra} [-e {prd,dev,uat}]

  -h, --help            show this help message and exit  
  -t TOKEN, --token TOKEN  
  -w WORKSPACE, --workspace WORKSPACE  
  -r {app,workspace_data,infra}, --repo {app,workspace_data,infra}  
  -e {prd,dev,uat}, --env {prd,dev,uat}  

  example
  ```sh
  docker run --rm controller -t yourpersonaltokenxyz -w test123 -r workspace_data
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
