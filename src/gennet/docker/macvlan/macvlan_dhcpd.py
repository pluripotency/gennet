from gennet.lib import misc
from gennet.docker.containers import dhcpd
from gennet.docker.macvlan import macvlan_str
from gennet.docker import common


def create_start_str(container_name, net_list):
    [pre_str, netop, post_str] = macvlan_str.create_macvlan_prepost_str(net_list)
    preup_script = common.create_build_and_stop_str() + pre_str
    container_macvlan_str = dhcpd.create_dhcpd_start_str(container_name, netop, preup_script)
    container_macvlan_str += post_str
    return container_macvlan_str


def create_files(output_dir, container_name, net_list, item):
    subnets = None
    if 'subnets' in item:
        subnets = item['subnets']
    cont_dir = f'{output_dir}/{container_name}'
    misc.prepare_clean_dir(cont_dir)
    misc.prepare_clean_dir(f'{cont_dir}/conf')
    file_list = [
        [f'{cont_dir}/Dockerfile', dhcpd.create_dhcpd_dockerfile_str()],
        [f'{cont_dir}/build.sh', common.create_build_sh_str('alpine-dhcpd')],
        [f'{cont_dir}/start.sh', create_start_str(container_name, net_list)],
        [f'{cont_dir}/stop.sh', common.create_stop_sh_str(container_name)],
        [f'{cont_dir}/conf/dhcpd.conf', dhcpd.create_dhcpd_conf_str(subnets)],
        [f'{cont_dir}/conf/dhcpd.leases', ''],
    ]

    misc.write_file_list(file_list)
    return container_name
