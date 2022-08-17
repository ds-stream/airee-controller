"""Module with configuration.

Atributes:
    template: dict with names of cookiecutter templates git repositories, used in ariee_repos
    log_lvl: logging level
    ch: channel of logging
    formatter: logging formatter used in controller
"""
import logging

template = {
    'infra': 'template_infra_dev.git',
    'app': 'template_app_dev.git',
    'workspace_data': 'template_workspace_data_dev.git'
}

log_lvl = logging.DEBUG
ch = logging.StreamHandler()
ch.setLevel(log_lvl)
# create formatter
formatter = logging.Formatter('%(asctime)s - %(filename)s:%(lineno)s - %(funcName)s() - %(levelname)s - %(message)s')
# add formatter to ch
ch.setFormatter(formatter)