from gennet.lib import misc
from gennet.docker.containers import dnsmasq
from gennet.docker.macvlan import macvlan_str
from gennet.docker import common


def create_start_str(container_name, net_list):
    [pre_str, netop, post_str] = macvlan_str.create_macvlan_prepost_str(net_list)
    preup_script = common.create_build_and_stop_str() + pre_str
    container_macvlan_str = dnsmasq.create_dnsmasq_start_str(container_name, netop, preup_script)
    container_macvlan_str += post_str
    return container_macvlan_str


def create_files(output_dir, container_name, net_list, item):
    hosts = None
    if 'hosts' in item:
        hosts = item['hosts']
    resolv_conf = None
    if 'resolv_conf' in item:
        resolv_conf = item['resolv_conf']
    cont_dir = f'{output_dir}/{container_name}'
    misc.prepare_clean_dir(cont_dir)
    misc.prepare_clean_dir(f'{cont_dir}/conf')
    file_list = [
        [f'{cont_dir}/Dockerfile', dnsmasq.create_dnsmasq_dockerfile_str()],
        [f'{cont_dir}/build.sh', common.create_build_sh_str('alpine-dnsmasq')],
        [f'{cont_dir}/start.sh', create_start_str(container_name, net_list)],
        [f'{cont_dir}/stop.sh', common.create_stop_sh_str(container_name)],
        [f'{cont_dir}/conf/dnsmasq.conf', dnsmasq.create_dnsmasq_conf_str()],
        [f'{cont_dir}/conf/resolv.conf', dnsmasq.create_resolv_conf_str(resolv_conf)],
        [f'{cont_dir}/conf/hosts', dnsmasq.create_hosts_str(hosts)],
    ]

    misc.write_file_list(file_list)
    return container_name
