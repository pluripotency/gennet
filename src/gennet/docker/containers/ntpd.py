from gennet.lib import misc
from gennet.docker import common


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
    IMAGE_NAME=alpine-ntpd
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


def create_start_sh_str(container_name):
    netop = '-p 123:123/udp'
    preup_script = common.create_build_and_stop_str()
    return create_ntpd_start_str(container_name, netop, preup_script)


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


def create_ntpd_files():
    container_name = 'ntpd'
    output_dir = '/tmp/ntpd'
    misc.prepare_clean_dir(output_dir)
    misc.prepare_clean_dir(f'{output_dir}/conf')
    file_list = [
        [f'{output_dir}/Dockerfile', create_ntpd_dockerfile_str()],
        [f'{output_dir}/start.sh', create_start_sh_str(container_name)],
        [f'{output_dir}/stop.sh', common.create_stop_sh_str(container_name)],
        [f'{output_dir}/build.sh', common.create_build_sh_str('alpine-ntpd')],
        [f'{output_dir}/check.sh', create_check_sh_str(container_name)],
        [f'{output_dir}/conf/ntpd.conf', create_ntpd_conf_str()],
        [f'{output_dir}/conf/resolv.conf', create_resolv_conf_str()],
    ]
    misc.write_file_list(file_list)
    return output_dir
