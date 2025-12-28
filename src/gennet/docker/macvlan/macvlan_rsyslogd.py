from gennet.lib import misc
from gennet.docker.containers import rsyslog
from gennet.docker.macvlan import macvlan_str
from gennet.docker import common


def create_start_str(container_name, net_list):
    [pre_str, netop, post_str] = macvlan_str.create_macvlan_prepost_str(net_list)
    preup_script = common.create_build_and_stop_str() + pre_str
    container_macvlan_str = rsyslog.create_rsyslog_start_str(container_name, netop, preup_script)
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
        [f'{cont_dir}/Dockerfile', rsyslog.create_rsyslog_dockerfile_str()],
        [f'{cont_dir}/build.sh', common.create_build_sh_str('alpine-rsyslogd')],
        [f'{cont_dir}/start.sh', create_start_str(container_name, net_list)],
        [f'{cont_dir}/stop.sh', common.create_stop_sh_str(container_name)],
        [f'{cont_dir}/conf/rsyslog.conf', rsyslog.create_rsyslog_conf_str(rules)],
    ]

    misc.write_file_list(file_list)
    return container_name
