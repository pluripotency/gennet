from gennet.lib import misc
from gennet.docker import common


def create_dnsmasq_dockerfile_str():
    return misc.del_indent(f"""
    FROM alpine:edge
    RUN apk --no-cache add dnsmasq
    ENTRYPOINT ["dnsmasq", "-k"]
    """)


def create_dnsmasq_start_str(container_name, netop, preup_script, docker_cmd='', dns=None):
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
    IMAGE_NAME=alpine-dnsmasq
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


def create_start_sh_str(container_name):
    netop = '-p 53:53/udp'
    preup_script = common.create_build_and_stop_str()
    return create_dnsmasq_start_str(container_name, netop, preup_script)


def create_files():
    container_name = 'dnsmasq'
    cont_dir = f'/tmp/dnsmasq'
    misc.prepare_clean_dir(cont_dir)
    misc.prepare_clean_dir(cont_dir + '/conf')
    file_list = [
        [f'{cont_dir}/Dockerfile', create_dnsmasq_dockerfile_str()],
        [f'{cont_dir}/start.sh', create_start_sh_str(container_name)],
        [f'{cont_dir}/stop.sh', common.create_stop_sh_str(container_name)],
        [f'{cont_dir}/build.sh', common.create_build_sh_str('alpine-dnsmasq')],
        [f'{cont_dir}/conf/dnsmasq.conf', create_dnsmasq_conf_str()],
        [f'{cont_dir}/conf/resolv.conf', create_resolv_conf_str()],
        [f'{cont_dir}/conf/hosts', create_hosts_str()],
    ]
    misc.write_file_list(file_list)
    return cont_dir


