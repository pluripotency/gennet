import sys
import json
from gennet.lib import misc
from gennet.docker import common
IMAGE_NAME='alpine-kea-dhcpd'


def create_dockerfile_str():
    return misc.del_indent("""
    FROM alpine:latest

    ENV DHCP4_SERVER=true
    ENV DHCP6_SERVER=false

    RUN apk --no-cache add kea bash tzdata

    COPY kea.sh /etc/kea/

    EXPOSE 67 68

    CMD ["/bin/bash", "/etc/kea/kea.sh"]

    """)

def create_kea_sh_str():
    return misc.del_indent("""
    #!/bin/bash

    # turn on bash's job control
    set -m

    # As of KEA 1.7.x it needs this directory to run
    mkdir /run/kea

    if [ "$DHCP4_SERVER" = "true" ]
    then
      /usr/sbin/kea-dhcp4 -c /etc/kea/kea-dhcp4.conf &
    fi

    if [ "$DHCP6_SERVER" = "true" ]
    then
      /usr/sbin/kea-dhcp6 -c /etc/kea/kea-dhcp6.conf &
    fi

    # now we bring the primary process back into the foreground
    # and leave it there
    fg %1
    """)


def create_start_str(container_name, netop, preup_script):
    return misc.del_indent(f"""
    #! /bin/bash
    CURRENT=$(cd $(dirname $0);pwd)
    IMAGE_NAME={IMAGE_NAME}
    CONTAINER_NAME={container_name}
    
    """) + preup_script + misc.del_indent(rf"""

    docker run -d {netop} \
        --name=$CONTAINER_NAME \
        -e DHCP4_SERVER:true \
        -e DHCP6_SERVER:false \
        -e TZ:Asia/Tokyo \
        -v $CURRENT/kea-dhcp4.conf:/etc/kea/kea-dhcp4.conf:ro \
        -v $CURRENT/kea-dhcp6.conf:/etc/kea/kea-dhcp6.conf:ro \
        -v $CURRENT/leases:/var/lib/kea:rw \
        $IMAGE_NAME
    
    """)


def create_build_str():
    return common.create_build_sh_str(IMAGE_NAME)


def create_start_port67_str(container_name):
    netop = '-p 67:67/udp'
    preup_script = common.create_build_and_stop_str()
    return create_start_str(container_name, netop, preup_script)


def create_dhcp6_conf_str():
    return misc.del_indent("""
    {
    # DHCPv6 configuration starts on the next line
    "Dhcp6": {

    # First we set up global values
        "valid-lifetime": 4000,
        "renew-timer": 1000,
        "rebind-timer": 2000,
        "preferred-lifetime": 3000,

    # Next we set up the interfaces to be used by the server.
        "interfaces-config": {
            "interfaces": [ "eth0" ]
        },

    # And we specify the type of lease database
        "lease-database": {
            "type": "memfile",
            "persist": true,
            "name": "/var/lib/kea/dhcp6.leases"
        },

    # Finally, we list the subnets from which we will be leasing addresses.
        "subnet6": [
            {
                "subnet": "2001:db8:1::/64",
                "pools": [
                     {
                         "pool": "2001:db8:1::1-2001:db8:1::ffff"
                     }
                 ]
            }
        ]
    # DHCPv6 configuration ends with the next line
    }
    }
    """)

