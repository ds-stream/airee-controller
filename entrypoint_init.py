"""Module with entrypoint functions and script for docker image.
"""
from airee_repos import Airee_gh_repo
from git_module import Gitrepo
import config, util
import argparse
from os.path import join as path_join 
import logging
import json 
import re #library for name check

logger = logging.getLogger(__name__)
logger.setLevel(config.log_lvl)
logger.addHandler(config.ch)
logger.propagate = False


def name_check(name, pattern, max_len, min_len):
    """Function to validate workspace name.

    Due to limitation of 30 characters for account name, wokspace name need to be limit as weel.
    Workspace name Will be glued to the 'wi-user-sa-' pattern.
    """
    if not (len(name) >= min_len and len(name) <= max_len and bool(re.match(pattern, name)) == True):
        logger.error(f"Workspace name should have between {min_len} and {max_len} characters, and can contain characters with regex {pattern}!")
        raise SystemExit(1)
    return True


def create_repo_with_keypair(airee_repo, type):
    """Function to create GH repositorie with deploy key using project naming convntion.

    Args:
        airee_repo: Airee_gh_repo object
        type: string with type ["infra", "app", "workspace_data"]

    Returns:
        Repository object with deploy key pair.
    """
    # create repo
    name = airee_repo.repo_naming(type)
    logger.info(f"Create repo '{name}' for workspace {airee_repo.workspace}")
    repo_gh = airee_repo.create_repo(name, auto_init=True)
    # create deploy-key for init push
    logger.info(f"Added Deploy Key")
    priv_k, pub_k, dk = airee_repo.set_deploy_key('init_push', repo_gh, False)

    return repo_gh, priv_k, pub_k

def add_token_to_sectets(airee_repo, repo_gh):
    """Function to PAT from airee_repo object atribute to repository as a secret.

    Args:
        airee_repo: Airee_gh_repo object
        repo_gh: Repository object where PAT will be placed
    
    Returns:
        0 value if exit without error
    """
    # Add secret for infra repo
    logger.info(f"Adding secret TF_VAR_github_token")
    airee_repo.set_secret(repo_gh, "TF_VAR_github_token", airee_repo.token)

    return 0

def workspace_repo_create(airee_repo, **kwargs):
    """Function to create "workspace data" repository.

    Args:
        airee_repo: Airee_gh_repo object.
        kwargs: dict with params passed to generate_from_template method in Airee_gh_repo object (cookiecutter params)
    
    Returns:
        git repository object of "workspace data" repository.
    """
    path = util.get_tmp_path('workspace_data')
    repo_gh, priv_k, pub_k = create_repo_with_keypair(airee_repo, 'workspace_data')

    logger.debug(f"Path to tmp folder: {path_join(path, 'workspace_data')}")
    logger.debug(f"Url to repo : {repo_gh.git_url}")

    add_token_to_sectets(airee_repo, repo_gh)
    workspace_git = Gitrepo(repo_gh.ssh_url, priv_k, pub_k)

    workspace_git.clone_repo(path_join(path, 'workspace_data'))
    airee_repo.generate_from_template('workspace_data', path, **kwargs)
    workspace_git.commit_all("Init commit [skip ci]")
    workspace_git.push()

    return workspace_git

def app_repo_create(airee_repo, workspace_git, **kwargs):
    """Function to create "app" repository with "workspace data" repository as a submodule.

    Args:
        airee_repo: Airee_gh_repo object.
        workspace_git: workspace git repository object.
        kwargs: dict with params passed to generate_from_template method in Airee_gh_repo object (cookiecutter params)
    
    Returns:
        git repository object of "app" repository.
    """
    path = util.get_tmp_path('app')
    repo_gh, priv_k, pub_k = create_repo_with_keypair(airee_repo, 'app')

    logger.debug(f"Path to tmp folder: {path_join(path, 'app')}")
    logger.debug(f"Url to repo : {repo_gh.git_url}")

    add_token_to_sectets(airee_repo, repo_gh)
    airee_repo.set_secret(repo_gh, "priv_k_dags", workspace_git.prv_k.decode())

    app_git = Gitrepo(repo_gh.ssh_url, priv_k, pub_k)
    app_git.clone_repo(path_join(path, 'app'))
    airee_repo.generate_from_template('app', path, **kwargs)
    app_git.add_submodule(workspace_git, 'dags')
    app_git.commit_all("Init commit [skip ci]")
    app_git.push()

    return app_git

