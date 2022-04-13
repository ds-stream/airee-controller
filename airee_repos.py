""""""
from email import message
from email.policy import default
from github import Github
from github.GithubException import GithubException
import pygit2
from pair_key import PairKey
import config, secrets
from cookiecutter.main import cookiecutter
from os.path import join as path_join 
import sys
import logging

logger = logging.getLogger(__name__)
logger.setLevel(config.log_lvl)
logger.addHandler(config.ch)

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

    def __repo_naming(self, type):
        """return name in order to naming convention."""
        return f'{self.workspace}_{type}_{self.env}'

    def __create_repo(self, name, private=True, **kwargs):
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
    
    def __get_tmp_path(self, type):
        """Method generate path in /tmp/ with random sufix"""
        random_dir_sufix = secrets.token_urlsafe(10)
        return f'/tmp/{type}{random_dir_sufix}'

    def create_empty_repo_gh(self, type):
        """Init repo for Airee.
        Params:
        type [str] Value from list [infra, app, workspace_data]
        Return: repository pygithub object
        """
        name = self.__repo_naming(type)
        return self.__create_repo(name)
    
    def get_airee_repo(self, type):
        """Get repo object by airee name"""
        name = self.__repo_naming(type)
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

    def generate_from_template(self, type, path, org=None, **kwargs):
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

    def create_repo_from_template(self, type, **kwargs):
        # create repo
        name = self.__repo_naming(type)
        logger.info(f"Create repo '{name}' for workspace {self.workspace}")
        repo_gh = self.__create_repo(name, auto_init=True)
        # repo_gh = self.get_airee_repo(type)
        # repo_gh.create_file("README.md", "init commit", """readmeText""")
        # create deploy-key for init push
        logger.info(f"Added Deploy Key")
        priv_k, pub_k, dk = self.set_deploy_key('init_push', repo_gh, False)
        # Add secret for infra repo
        if type in ('infra', 'app'):
            logger.info(f"Adding secret TF_VAR_github_token")
            self.set_secret(repo_gh, "TF_VAR_github_token", self.token)
        # create tmp path
        path = self.__get_tmp_path(type)
        # change to logging
        logger.debug(f"Path to tmp folder: {path_join(path, type)}")
        logger.debug(f"Url to repo : {repo_gh.git_url}")
        keypair = pygit2.KeypairFromMemory("git", pub_k.decode(), priv_k.decode(), "")
        callbacks = pygit2.RemoteCallbacks(credentials=keypair)
        repoClone= pygit2.clone_repository(f"ssh://{repo_gh.ssh_url.replace(':','/')}", path_join(path, type), callbacks=callbacks)

        # copy files from template
        logger.info(f"Generating repo from template")
        # path + 'repo_name' subfolder. 'repo_name' varialbe from cookicuterr -> name placed in extra_context in kwargs
        self.generate_from_template(type, path, **kwargs)

        # add files, commit and push
        logger.info(f"Pushing files to new repo")
        repoClone.remotes.set_url("origin", f"ssh://{repo_gh.ssh_url.replace(':','/')}")
        index = repoClone.index
        index.add_all()
        index.write()
        author = pygit2.Signature("Init", "test@dsstream.com")
        commiter = pygit2.Signature("Init", "test@dsstream.com")
        tree = index.write_tree()
        oid = repoClone.create_commit('refs/heads/main', author, commiter, "init commit",tree,[repoClone.head.target])
        remote = repoClone.remotes["origin"]

        remote.push(['refs/heads/main'],callbacks=callbacks)
        logger.info(f"Repo ready!")

        return 0
