from airee_repos import Airee_gh_repo
import argparse

parser = argparse.ArgumentParser(description='Init Airee repos base on template')
parser.add_argument('-t', '--token', action='store', required=True)
parser.add_argument('-w', '--workspace', action='store', required=True)
parser.add_argument('-r', '--repo', action='store', choices=['app', 'workspace_data', 'infra'], required=True)
parser.add_argument('-e', '--env', action='store', choices=['prd', 'dev', 'uat'], required=False, default='dev')

args = vars(parser.parse_args())


airee = Airee_gh_repo(args['token'], args['workspace'], env=args['env'])
airee.create_repo_from_template(args['repo'], extra_context={'repo_name': args['repo']}, default_config=True, overwrite_if_exists=True, no_input=True)