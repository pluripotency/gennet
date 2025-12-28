from gennet.lib import misc
from gennet.docker.containers import gw
from gennet.docker.macvlan import macvlan_str
from gennet.docker import common


def create_start_str(container_name, net_list):
    [pre_str, netop, post_str] = macvlan_str.create_macvlan_prepost_str(net_list, additional_scripts=[
        'sh ${CURRENT}/rules.sh',
        'iptables -nvL -t nat',
    ])
    preup_script = 'sh ${CURRENT}/stop.sh\n' + pre_str
    container_macvlan_str = gw.create_gw_start_str(container_name, netop, preup_script)
    container_macvlan_str += post_str
    return container_macvlan_str


def create_files(output_dir, container_name, net_list, item):
    rules = None
    if 'rules' in item:
        rules = item['rules']
    cont_dir = f'{output_dir}/{container_name}'
    misc.prepare_clean_dir(cont_dir)
    misc.prepare_clean_dir(f'{cont_dir}/conf')
    file_list = [
        [f'{cont_dir}/start.sh', create_start_str(container_name, net_list)],
        [f'{cont_dir}/stop.sh', common.create_stop_sh_str(container_name)],
        [f'{cont_dir}/rules.sh', gw.create_ipbales_str(rules)]
    ]

    misc.write_file_list(file_list)
    return container_name
