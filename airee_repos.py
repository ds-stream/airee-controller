"""Module to comunicate with Ariee repos on GitHub.

It use mainly github and cookiecutter frameworks.

    Typical usege:
    
    repo1 = Airee_gh_repo(PAT, name_of_workspace, github_org, env)
    repo1_obj = repo1.create_empty_repo_gh("infra")
    repo1.delete_repo(repo1_obj)
"""
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
    """Airee GitHub organization connector.

    Object of this class is communicate with GitHub Organization.
    There are methods to create and delete git repositories. You can also
    set deploy key and create secret in repository.
    This class contain also method "generate_from_template" to fulfil repo with files
    described in cookiecutter template repo.

    Attributes:
        workspace: string with name of Ariee workspace
        env: string with environment variable [e.g prd, dev, uat]
        org: string with name of GitHub Organization
        token: string value of PAT
        gh: GitHub class object
        gh_org: GitHub Organization object
    """
    def __init__(self, token, workspace, org='DsAirKube', env='prd') -> None:
        """Create Airee_gh_repo object."""
        self.workspace = workspace
        self.env = env
        self.org = org
        self.token = token
        self.gh = Github(token)
        self.gh_org = self.__set_org()
        logger.debug("Airee Obj created")

    def __set_org(self):
        """Return GitHub Organization object."""
        org_obj = self.gh.get_organization(self.org)
        logger.debug(f"Organization set to {self.org}")
        return org_obj

    def repo_naming(self, type):
        """Return name in order to naming convention.
        
        Args:
            type: string with type ["infra", "app", "workspace_data"]

        Returns:
            Name of repo for a given type in order to Airee naming convention.
        """
        return f'{self.workspace}_{type}_{self.env}'

    def create_repo(self, name, private=True, **kwargs):
        """Method to create git repository in GitHub.
        
        If name already exist, program is exit with 1.

        Args:
            name: string with name of repository
            private: bool, default value True
            kwargs: dict with other params that can be passed to create_repo in GitHub Organization object.

        Returns:
            GitHub repository object.
        """
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
        """Create GitHub repository using Airee naming convention.

        Args:
            type: string value from list [infra, app, workspace_data]
        Returns: 
            Repository GitHub object.
        """
        name = self.repo_naming(type)
        return self.create_repo(name)
    
    def get_airee_repo(self, type):
        """Get GitHub repository object by Airee type.
        
        Args:
            type: string value from list [infra, app, workspace_data]
        Returns: 
            Repository GitHub object.
        """
        name = self.repo_naming(type)
        return self.gh_org.get_repo(name)

    def set_deploy_key(self, name, repo_obj, read_only=True):
        """Method to set deploy_key on repository.
        
        Args:
            name: string name of "deploy key" in GH repository
            repo_obj: GH repository object where key will be placed
            read_only: bool read only flag, default True
        Returns:
            Method return priv, pub keys and GH key object
        """
        priv_key, pub_key = PairKey.generate_pair_ecdsa()
        key_obj = repo_obj.create_key(name, pub_key.decode(), read_only)
        return priv_key, pub_key, key_obj
    
    def remove_deploy_key(self, key_obj):
        """Method to remove deploy key in repository.
        
        Args:
            repo_obj: GH repository object where key will deleted
        Returns:
            Status of delete operation.
        """
        return key_obj.delete()
    
    def set_secret(self, repo_obj, name, secret):
        """Method to set secret in GH repository.

        If secret exists, method rise an Exeption.
        
        Args:
            repo_obj: GH repository object where secret will be placed
            name: string name of a secret in GH git repository
            secret: string value of secret
        Returns:
            Status of creation operation.
            """
        try:
            r = repo_obj.create_secret(name, secret)
        except Exception as e:
            logger.error(f"Can't create secret {secret} in repo {repo_obj.name}")
            raise e
        return r

    def generate_from_template(self, type, path, org=None, **kwargs):
        """Method to generate files from template stored on github.
        
        Method use a cookiecutter framework to create files from template.
        Will rise exeption if any issue with creation appear

        Args:
            type: string value from list [infra, app, workspace_data]
            path: string path where files will be placed
            org: string name of Github Organization where repo is placed
            kwargs: dict with other params that can be ued by cookiecutter method, e.g extra_context
        Returns:
            return a root path of creted file from template.
        """
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
        """Method to delete GH repository.
        
        Args:
            repo_obj: GH repo object to repository that will be deleted.
        Returns:
            Return 0 (int) if repopository will be deleted.
            If any issue appear, program will exit (sys exit) with status 1.
        """
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

