from gennet.lib import misc
from gennet.docker import common
from gennet.docker.containers import tftpd
from gennet.docker.macvlan import macvlan_str


def create_start_str(container_name, net_list):
    [pre_str, netop, post_str] = macvlan_str.create_macvlan_prepost_str(net_list)
    preup_script = common.create_build_and_stop_str() + pre_str
    tftpd_macvlan_str = tftpd.create_tftpd_start_str(container_name, netop, preup_script)
    tftpd_macvlan_str += post_str
    return tftpd_macvlan_str


def create_files(output_dir, container_name, net_list):
    cont_dir = f'{output_dir}/{container_name}'

    file_list = [
        [f'{cont_dir}/Dockerfile', tftpd.create_tftpd_dockerfile_str()],
        [f'{cont_dir}/build.sh', common.create_build_sh_str('tftpd')],
        [f'{cont_dir}/start.sh', create_start_str(container_name, net_list)],
        [f'{cont_dir}/stop.sh', common.create_stop_sh_str(container_name)],
    ]

    misc.prepare_clean_dir(cont_dir)
    misc.write_file_list(file_list)
    return container_name
