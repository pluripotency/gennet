from gennet.lib import misc
from gennet.docker import common
IMAGE_NAME='alpine-dnsmasq'

def create_dnsmasq_dockerfile_str():
    return misc.del_indent(f"""
    FROM alpine:edge
    RUN apk --no-cache add dnsmasq
    ENTRYPOINT ["dnsmasq", "-k"]
    """)

def create_start_str(container_name, netop, preup_script, docker_cmd='', dns=None):
    dns_str = '-v $CURRENT/conf/resolv.conf:/etc/resolv.conf:ro'
    if dns is not None:
        dns_entries = []
        for entry in dns.split(','):
            if misc.is_ipv4(entry):
                dns_entries += ['--dns ' + entry]
        dns_str = ' '.join(dns_entries)
    start_sh_str = misc.del_indent(f"""
    #! /bin/bash
    CURRENT=$(cd $(dirname $0);pwd)
    IMAGE_NAME={IMAGE_NAME}
    CONTAINER_NAME={container_name}
    
    """)
    start_sh_str += preup_script
    start_sh_str += misc.del_indent(rf"""

    docker run -d {netop} \
        --name=$CONTAINER_NAME \
        --cap-add=NET_ADMIN \
        -v $CURRENT/conf/hosts:/etc/hosts:ro \
        -v $CURRENT/conf/dnsmasq.conf:/etc/dnsmasq.conf:ro \
        {dns_str} \
        $IMAGE_NAME {docker_cmd}
    
    """)
    return start_sh_str

def create_dnsmasq_conf_str():
    return misc.del_indent("""
    #local-service

    """)

def create_hosts_str(hosts=None):
    if hosts:
        return hosts
    else:
        return misc.del_indent("""
    127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4
    ::1         localhost localhost.localdomain localhost6 localhost6.localdomain6
    
    """)

def create_resolv_conf_str(resolve_conf=None):
    if resolve_conf:
        return resolve_conf
    else:
        return misc.del_indent("""
    search local
    nameserver 8.8.8.8
    nameserver 8.8.4.4

    """)

def create_base_files(output_dir, container_name, item):
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
        [f'{cont_dir}/Dockerfile', create_dnsmasq_dockerfile_str()],
        [f'{cont_dir}/build.sh', common.create_build_sh_str(IMAGE_NAME)],
        [f'{cont_dir}/stop.sh', common.create_stop_sh_str(container_name)],
        [f'{cont_dir}/conf/dnsmasq.conf', create_dnsmasq_conf_str()],
        [f'{cont_dir}/conf/resolv.conf', create_resolv_conf_str(resolv_conf)],
        [f'{cont_dir}/conf/hosts', create_hosts_str(hosts)],
    ]
    return cont_dir, file_list

def create_bridge_files(output_dir, container_name, net_list, item):
    cont_dir, file_list = create_base_files(output_dir, container_name, item)
    netop = '-p 53:53/udp'
    preup_script = common.create_build_and_stop_str()
    file_list += [
        [f'{cont_dir}/start.sh', create_start_str(container_name, netop, preup_script)],
    ]
    misc.write_file_list(file_list)
    return container_name

def create_hostnet_files(output_dir, container_name, net_list, item):
    cont_dir, file_list = create_base_files(output_dir, container_name, item)
    netop = '--network=host'
    preup_script = common.create_build_and_stop_str()
    file_list += [
        [f'{cont_dir}/start.sh', create_start_str(container_name, netop, preup_script)],
    ]
    misc.write_file_list(file_list)
    return container_name


def create_macvlan_start_str(container_name, net_list):
    from gennet.docker.macvlan import macvlan_str
    [pre_str, netop, post_str] = macvlan_str.create_macvlan_prepost_str(net_list)
    preup_script = common.create_build_and_stop_str() + pre_str
    container_macvlan_str = dnsmasq.create_dnsmasq_start_str(container_name, netop, preup_script)
    container_macvlan_str += post_str
    return container_macvlan_str

def create_macvlan_files(output_dir, container_name, net_list, item):
    cont_dir, file_list = create_base_files(output_dir, container_name, item)
    file_list += [
        [f'{cont_dir}/start.sh', create_macvlan_start_str(container_name, net_list)],
    ]
    misc.write_file_list(file_list)
    return container_name
