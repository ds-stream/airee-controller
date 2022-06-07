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
    # create repo
    name = airee_repo.repo_naming(type)
    logger.info(f"Create repo '{name}' for workspace {airee_repo.workspace}")
    repo_gh = airee_repo.create_repo(name, auto_init=True)
    # create deploy-key for init push
    logger.info(f"Added Deploy Key")
    priv_k, pub_k, dk = airee_repo.set_deploy_key('init_push', repo_gh, False)

    return repo_gh, priv_k, pub_k

def add_token_to_sectets(airee_repo, repo_gh):
    # Add secret for infra repo
    logger.info(f"Adding secret TF_VAR_github_token")
    airee_repo.set_secret(repo_gh, "TF_VAR_github_token", airee_repo.token)

    return 0

def workspace_repo_create(airee_repo, **kwargs):
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
    app_git.commit_all("Init commit")
    app_git.push()

    return app_git

def infra_repo_create(airee_repo, **kwargs):
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
    parser.add_argument('-t', '--token', action='store', required=True)
    parser.add_argument('-w', '--workspace', action='store', required=True)
    parser.add_argument('-e', '--env', action='store', choices=['prd', 'dev', 'uat'], required=False, default='dev')
    parser.add_argument('-r', '--tier', action='store', choices=['small', 'standard', 'large'], required=True)
    parser.add_argument('-b', '--branch', action='store', required=False, default='main')

    args = vars(parser.parse_args())
    
    try:
        airee = Airee_gh_repo(args['token'], args['workspace'], env=args['env'])
        workspace_data = workspace_repo_create(airee, extra_context={'repo_name': 'workspace_data', 'env': args['env'], 'workspace': args['workspace'], 'org': airee.org}, default_config=True, overwrite_if_exists=True, no_input=True, checkout=args['branch'])
        app = app_repo_create(airee, workspace_data, extra_context={'repo_name': 'app', 'env': args['env'], 'workspace': args['workspace'], 'org': airee.org}, default_config=True, overwrite_if_exists=True, no_input=True, checkout=args['branch'])
        infra = infra_repo_create(airee, extra_context={'repo_name': 'infra', 'env': args['env'], 'workspace': args['workspace'], 'org': airee.org, 'airflow_performance': args['tier']}, default_config=True, overwrite_if_exists=True, no_input=True, checkout=args['branch'])
    except Exception as e:
        logger.error(str(e))
        # raise e

    # airee.create_repo_from_template(args['repo'], extra_context={'repo_name': args['repo'], 'env': args['env'], 'workspace': args['workspace'], 'org': airee.org}, default_config=True, overwrite_if_exists=True, no_input=True)