def create_dhcp4_conf_str(dhcp4_list=None):
    if dhcp4_list is None:
        return misc.del_indent("""
        {
        # DHCPv4 configuration starts on the next line
        "Dhcp4": {
            # First we set up global values
            "valid-lifetime": 4000,
            "renew-timer": 1000,
            "rebind-timer": 2000,

            # Next we set up the interfaces to be used by the server.
            "interfaces-config": {
                "interfaces": [ "eth0" ]
            },

            # And we specify the type of lease database
            "lease-database": {
                "type": "memfile",
                "persist": true,
                "name": "/var/lib/kea/kea-leases4.csv",
                "lfc-interval": 1800,
                "max-row-errors": 100
            },

            # Finally, we list the subnets from which we will be leasing addresses.
            "subnet4": [
                {
                    "id", 1,
                    "subnet": "192.168.1.0/24",
                    "pools": [
                        {
                             "pool": "192.168.1.50 - 192.168.1.200"
                        }
                    ],
                    "option-data": [
                        {
                            "name": "routers",
                            "data": "192.168.1.254"
                        },
                        {
                            "name": "domain-name-servers",
                            "data": "8.8.8.8, 8.8.4.4"
                        }
                    ]
                }
            ]
            # DHCPv4 configuration ends with the next line
        }
        }
        """)
    # dhcp4 is list
    interfaces = []
    subnet4_list = []
    for num, dhcp4 in enumerate(dhcp4_list):
        errors = []
        required_attrs = ['iface', 'subnet', 'range']
        for attr in required_attrs:
            if attr not in dhcp4:
                errors.append(attr)
        if len(errors) > 0:
            print(misc.ansi_colors.red(f'kea-dhcp4.conf require at least {" ".join(required_attrs)}, you need {" ".join(errors)} in index:{num}'))
            sys.exit(1)
        interfaces.append(dhcp4['iface'])
        subnet4_dict = {
            "id": num + 1,
            "subnet": dhcp4['subnet'],
            "pools": [
                {
                     "pool": dhcp4['range']
                }
            ],
        }
        if 'gateway' in dhcp4 or 'dns' in dhcp4:
            option_list = []
            if 'gateway' in dhcp4:
                option_list.append({
                    "name": "routers",
                    "data": dhcp4['gateway']
                })
            if 'dns' in dhcp4:
                option_list.append({
                    "name": "domain-name-servers",
                    "data": dhcp4['dns']
                })
            subnet4_dict['option-data'] = option_list
        subnet4_list.append(subnet4_dict)
    dhcp4_dict = {
        "Dhcp4": {
            "valid-lifetime": 4000,
            "renew-timer": 1000,
            "rebind-timer": 2000,
            "interfaces-config": {
                "interfaces": interfaces
            },
            "lease-database": {
                "type": "memfile",
                "persist": True,
                "name": "/var/lib/kea/kea-leases4.csv",
                "lfc-interval": 1800,
                "max-row-errors": 100
            },
            "subnet4": subnet4_list
        }
    }
    return json.dumps(dhcp4_dict, indent=2)

def create_base_files(output_dir, container_name, item):
    dhcp4 = None
    if 'dhcp4' in item:
        dhcp4 = item['dhcp4']
    cont_dir = f'{output_dir}/{container_name}'
    misc.prepare_clean_dir(cont_dir)
    misc.prepare_clean_dir(f'{cont_dir}/leases')
    file_list = [
        [f'{cont_dir}/Dockerfile', create_dockerfile_str()],
        [f'{cont_dir}/kea.sh', create_kea_sh_str()],
        [f'{cont_dir}/build.sh', create_build_str()],
        [f'{cont_dir}/kea-dhcp4.conf', create_dhcp4_conf_str(dhcp4)],
        [f'{cont_dir}/kea-dhcp6.conf', create_dhcp6_conf_str()],
        [f'{cont_dir}/stop.sh', common.create_stop_sh_str(container_name)],
    ]
    return cont_dir, file_list

def create_bridge_files(output_dir, container_name, net_list, item):
    cont_dir, file_list = create_base_files(output_dir, container_name, item)
    netop = '-p 67:67/udp'
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
    container_macvlan_str = create_start_str(container_name, netop, preup_script)
    container_macvlan_str += post_str
    return container_macvlan_str

def create_macvlan_files(output_dir, container_name, net_list, item):
    cont_dir, file_list = create_base_files(output_dir, container_name, item)
    file_list += [
        [f'{cont_dir}/start.sh', create_macvlan_start_str(container_name, net_list)],
    ]
    misc.write_file_list(file_list)
    return container_name
