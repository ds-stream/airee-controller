# Controller

For now it just creating repos.
How to test it:
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

