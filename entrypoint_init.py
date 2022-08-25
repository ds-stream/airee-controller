"""Module with entrypoint functions and script for docker image.
"""
from airee_repos import Airee_gh_repo
from git_module import Gitrepo
import config, util
import argparse
from os.path import join as path_join 
import logging

logger = logging.getLogger(__name__)
logger.setLevel(config.log_lvl)
logger.addHandler(config.ch)
logger.propagate = False


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


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Init Airee repos base on template')
    parser.add_argument('-t', '--token', action='store', required=True, help="GitHub PAT needed to create repositories and deploy keys - Required")
    parser.add_argument('-w', '--workspace', action='store', required=True, help="workspace name - Required")
    parser.add_argument('-e', '--env', action='store', choices=['prd', 'dev', 'uat'], required=False, default='dev', help="environment name (for future purposes) - default='dev'")
    parser.add_argument('-r', '--tier', action='store', choices=['small', 'standard', 'large'], required=True, help="environment size (maps to VM sizes, etc. ) - Required")
    parser.add_argument('-b', '--branch', action='store', required=False, default='main', help="template repositories branch to be used, optional parameter, default = main")
    parser.add_argument('-p', '--project', action='store', required=True, help="GCP project - Required")
    parser.add_argument('-l', '--ghrlabels', action='store', required=False, default='airflow', help="GitHub Actions runner labels - default='airflow'")
    parser.add_argument('-g', '--ghorg', action='store', required=True, help="GitHub organization - Required")
    parser.add_argument('-s', '--tfbuckend', action='store', required=True, help="Terraform GCS bucket name to store TF state - Required")
    parser.add_argument('-k', '--key', action='store', required=False, default=None, help="private key needed for SSL/TLS in Airflow Webserver")
    parser.add_argument('-c', '--cert', action='store', required=False, default=None, help="certificate needed for SSL/TLS in Airflow Webserver")
    parser.add_argument('-d', '--domain', action='store', required=False, default=None, help="name of domain in GCP Project")
    parser.add_argument('-z', '--dnszone', action='store', required=False, default=None, help="name of dns-zone service in GCP Project")
    parser.add_argument('-n', '--nfsdags', action='store', required=False, choices=['yes', 'no'], default='yes', help="Flag if DAGs will be keeped on NFS, otherwise DAGs will be in image")
    args = vars(parser.parse_args())
    
    # check certs
    if (args['cert'] == None) & (args['domain'] == None):
        logging.info(f"Cert secret name was not passed. Self signed cert will be generated.")
        app_cert = f"{args['workspace']}-airee_cert"
        app_key = f"{args['workspace']}-airee_key"
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
        airee = Airee_gh_repo(args['token'], args['workspace'], env=args['env'], org=args['ghorg'])
        workspace_data = workspace_repo_create(airee, extra_context={'repo_name': 'workspace_data', 'env': args['env'], 'workspace': args['workspace'], 'org': airee.org, 'labels': args['ghrlabels'], 'nfs_dags': nfsdags, 'project_id': args['project']}, default_config=True, overwrite_if_exists=True, no_input=True, checkout=args['branch'])
        app = app_repo_create(airee, workspace_data, extra_context={'repo_name': 'app', 'env': args['env'], 'workspace': args['workspace'], 'org': airee.org, 'labels': args['ghrlabels'], 'project_id': args['project'], 'key_name': app_key, 'cert_name': app_cert, 'nfs_dags': nfsdags}, default_config=True, overwrite_if_exists=True, no_input=True, checkout=args['branch'])
        infra = infra_repo_create(airee, extra_context={'repo_name': 'infra', 'env': args['env'], 'workspace': args['workspace'], 'org': airee.org, 'airflow_performance': args['tier'], 'labels': args['ghrlabels'], 'project_id': args['project'], 'tf_backend': args['tfbuckend'], 'domain': args['domain'], 'dns_zone': args['dnszone'], 'cert_name': args['cert'], 'nfs_dags': nfsdags}, default_config=True, overwrite_if_exists=True, no_input=True, checkout=args['branch'])

    except Exception as e:
        logger.error(str(e))

