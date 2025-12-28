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
ex_translated_iface_list = [
    {
        'ovsbr': 'br0',
        'phyif': 'eth0',
        'subnet': '10.30.0.0/24',
        'gateway': '10.30.0.1',
        'vlan_list': [
            {
                'ovsbr': 'br0.0202',
                'vlanid': 202,
                'subnet': '192.168.202.0/24',
                'gateway': '192.168.202.254', 
            }
        ]
    }
]
ex_translated_ovs_net_list = [
    {
        'ovsbr': 'br0',
        'subnet': '10.30.0.0/24',
        'gateway': '10.30.0.1',
    },
    {
        'ovsbr': 'br0.0202',
        'subnet': '192.168.202.0/24',
        'gateway': '192.168.202.254', 
    }
]


def extract_network(ovsbr, item):
    if 'subnet' in item:
        subnet = item['subnet']
        if not misc.is_ipv4_with_prefix(subnet):
            print(red(f'invalid subnet format: {subnet} in {ovsbr}'), flush=True)
            sys.exit(1)
        network = {
            'ovsbr': ovsbr,
            'subnet': subnet
        }
        if 'gateway' in item:
            gateway = item['gateway']
            if not misc.is_ipv4(gateway):
                print(red(f'invalid gateway format: {gateway} in {ovsbr}'), flush=True)
                sys.exit(1)
            network['gateway'] = gateway
        return network
    return False


def create_ovs_str(iface_list):
    ovs_add_str = "#! /bin/bash\n"
    ovs_del_str = misc.del_indent("""
    #! /bin/bash
    CURRENT=$(cd $(dirname $0);pwd)
    $CURRENT/stop.sh

    """)
    ovs_net_list = []
    for index, iface in enumerate(iface_list):
        ovsbr = f'br{index}'
        ovs_add_str += f'sudo ovs-vsctl add-br {ovsbr}\n'
        ovs_del_str += f'sudo ovs-vsctl del-br {ovsbr}\n'
        if 'phyif' in iface:
            ovsport = iface['phyif']
            ovs_add_str += f'sudo nmcli con up {ovsport}\n'
            ovs_add_str += f'sudo ovs-vsctl add-port {ovsbr} {ovsport}\n'
            ovs_del_str += f'sudo nmcli con down {ovsport}\n'
        network = extract_network(ovsbr, iface)
        if network:
            ovs_net_list.append(network)
        if 'vlan' in iface and isinstance(iface['vlan'], list):
            for vlan in iface['vlan']:
                if 'vlanid' in vlan:
                    vlanid = vlan['vlanid']
                    if not isinstance(vlanid, int) or not 1 < vlanid < 4095:
                        print(red(f'invalid vlanid: {vlanid}'), flush=True)
                        sys.exit(1)

                    ovssubbr = ovsbr + '.' + f'000{vlanid}'[-4:]
                    ovs_add_str += f'sudo ovs-vsctl add-br {ovssubbr} {ovsbr} {vlanid}\n'
                    network = extract_network(ovssubbr, vlan)
                    if network:
                        ovs_net_list.append(network)

    return [ovs_add_str, ovs_del_str, ovs_net_list]


def generate_container_scripts(outdir_path, cont_type, container_name, net_list, item):
    if cont_type == 'gw':
        from gennet.docker.ovs_docker import ovs_docker_gw
        return ovs_docker_gw.create_files(outdir_path, container_name, net_list, item)
    elif cont_type == 'rsyslogd':
        from gennet.docker.ovs_docker import ovs_docker_rsyslogd
        return ovs_docker_rsyslogd.create_files(outdir_path, container_name, net_list, item)
    elif cont_type == 'tftpd':
        from gennet.docker.ovs_docker import ovs_docker_tftpd
        return ovs_docker_tftpd.create_files(outdir_path, container_name, net_list)
    elif cont_type == 'ntpd':
        from gennet.docker.ovs_docker import ovs_docker_ntpd
        return ovs_docker_ntpd.create_files(outdir_path, container_name, net_list, item)
    elif cont_type == 'dnsmasq':
        from gennet.docker.ovs_docker import ovs_docker_dnsmasq
        return ovs_docker_dnsmasq.create_files(outdir_path, container_name, net_list, item)
    elif cont_type == 'mailcatcher':
        from gennet.docker.ovs_docker import ovs_docker_mailcatcher
        return ovs_docker_mailcatcher.create_files(outdir_path, container_name, net_list, item)
    elif cont_type == 'dhcpd':
        from gennet.docker.ovs_docker import ovs_docker_dhcpd
        return ovs_docker_dhcpd.create_files(outdir_path, container_name, net_list, item)
    elif cont_type == 'radiusd':
        from gennet.docker.ovs_docker import ovs_docker_radiusd
        return ovs_docker_radiusd.create_files(outdir_path, container_name, net_list, item)
    else:
        print(red(f'no such container type: {cont_type}'), flush=True)
        sys.exit(1)


def find_ovs_net(ovs_net_list, ip):
    for ovs_net in ovs_net_list:
        network = ovs_net['subnet']
        if misc.is_ip_in_network(network, ip):
            pfx = network.split('/')[1]
            found_net = {
                'ovsbr': ovs_net['ovsbr'],
                'pfx': pfx
            }
            if 'gateway' in ovs_net:
                found_net['gw'] = ovs_net['gateway']
            return found_net
    return False


def create_start_stop_all(outdir_path, container_name_list):
    start_all_sh_str = misc.del_indent("""
    #! /bin/bash
    CURRENT=$(cd $(dirname $0);pwd)

    """) + '\n'.join([f'$CURRENT/{container_name}/start.sh' for container_name in container_name_list])
    stop_all_sh_str = misc.del_indent("""
    #! /bin/bash
    CURRENT=$(cd $(dirname $0);pwd)

    """) + '\n'.join([f'$CURRENT/{container_name}/stop.sh' for container_name in container_name_list])
    return [
        [f'{outdir_path}/start.sh', start_all_sh_str],
        [f'{outdir_path}/stop.sh', stop_all_sh_str],
    ]


def generate_scripts(outdir_path, ovs_docker_params):
    iface_list = ovs_docker_params['iface']
    container_list = ovs_docker_params['container']
    [ovs_add_str, ovs_del_str, ovs_net_list] = create_ovs_str(iface_list)
    misc.prepare_clean_dir(outdir_path)
    file_list = [
        [f'{outdir_path}/create_ovs.sh', ovs_add_str],
        [f'{outdir_path}/destroy_ovs.sh', ovs_del_str],
    ]
    container_name_list = []
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
        for num, net in enumerate(item['net']):
            ip = net['ip']
            if not misc.is_ipv4(ip):
                print(red(f'invalid ipv4: {ip}'), flush=True)
                sys.exit(1)
            found_net = find_ovs_net(ovs_net_list, ip)
            if found_net:
                net_list.append(misc.concat_dict([found_net, {
                    'ifname': f'eth{num}',
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
