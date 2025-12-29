from gennet.lib import misc
from gennet.docker import common


def create_ipbales_str(rules=None):
    if rules:
        return rules
    return misc.del_indent("""
    #! /bin/bash
    echo 1 > /proc/sys/net/ipv4/ip_forward

    #Flush & Reset
    iptables -F
    iptables -t nat -F
    iptables -X

    #loopback
    #iptables -A INPUT -i lo -j ACCEPT
    #iptables -A OUTPUT -o lo -j ACCEPT

    #Default Rule
    iptables -P INPUT DROP
    iptables -P OUTPUT DROP
    iptables -P FORWARD DROP

    iptables -A FORWARD -i eth0 -m state --state NEW,INVALID -j DROP
    iptables -A FORWARD -m state --state NEW,ESTABLISHED,RELATED -j ACCEPT

    iptables -A INPUT -p icmp -j ACCEPT
    iptables -A OUTPUT -p icmp -j ACCEPT

    #NAT(masquerade)
    iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE 
    """)


def create_gw_start_str(container_name, netop, preup_script):
    return misc.del_indent(f"""
    #! /bin/bash
    CURRENT=$(cd $(dirname $0);pwd)
    IMAGE_NAME=busybox
    CONTAINER_NAME={container_name}
    
    """) + preup_script + misc.del_indent(rf"""

    docker run -t -d {netop} \
        --name=$CONTAINER_NAME \
        $IMAGE_NAME /bin/sh
    
    """)

def create_macvlan_start_str(container_name, net_list):
    from gennet.docker.macvlan import macvlan_str
    [pre_str, netop, post_str] = macvlan_str.create_macvlan_prepost_str(net_list, additional_scripts=[
        'sh ${CURRENT}/rules.sh',
        'iptables -nvL -t nat',
    ])
    preup_script = 'sh ${CURRENT}/stop.sh\n' + pre_str
    container_macvlan_str = create_gw_start_str(container_name, netop, preup_script)
    container_macvlan_str += post_str
    return container_macvlan_str

def create_macvlan_files(output_dir, container_name, net_list, item):
    rules = None
    if 'rules' in item:
        rules = item['rules']
    cont_dir = f'{output_dir}/{container_name}'
    misc.prepare_clean_dir(cont_dir)
    misc.prepare_clean_dir(f'{cont_dir}/conf')
    file_list = [
        [f'{cont_dir}/start.sh', create_macvlan_start_str(container_name, net_list)],
        [f'{cont_dir}/stop.sh', common.create_stop_sh_str(container_name)],
        [f'{cont_dir}/rules.sh', create_ipbales_str(rules)]
    ]

    misc.write_file_list(file_list)
    return container_name
