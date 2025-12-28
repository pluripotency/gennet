from gennet.lib import misc
from gennet.docker import common
from gennet.docker.containers import ntpd
from gennet.docker.macvlan import macvlan_str


def create_start_str(container_name, net_list):
    [pre_str, netop, post_str] = macvlan_str.create_macvlan_prepost_str(net_list)
    preup_script = common.create_build_and_stop_str() + pre_str
    container_macvlan_str = ntpd.create_ntpd_start_str(container_name, netop, preup_script)
    container_macvlan_str += post_str
    return container_macvlan_str


def create_files(output_dir, container_name, net_list, item):
    servers = None
    if 'servers' in item:
        servers = item['servers']
    resolv_conf = None
    if 'resolv_conf' in item:
        resolv_conf = item['resolv_conf']
    cont_dir = f'{output_dir}/{container_name}'
    misc.prepare_clean_dir(cont_dir)
    misc.prepare_clean_dir(f'{cont_dir}/conf')

    file_list = [
        [f'{cont_dir}/Dockerfile', ntpd.create_ntpd_dockerfile_str()],
        [f'{cont_dir}/build.sh', common.create_build_sh_str('alpine-ntpd')],
        [f'{cont_dir}/start.sh', create_start_str(container_name, net_list)],
        [f'{cont_dir}/stop.sh', common.create_stop_sh_str(container_name)],
        [f'{cont_dir}/check.sh', ntpd.create_check_sh_str(container_name)],
        [f'{cont_dir}/conf/ntpd.conf', ntpd.create_ntpd_conf_str(servers)],
        [f'{cont_dir}/conf/resolv.conf', ntpd.create_resolv_conf_str(resolv_conf)],
    ]

    misc.write_file_list(file_list)
    return container_name


