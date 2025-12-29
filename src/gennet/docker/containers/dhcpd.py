from gennet.lib import misc
from gennet.docker import common
IMAGE_NAME='alpine-dhcpd'
dhcpd_cmd = ["/usr/sbin/dhcpd", "-4", "-f", "-d", "--no-pid", "-cf", "/etc/dhcp/dhcpd.conf", "-lf", "/var/lib/dhcp/dhcpd.leases" ]


def create_cmd_as_dockerfile_cmd():
    return '[' + ', '.join([f'"{item}"' for item in dhcpd_cmd]) + ']'


def create_cmd_as_delayed_cmd_arg():
    return '/bin/sh -c "sleep 2 && ' + ' '.join(dhcpd_cmd) + '"'


def create_dhcpd_dockerfile_str():
    return misc.del_indent(f"""
    FROM alpine:3.12
    RUN apk add --no-cache dhcp
    RUN ["touch", "/var/lib/dhcp/dhcpd.leases"]
    CMD {create_cmd_as_dockerfile_cmd()}
    """)


def create_dhcpd_start_str(container_name, netop, preup_script, docker_cmd=''):

    return misc.del_indent(f"""
    #! /bin/bash
    CURRENT=$(cd $(dirname $0);pwd)
    IMAGE_NAME={IMAGE_NAME}
    CONTAINER_NAME={container_name}
    
    """) + preup_script + misc.del_indent(rf"""

    docker run -d {netop} \
        --name=$CONTAINER_NAME \
        -v $CURRENT/conf/dhcpd.conf:/etc/dhcp/dhcpd.conf:ro \
        $IMAGE_NAME {docker_cmd}
    
    """)


def create_start_sh_str(container_name):
    netop = '-p 67:67/udp'
    preup_script = common.create_build_and_stop_str()
    return create_dhcpd_start_str(container_name, netop, preup_script)


def create_subnet_str(seg_pre, netmask, range_start, range_end, nameservers):
    """
    >>> print(create_subnet_str('192.168.202', '255.255.255.0', 200, 250, '8.8.8.8, 8.8.4.4'))
    subnet 192.168.202.0 netmask 255.255.255.0 {
        option routers 192.168.202.254;
        option subnet-mask 255.255.255.0;
        range 192.168.202.200 192.168.202.250;
        option broadcast-address 192.168.202.255;
        option domain-name-servers 8.8.8.8, 8.8.4.4;
        option domain-name "local";
        option domain-search "local";
    }
    <BLANKLINE>
    """
    return misc.del_indent(f"""
    subnet {seg_pre}.0 netmask {netmask} {{
        option routers {seg_pre}.254;
        option subnet-mask {netmask};
        range {seg_pre}.{range_start} {seg_pre}.{range_end};
        option broadcast-address {seg_pre}.255;
        option domain-name-servers {nameservers};
        option domain-name "local";
        option domain-search "local";
    }}
    
    """)


def create_dhcpd_conf_str(subnet=None):
    if subnet is None:
        seg_pre = '192.168.0'
        netmask = '255.255.255.0'
        range_start = 200
        range_end = 250
        nameservers = '8.8.8.8, 8.8.4.4'

        subnet = create_subnet_str(seg_pre, netmask, range_start, range_end, nameservers)

    return misc.del_indent(f"""
    authoritative;

    default-lease-time 7200;
    max-lease-time 7200;
    
    lease-file-name "/var/lib/dhcp/dhcpd.leases";
    


    """) + subnet

def create_base_files(output_dir, container_name, item):
    subnets = None
    if 'subnets' in item:
        subnets = item['subnets']
    cont_dir = f'{output_dir}/{container_name}'
    misc.prepare_clean_dir(cont_dir)
    misc.prepare_clean_dir(f'{cont_dir}/conf')
    file_list = [
        [f'{cont_dir}/Dockerfile', create_dhcpd_dockerfile_str()],
        [f'{cont_dir}/build.sh', common.create_build_sh_str(IMAGE_NAME)],
        [f'{cont_dir}/stop.sh', common.create_stop_sh_str(container_name)],
        [f'{cont_dir}/conf/dhcpd.conf', create_dhcpd_conf_str(subnets)],
        [f'{cont_dir}/conf/dhcpd.leases', ''],
    ]
    return cont_dir, file_list

def create_bridge_files(output_dir, container_name, net_list, item):
    cont_dir, file_list = create_base_files(output_dir, container_name, item)
    netop = '-p 67:67/udp'
    preup_script = common.create_build_and_stop_str()
    file_list += [
        [f'{cont_dir}/start.sh', create_dhcpd_start_str(container_name, netop, preup_script)],
    ]
    misc.write_file_list(file_list)
    return container_name

def create_hostnet_files(output_dir, container_name, net_list, item):
    cont_dir, file_list = create_base_files(output_dir, container_name, item)
    netop = '--network=host'
    preup_script = common.create_build_and_stop_str()
    file_list += [
        [f'{cont_dir}/start.sh', create_dhcpd_start_str(container_name, netop, preup_script)],
    ]
    misc.write_file_list(file_list)
    return container_name

def create_macvlan_start_str(container_name, net_list):
    from gennet.docker.macvlan import macvlan_str
    [pre_str, netop, post_str] = macvlan_str.create_macvlan_prepost_str(net_list)
    preup_script = common.create_build_and_stop_str() + pre_str
    container_macvlan_str = dhcpd.create_dhcpd_start_str(container_name, netop, preup_script)
    container_macvlan_str += post_str
    return container_macvlan_str

def create_macvlan_files(output_dir, container_name, net_list, item):
    cont_dir, file_list = create_base_files(output_dir, container_name, item)
    file_list += [
        [f'{cont_dir}/start.sh', create_macvlan_start_str(container_name, net_list)],
    ]
    misc.write_file_list(file_list)
    return container_name
