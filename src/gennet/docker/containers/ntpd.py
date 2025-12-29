from gennet.lib import misc
from gennet.docker import common
IMEAGE_NAME='alpine-ntpd'


def create_ntpd_dockerfile_str():
    return misc.del_indent("""
    FROM alpine:latest
    RUN apk add --no-cache openntpd
    ENTRYPOINT [ "/usr/sbin/ntpd", "-v", "-d", "-s" ]
    """)


def create_ntpd_start_str(container_name, netop, preup_script, docker_cmd='', dns=None):
    dns_str = '-v $CURRENT/conf/resolv.conf:/etc/resolv.conf:ro'
    if dns is not None:
        dns_entries = []
        for entry in dns.split(','):
            if misc.is_ipv4(entry):
                dns_entries += ['--dns ' + entry]
        dns_str = ' '.join(dns_entries)
    return misc.del_indent(f"""
    #! /bin/bash
    CURRENT=$(cd $(dirname $0);pwd)
    IMAGE_NAME={IMEAGE_NAME}
    CONTAINER_NAME={container_name}
    
    """) + preup_script + misc.del_indent(rf"""

    docker run -d {netop} \
        --name=$CONTAINER_NAME \
        --cap-add=SYS_NICE \
        --cap-add=SYS_RESOURCE \
        --cap-add=SYS_TIME \
        -v $CURRENT/conf/ntpd.conf:/etc/ntpd.conf:ro \
        {dns_str} \
        $IMAGE_NAME {docker_cmd}
    
    """)


def create_check_sh_str(container_name):
    return misc.del_indent(f"""
    #! /bin/bash
    CONTAINER_NAME={container_name}
    docker exec `docker ps -q -f name=^$CONTAINER_NAME$` ntpctl -s all
    """)


def create_ntpd_conf_str(servers=None):
    if servers is None:
        servers = misc.del_indent("""
    server ntp.nict.jp
    server ntp.jst.mfeed.ad.jp
    
    """)
    return misc.del_indent("""
    listen on *

    """) + servers


def create_resolv_conf_str(resolve_conf=None):
    if resolve_conf:
        return resolve_conf
    return misc.del_indent("""
    search local
    nameserver 8.8.8.8
    nameserver 8.8.4.4

    """)

def create_base_files(output_dir, container_name, item):
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
        [f'{cont_dir}/Dockerfile', create_ntpd_dockerfile_str()],
        [f'{cont_dir}/build.sh', common.create_build_sh_str(IMEAGE_NAME)],
        [f'{cont_dir}/stop.sh', common.create_stop_sh_str(container_name)],
        [f'{cont_dir}/check.sh', create_check_sh_str(container_name)],
        [f'{cont_dir}/conf/ntpd.conf', create_ntpd_conf_str(servers)],
        [f'{cont_dir}/conf/resolv.conf', create_resolv_conf_str(resolv_conf)],
    ]
    return cont_dir, file_list

def create_bridge_files(output_dir, container_name, net_list, item):
    cont_dir, file_list = create_base_files(output_dir, container_name, item)
    netop = '-p 123:123/udp'
    preup_script = common.create_build_and_stop_str()
    file_list += [
        [f'{cont_dir}/start.sh', create_ntpd_start_str(container_name, netop, preup_script)],
    ]
    misc.write_file_list(file_list)
    return container_name

def create_hostnet_files(output_dir, container_name, net_list, item):
    cont_dir, file_list = create_base_files(output_dir, container_name, item)
    netop = '--network=host'
    preup_script = common.create_build_and_stop_str()
    file_list += [
        [f'{cont_dir}/start.sh', create_ntpd_start_str(container_name, netop, preup_script)],
    ]
    misc.write_file_list(file_list)
    return container_name

def create_macvlan_start_str(container_name, net_list):
    from gennet.docker.macvlan import macvlan_str
    [pre_str, netop, post_str] = macvlan_str.create_macvlan_prepost_str(net_list)
    preup_script = common.create_build_and_stop_str() + pre_str
    container_macvlan_str = create_ntpd_start_str(container_name, netop, preup_script)
    container_macvlan_str += post_str
    return container_macvlan_str

def create_macvlan_files(output_dir, container_name, net_list, item):
    cont_dir, file_list = create_base_files(output_dir, container_name, item)
    file_list += [
        [f'{cont_dir}/start.sh', create_macvlan_start_str(container_name, net_list)],
    ]
    misc.write_file_list(file_list)
    return container_name


