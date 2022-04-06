import logging

template = {
    'infra': 'dsstream-airflowk8s_infra_dev.git',
    'app': 'dsstream-airflowk8s_app_dev.git',
    'workspace_data': 'dsstream-airflowk8s_workspace_data_dev.git'
}

log_lvl = logging.DEBUG
ch = logging.StreamHandler()
ch.setLevel(log_lvl)
# create formatter
formatter = logging.Formatter('%(asctime)s - %(filename)s:%(lineno)s - %(funcName)s() - %(levelname)s - %(message)s')
# add formatter to ch
ch.setFormatter(formatter)