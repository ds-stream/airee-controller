""""""
import pygit2
import logging
import config

logger = logging.getLogger(__name__)
logger.setLevel(config.log_lvl)
logger.addHandler(config.ch)
logger.propagate = False

class Gitrepo:
    def __init__(self, ssh_url, prv_k, pub_k):
        self.keypair = pygit2.KeypairFromMemory("git", pub_k.decode(), prv_k.decode(), "")
        self.callbacks = pygit2.RemoteCallbacks(credentials=self.keypair)
        self.ssh_url = self.__check_ssh_url(ssh_url)
        self.prv_k = prv_k
        self.pub_k = pub_k
        logger.debug(f"Gitrepo object for repo {ssh_url} created")


    def __check_ssh_url(self, url):
        """"""
        logger.debug(f"Checking if url is valid")
        if url.startswith("ssh://"):
            return url
        elif url.startswith("git@"):
            return f"ssh://{url.replace(':','/')}"
        else:
            logger.error("SSH url is not valid. Need start with 'ssh://' or 'git@'")
            raise


    def clone_repo(self, path):
        self.repo = pygit2.clone_repository(self.ssh_url, path, callbacks=self.callbacks)
        self.repo.remotes.set_url("origin", self.ssh_url)
        logger.debug(f"Repo created on path {path}")
        return 0


    def commit_all(self, comment, author=["Init", "test@dsstream.com"], commiter=["Init", "test@dsstream.com"]):
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

    
    def push(self, branch=['refs/heads/main']):
        remote = self.repo.remotes["origin"]
        remote.push(['refs/heads/main'],callbacks=self.callbacks)
        logger.debug(f"Pushed")
        return 0



    def add_submodule(self, git_repo, path):
        self.repo.add_submodule(git_repo.ssh_url, path, callbacks=git_repo.callbacks)
        logger.debug(f"Submodule added")
        return 0