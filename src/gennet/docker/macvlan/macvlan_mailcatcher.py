from gennet.lib import misc
from gennet.docker.containers import mailcatcher
from gennet.docker.macvlan import macvlan_str
from gennet.docker import common


def create_start_str(container_name, net_list, smtp_port, http_port):
    [pre_str, netop, post_str] = macvlan_str.create_macvlan_prepost_str(net_list)
    preup_script = 'sh ${CURRENT}/stop.sh\n' + pre_str
    cmd = mailcatcher.create_start_cmd(smtp_port, http_port)
    container_macvlan_str = mailcatcher.create_start_str(container_name, netop, preup_script, cmd)
    container_macvlan_str += post_str
    return container_macvlan_str


def create_files(output_dir, container_name, net_list, item):
    http_port = 1080
    if 'http_port' in item:
        http_port = item['http_port']
    smtp_port = 1025
    if 'smtp_port' in item:
        smtp_port = item['smtp_port']
    cont_dir = f'{output_dir}/{container_name}'
    misc.prepare_clean_dir(cont_dir)
    file_list = [
        [f'{cont_dir}/start.sh', create_start_str(container_name, net_list, smtp_port, http_port)],
        [f'{cont_dir}/stop.sh', common.create_stop_sh_str(container_name)],
    ]

    misc.write_file_list(file_list)
    return container_name
