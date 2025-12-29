import sys
from gennet.lib import misc
from gennet.lib.ansi_colors import red


ex_iface_list = [
    {
        'phyif': 'eth0',
        'subnet': '10.30.0.0/24',
        'gateway': '10.30.0.1',
        'vlan_list': [
            {
                'vlanid': 202,
                'subnet': '192.168.202.0/24',
                'gateway': '192.168.202.254', 
            }

        ]
    }
]
ex_translated_macvlan_list = [
    {
        'macvlan_name': 'native',
        'macvlan_iface': 'eth0',
        'subnet': '10.30.0.0/24',
        'gateway': '10.30.0.1',
    },
    {
        'macvlan_name': 'v0202',
        'macvlan_iface': 'eth0.202',
        'subnet': '192.168.202.0/24',
        'gateway': '192.168.202.254', 
    }

]


def extract_network(macvlan_name, item, macvlan_iface):
    if 'subnet' in item:
        subnet = item['subnet']
        if not misc.is_ipv4_with_prefix(subnet):
            print(red(f'invalid subnet format: {subnet} in {macvlan_name}'), flush=True)
            sys.exit(1)
        network = {
            'macvlan_name': macvlan_name,
            'macvlan_iface': macvlan_iface,
            'subnet': subnet
        }
        if 'gateway' in item:
            gateway = item['gateway']
            if not misc.is_ipv4(gateway):
                print(red(f'invalid gateway format: {gateway} in {macvlan_name}'), flush=True)
                sys.exit(1)
            network['gateway'] = gateway
        return network
    return False


def extract_macvlan_list(iface_list):
    macvlan_net_list = []
    for item in iface_list:
        if not 'phyif' in item:
            print(red('phyif is needed in iface'), flush=True)
            sys.exit(1)
        phyif = item['phyif']
        network = extract_network('native', item, phyif)
        if network:
            macvlan_net_list.append(network)
        if 'vlan' in item and isinstance(item['vlan'], list):
            for vlan in item['vlan']:
                if 'vlanid' in vlan:
                    vlanid = vlan['vlanid']
                    if not isinstance(vlanid, int) or not 1 < vlanid < 4095:
                        print(red(f'invalid vlanid: {vlanid}'), flush=True)
                        sys.exit(1)

                    macvlan_name = 'v' + f'000{vlanid}'[-4:]
                    macvlan_iface = phyif + f'.{vlanid}'
                    network = extract_network(macvlan_name, vlan, macvlan_iface)
                    if network:
                        macvlan_net_list.append(network)

    return macvlan_net_list


def create_start_stop_all(outdir_path, container_name_list):
    start_all_str = misc.del_indent("""
    #! /bin/bash
    CURRENT=$(cd $(dirname $0);pwd)
    docker network ls | grep macvlan | awk '{print $2}' | xargs -I{} docker network rm {}

    """)
    stop_all_str = misc.del_indent("""
    #! /bin/bash
    CURRENT=$(cd $(dirname $0);pwd)
    
    """)
    for container_name in container_name_list:
        start_all_str += f"bash $CURRENT/{container_name}/start.sh\n"
        stop_all_str += f"bash $CURRENT/{container_name}/stop.sh\n"
    stop_all_str += "docker network ls | grep macvlan | awk '{print $2}' | xargs -I{} docker network rm {}\n"
    return [
        [f'{outdir_path}/start.sh', start_all_str],
        [f'{outdir_path}/stop.sh', stop_all_str],
    ]


def generate_container_scripts(outdir_path, cont_type, container_name, net_list, item):
    if cont_type == 'tftpd':
        from gennet.docker.containers import tftpd
        return tftpd.create_macvlan_files(outdir_path, container_name, net_list)
    elif cont_type == 'dhcpd':
        from gennet.docker.containers import dhcpd
        return dhcpd.create_macvlan_files(outdir_path, container_name, net_list, item)
    elif cont_type == 'kea-dhcpd':
        from gennet.docker.containers import kea_dhcpd
        return kea_dhcpd.create_macvlan_files(outdir_path, container_name, net_list, item)
    elif cont_type == 'gw':
        from gennet.docker.containers import gw
        return gw.create_macvlan_files(outdir_path, container_name, net_list, item)
    elif cont_type == 'ntpd':
        from gennet.docker.containers import ntpd
        return ntpd.create_macvlan_files(outdir_path, container_name, net_list, item)
    elif cont_type == 'rsyslogd':
        from gennet.docker.containers import rsyslog
        return rsyslog.create_macvlan_files(outdir_path, container_name, net_list, item)
    elif cont_type == 'dnsmasq':
        from gennet.docker.containers import dnsmasq
        return dnsmasq.create_macvlan_files(outdir_path, container_name, net_list, item)
    elif cont_type == 'mailcatcher':
        from gennet.docker.containers import mailcatcher
        return mailcatcher.create_macvlan_files(outdir_path, container_name, net_list, item)
    elif cont_type == 'radiusd':
        from gennet.docker.containers import radiusd
        return radiusd.create_macvlan_files(outdir_path, container_name, net_list, item)
    else:
        print(red(f'no such container type: {cont_type}'), flush=True)
        sys.exit(1)


def find_net(network_list, ip):
    for network in network_list:
        subnet = network['subnet']
        if misc.is_ip_in_network(subnet, ip):
            return network
    return False


def generate_scripts(outdir_path, macvlan_params):
    iface_list = macvlan_params['iface']
    container_list = macvlan_params['container']
    macvlan_net_list = extract_macvlan_list(iface_list)
    misc.prepare_clean_dir(outdir_path)
    container_name_list = []
    file_list = []
    for item in container_list:
        if 'container_name' in item:
            container_name = item['container_name']
        else:
            print(red(r'container_name is required:\n' + misc.json.dumps(item, indent=2)), flush=True)
            sys.exit(1)
        if 'type' in item:
            cont_type = item['type']
        else:
            print(red(r'container type is required:\n' + misc.json.dumps(item, indent=2)), flush=True)
            sys.exit(1)
        if not 'net' in item:
            print(red(r'container.net is required:' + misc.json.dumps(item, indent=2)), flush=True)
            sys.exit(1)
        net_list = []
        for net in item['net']:
            ip = net['ip']
            if not misc.is_ipv4(ip):
                print(red(f'invalid ipv4: {ip}'), flush=True)
                sys.exit(1)
            found_net = find_net(macvlan_net_list, ip)
            if found_net:
                net_list.append(misc.concat_dict([found_net, {
                    'ip': ip,
                }]))
            else:
                print(red(f'no such network for ip: {ip}'), flush=True)
                sys.exit(1)
        created_container_name = generate_container_scripts(outdir_path, cont_type, container_name, net_list, item)
        if created_container_name:
            container_name_list.append(created_container_name)
    file_list += create_start_stop_all(outdir_path , container_name_list)
    misc.write_file_list(file_list)
