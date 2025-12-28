from gennet.lib import misc
from gennet.docker.containers import mailcatcher
from gennet.docker.ovs_docker import ops


def create_run_container_str(http_port, smtp_port):
    """
    >>> print(create_run_container_str())

    """
    netop = '--net=none'
    cmd = mailcatcher.create_start_cmd(smtp_port, http_port, delay=True)
    preup_script = ''
    return mailcatcher.create_start_str('$1', netop, preup_script, cmd)


def create_files(output_dir, container_name, net_list, item):
    http_port = 1080
    if 'http_port' in item:
        http_port = item['http_port']
    smtp_port = 1025
    if 'smtp_port' in item:
        smtp_port = item['smtp_port']
    cont_dir = f'{output_dir}/{container_name}'
    file_list = [
        [f'{cont_dir}/run_container.sh', create_run_container_str(http_port, smtp_port)],
        [f'{cont_dir}/add_ovsnet.sh', ops.create_add_ovsnet_str(net_list)],
        [f'{cont_dir}/start.sh', ops.create_start_str(container_name)],
        [f'{cont_dir}/stop.sh', ops.create_stop_str(container_name)],
    ]
    misc.prepare_clean_dir(cont_dir)
    misc.write_file_list(file_list)
    return container_name

