""""""
from github import Github
from github.GithubException import GithubException
import pygit2
from pair_key import PairKey
import config, util
from cookiecutter.main import cookiecutter
from os.path import join as path_join 
import sys
import logging

logger = logging.getLogger(__name__)
logger.setLevel(config.log_lvl)
logger.addHandler(config.ch)
logger.propagate = False

class Airee_gh_repo:

    def __init__(self, token, workspace, org='DsAirKube', env='prd') -> None:
        """"""
        self.workspace = workspace
        self.env = env
        self.org = org
        self.token = token
        self.gh = Github(token)
        self.gh_org = self.__set_org()
        logger.debug("Airee Obj created")

    def __set_org(self):
        """return organization object."""
        org_obj = self.gh.get_organization(self.org)
        logger.debug(f"Organization set to {self.org}")
        return org_obj

    def repo_naming(self, type):
        """return name in order to naming convention."""
        return f'{self.workspace}_{type}_{self.env}'

    def create_repo(self, name, private=True, **kwargs):
        """Method to create repos."""
        try:
            repo_obj = self.gh_org.create_repo(name, private=private, **kwargs)
            logger.debug(f"Repositoy {name} created in {self.org}")
            logger.debug(f"Repositoy url: {repo_obj.git_url}")
        except GithubException as e:
            if e.status==422 and (any(mesg.get('message')=='name already exists on this account' for mesg in e.data.get('errors', []))):
                logger.error(f"Repository name {name} already exist in {self.org}")
                sys.exit(1)
            else:
                raise e
        return repo_obj

    def create_empty_repo_gh(self, type):
        """Init repo for Airee.
        Params:
        type [str] Value from list [infra, app, workspace_data]
        Return: repository pygithub object
        """
        name = self.repo_naming(type)
        return self.create_repo(name)
    
    def get_airee_repo(self, type):
        """Get repo object by airee name"""
        name = self.repo_naming(type)
        return self.gh_org.get_repo(name)

    def set_deploy_key(self, name, repo_obj, read_only=True):
        """Method to set deploy_key on repo"""
        priv_key, pub_key = PairKey.generate_pair_ecdsa()
        key_obj = repo_obj.create_key(name, pub_key.decode(), read_only)
        return priv_key, pub_key, key_obj
    
    def remove_deploy_key(self, key_obj):
        return key_obj.delete()
    
    def set_secret(self, repo_obj, name, secret):
        """Method to set secret in repo"""
        try:
            r = repo_obj.create_secret(name, secret)
        except Exception as e:
            logger.error(f"Can't create secret {secret} in repo {repo_obj.name}")
            raise e
        return r

    def generate_from_template(self, type, path, tag, org=None, **kwargs):
        """Method to generate files from template stored on github"""
        org_name = org if org else self.org
        git_url = f'https://{self.token}@github.com/{org_name}/{config.template[type]}'
        try:
            cookiecutter(git_url, output_dir=path, **kwargs)
            logger.debug(f"Created repo from template url {git_url.replace(self.token, 'git')}")
            return path
        except Exception as e:
            # configure logging
            logger.error("Can't create repo from template - check logs")
            raise e


    def delete_repo(self, repo_obj):
        """Method to delete repo"""
        try: 
            repo_obj.delete()
        except GithubException as e:
            if e.data.get('message') == 'Must have admin rights to Repository.':
                # logging error
                logger.error("Must have admin rights to Repository.")
                sys.exit(1)
            else:
                raise
        return 0

