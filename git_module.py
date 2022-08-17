"""Module to comunicate with git repositories.

It use mainly pygit2 frameworks.

    Typical usege:
    
    app_git = Gitrepo(ssh_url, priv_k, pub_k)
    app_git.clone_repo(path)
    # done some changes on files
    app_git.commit_all("Init commit")
    app_git.push()
"""
import pygit2
import logging
import config
from retry import retry

logger = logging.getLogger(__name__)
logger.setLevel(config.log_lvl)
logger.addHandler(config.ch)
logger.propagate = False

class Gitrepo:
    """Class to conect with git repository.

    Object of this class comunicate with git repository using ssh connecions with public and private key auth.
    There are methods to basic operation on git repository like commit, clone, push or add submodule.
    Some of methods are decorated with retry function to handle connections issues.

    Attributes:
        keypair: pygit2 keypair object contain public and private key for auth
        callbacks: pygit2 callback object to handle comunication with remote repository
        ssh_url: string with ssh's type url to repository
        prv_k: string byte encoded private key
        pub_k: string byte encoded public key
        repo: pygit repository object
    """
    def __init__(self, ssh_url, prv_k, pub_k):
        """Create Gitrepo object."""
        self.keypair = pygit2.KeypairFromMemory("git", pub_k.decode(), prv_k.decode(), "")
        self.callbacks = pygit2.RemoteCallbacks(credentials=self.keypair)
        self.ssh_url = self.__check_ssh_url(ssh_url)
        self.prv_k = prv_k
        self.pub_k = pub_k
        logger.debug(f"Gitrepo object for repo {ssh_url} created")


    def __check_ssh_url(self, url):
        """Method to validate url address match to ssh convention."""
        logger.debug(f"Checking if url is valid")
        if url.startswith("ssh://"):
            return url
        elif url.startswith("git@"):
            return f"ssh://{url.replace(':','/')}"
        else:
            logger.error("SSH url is not valid. Need start with 'ssh://' or 'git@'")
            raise

    @retry(tries=2, delay=20, backoff=2, logger=logger)
    def clone_repo(self, path):
        """Method to clone repository on provided path.
        It create attribute "repo".
        """
        self.repo = pygit2.clone_repository(self.ssh_url, path, callbacks=self.callbacks)
        self.repo.remotes.set_url("origin", self.ssh_url)
        logger.debug(f"Repo created on path {path}")
        return 0


    def commit_all(self, comment, author=["Init", "test@dsstream.com"], commiter=["Init", "test@dsstream.com"]):
        """Method to commit all changes in local repository.

        Args:
            comment: string with comment to commit
            author: list of two strings with name and email of changes author
            commiter: list of two strings with name and email of commiter
        Returns
            pygit2 commit object
        """
        auth = pygit2.Signature(*author)
        comm = pygit2.Signature(*commiter)
        index = self.repo.index
        index.add_all()
        logger.debug(f"Added all changes to commit")
        index.write()
        tree = index.write_tree()
        commit_obj = self.repo.create_commit('refs/heads/main', auth, comm, comment, tree, [self.repo.head.target])
        logger.debug(f"Commited")
        return commit_obj

    @retry(tries=2, delay=20, backoff=2, logger=logger)
    def push(self, branch=['refs/heads/main']):
        """Method push all commited changes to remote.

        Args:
            branch: list of strings with branches name where changes will be pushed. Default value main (refs/heads/main)
        """
        remote = self.repo.remotes["origin"]
        remote.push(branch, callbacks=self.callbacks)
        logger.debug(f"Pushed")
        return 0


    @retry(tries=2, delay=20, backoff=2, logger=logger)
    def add_submodule(self, git_repo, path):
        """Method to add submodule.

        Args:
            git_repo: pygit2 repository object to submodule repository
            path: string with path where submodule will be placed
        """
        self.repo.add_submodule(git_repo.ssh_url, path, callbacks=git_repo.callbacks)
        logger.debug(f"Submodule added")
        return 0