def infra_repo_create(airee_repo, **kwargs):
    """Function to create "infra" repository.

    Args:
        airee_repo: Airee_gh_repo object.
        kwargs: dict with params passed to generate_from_template method in Airee_gh_repo object (cookiecutter params)
    
    Returns:
        git repository object of "infra" repository.
    """
    path = util.get_tmp_path('infra')
    repo_gh, priv_k, pub_k = create_repo_with_keypair(airee_repo, 'infra')

    logger.debug(f"Path to tmp folder: {path_join(path, 'infra')}")
    logger.debug(f"Url to repo : {repo_gh.git_url}")

    add_token_to_sectets(airee_repo, repo_gh)
    infra_git = Gitrepo(repo_gh.ssh_url, priv_k, pub_k)

    infra_git.clone_repo(path_join(path, 'infra'))
    airee_repo.generate_from_template('infra', path, **kwargs)
    infra_git.commit_all("Init commit")
    infra_git.push()

    return infra_git

def change_status_json(path, status):

    with open(path_join(path, 'infra', "status.json"), "r") as status_file:
       json_object = json.load(status_file)

    if (json_object["status"] == "down") & (status == "pause"):
        logger.error(f"Pause operation cannot be execute while infra is down.")
        return 1
    if json_object["status"] == status :
        logger.error(f"{status} operation cannot be execute because infra status is now {status}")
        return 1
    
    old_status = json_object["status"]
    logger.info(f"Status change from {old_status} to {status}")
    json_object["status"] = status

    with open(path_join(path, 'infra', "status.json"), "w") as status_file:
       json.dump(json_object, status_file, indent=2)

    return 0

