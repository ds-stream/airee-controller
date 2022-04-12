from airee_repos import Airee_gh_repo
import argparse

parser = argparse.ArgumentParser(description='Init Airee repos base on template')
parser.add_argument('-t', '--token', action='store', required=True)
parser.add_argument('-w', '--workspace', action='store', required=True)
parser.add_argument('-r', '--repo', action='store', choices=['app', 'workspace_data', 'infra', 'all'], required=True)
parser.add_argument('-e', '--env', action='store', choices=['prd', 'dev', 'uat'], required=False, default='dev')

args = vars(parser.parse_args())


airee = Airee_gh_repo(args['token'], args['workspace'], env=args['env'])
if args['repo'] == 'all':
    airee.create_repo_from_template('workspace_data', extra_context={'repo_name': 'workspace_data', 'env': args['env'], 'workspace': args['workspace'], 'org': airee.org}, default_config=True, overwrite_if_exists=True, no_input=True)
    airee.create_repo_from_template('app', extra_context={'repo_name': 'app', 'env': args['env'], 'workspace': args['workspace'], 'org': airee.org}, default_config=True, overwrite_if_exists=True, no_input=True)
    airee.create_repo_from_template('infra', extra_context={'repo_name': 'infra', 'env': args['env'], 'workspace': args['workspace'], 'org': airee.org}, default_config=True, overwrite_if_exists=True, no_input=True)    
else:
    airee.create_repo_from_template(args['repo'], extra_context={'repo_name': args['repo'], 'env': args['env'], 'workspace': args['workspace'], 'org': airee.org}, default_config=True, overwrite_if_exists=True, no_input=True)