def change_status(airee_repo, status):

    path = util.get_tmp_path('infra')
    repo_gh = airee_repo.get_airee_repo('infra')
    priv_k_tmp, pub_k_tmp, dk_tmp = airee_repo.set_deploy_key('set_deploy_key', repo_gh, False)

    infra_git = Gitrepo(repo_gh.ssh_url, priv_k_tmp, pub_k_tmp)
    infra_git.clone_repo(path_join(path, 'infra'))

    if not change_status_json(path, status):
        infra_git.commit_all("Update status")
        infra_git.push()
    
    airee_repo.remove_deploy_key(dk_tmp)

    return 0

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Init Airee repos base on template')
    subparser = parser.add_subparsers(dest='command')
    create = subparser.add_parser('create')
    pause = subparser.add_parser('pause')
    start = subparser.add_parser('start')
    destroy = subparser.add_parser('destroy')

    pause.add_argument('-t', '--token', action='store', required=True, help="GitHub PAT needed to perform actions in the repository and deploy keys - Required")
    pause.add_argument('-w', '--workspace', action='store', required=True, help="workspace name - Required")
    pause.add_argument('-e', '--env', action='store', choices=['prd', 'dev', 'uat'], required=True, help="environment name - Required ")
    pause.add_argument('-g', '--ghorg', action='store', required=True, help="GitHub organization - Required")

    start.add_argument('-t', '--token', action='store', required=True, help="GitHub PAT needed to perform actions in the repository and deploy keys - Required")
    start.add_argument('-w', '--workspace', action='store', required=True, help="workspace name - Required")
    start.add_argument('-e', '--env', action='store', choices=['prd', 'dev', 'uat'], required=True, help="environment name - Required")
    start.add_argument('-g', '--ghorg', action='store', required=True, help="GitHub organization - Required")

    destroy.add_argument('-t', '--token', action='store', required=True, help="GitHub PAT needed to perform actions in the repository and deploy keys - Required")
    destroy.add_argument('-w', '--workspace', action='store', required=True, help="workspace name - Required")
    destroy.add_argument('-e', '--env', action='store', choices=['prd', 'dev', 'uat'], required=True, help="environment name - Required")
    destroy.add_argument('-g', '--ghorg', action='store', required=True, help="GitHub organization - Required")

    create.add_argument('-t', '--token', action='store', required=True, help="GitHub PAT needed to create repositories and deploy keys - Required")
    create.add_argument('-w', '--workspace', action='store', required=True, help="workspace name - Required")
    create.add_argument('-e', '--env', action='store', choices=['prd', 'dev', 'uat'], required=False, default='dev', help="environment name (for future purposes) - default='dev'")
    create.add_argument('-r', '--tier', action='store', choices=['small', 'standard', 'large'], required=True, help="environment size (maps to VM sizes, etc. ) - Required")
    create.add_argument('-b', '--branch', action='store', required=False, default='main', help="template repositories branch to be used, optional parameter, default = main")
    create.add_argument('-p', '--project', action='store', required=True, help="GCP project - Required")
    create.add_argument('-l', '--ghrlabels', action='store', required=False, default='airflow', help="GitHub Actions runner labels - default='airflow'")
    create.add_argument('-g', '--ghorg', action='store', required=True, help="GitHub organization - Required")
    create.add_argument('-s', '--tfbuckend', action='store', required=True, help="Terraform GCS bucket name to store TF state - Required")
    create.add_argument('-k', '--key', action='store', required=False, default=None, help="private key needed for SSL/TLS in Airflow Webserver")
    create.add_argument('-c', '--cert', action='store', required=False, default=None, help="certificate needed for SSL/TLS in Airflow Webserver")
    create.add_argument('-d', '--domain', action='store', required=False, default=None, help="name of domain in GCP Project")
    create.add_argument('-z', '--dnszone', action='store', required=False, default=None, help="name of dns-zone service in GCP Project")
    create.add_argument('-n', '--nfsdags', action='store', required=False, choices=['yes', 'no'], default='no', help="Flag if DAGs will be keeped on NFS, otherwise DAGs will be in image")
    args = vars(parser.parse_args())
    

    if args['command'] == 'create':
        # check certs
        if (args['cert'] == None) & (args['domain'] == None):
            logging.info(f"Cert secret name was not passed. Self signed cert will be generated.")
            app_cert = f"{args['workspace']}-{args['env']}-airee_cert"
            app_key = f"{args['workspace']}-{args['env']}-airee_key"
        elif (args['cert'] == None) & (args['domain'] != None):
            logging.error("Domain passed without Cert! Please pass Cert Secret name.")
            exit(1)
        else:
            app_cert = args['cert']
            app_key = args['key']

        #check NFS
        if args['nfsdags'] == 'no':
            nfsdags = None
        else:
            nfsdags = args['nfsdags']

        try:
            name_check(args['workspace'], "^[a-z0-9-]*$", 19, 1)
            airee = Airee_gh_repo(args['token'], args['workspace'], env=args['env'], org=args['ghorg'])
            workspace_data = workspace_repo_create(airee, extra_context={'repo_name': 'workspace_data', 'env': args['env'], 'workspace': args['workspace'], 'org': airee.org, 'labels': args['ghrlabels'], 'nfs_dags': nfsdags, 'project_id': args['project']}, default_config=True, overwrite_if_exists=True, no_input=True, checkout=args['branch'])
            app = app_repo_create(airee, workspace_data, extra_context={'repo_name': 'app', 'env': args['env'], 'workspace': args['workspace'], 'org': airee.org, 'labels': args['ghrlabels'], 'project_id': args['project'], 'key_name': app_key, 'cert_name': app_cert, 'nfs_dags': nfsdags}, default_config=True, overwrite_if_exists=True, no_input=True, checkout=args['branch'])
            infra = infra_repo_create(airee, extra_context={'repo_name': 'infra', 'env': args['env'], 'workspace': args['workspace'], 'org': airee.org, 'airflow_performance': args['tier'], 'labels': args['ghrlabels'], 'project_id': args['project'], 'tf_backend': args['tfbuckend'], 'domain': args['domain'], 'dns_zone': args['dnszone'], 'cert_name': args['cert'], 'nfs_dags': nfsdags}, default_config=True, overwrite_if_exists=True, no_input=True, checkout=args['branch'])

        except Exception as e:
            logger.error(str(e))

    elif args['command'] == 'pause':
        airee = Airee_gh_repo(args['token'], args['workspace'], env=args['env'], org=args['ghorg'])
        infra = change_status(airee, 'pause')
        
    elif args['command'] == 'start':
        airee = Airee_gh_repo(args['token'], args['workspace'], env=args['env'], org=args['ghorg'])
        infra = change_status(airee, 'up')

    elif args['command'] == 'destroy':
        airee = Airee_gh_repo(args['token'], args['workspace'], env=args['env'], org=args['ghorg'])
        infra = change_status(airee, 'down')
    
   
