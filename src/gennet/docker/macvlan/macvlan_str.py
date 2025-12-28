from gennet.lib import misc
from gennet.docker import netns_str


def create_macvlan_str(index, name, subnet, iface, ip, gw=None):
    """
    >>> print(create_macvlan_str(1, 'test', '192.168.0.0/24', 'eth1.4084', '192.168.0.10'))
    <BLANKLINE>
    NET1=test
    SUBNET1=192.168.0.0/24
    IFACE1=eth1.4084
    IP1=192.168.0.10
    docker network ls | egrep -q " $NET1 +macvlan" || \\
      docker network create -d macvlan --subnet=$SUBNET1 --gateway=192.168.0.2 -o parent=$IFACE1 $NET1
    <BLANKLINE>
    >>> print(create_macvlan_str(1, 'test', '192.168.0.0/24', 'eth1.4084', '192.168.0.10', '192.168.0.254'))
    <BLANKLINE>
    NET1=test
    SUBNET1=192.168.0.0/24
    IFACE1=eth1.4084
    IP1=192.168.0.10
    GW1=192.168.0.254
    docker network ls | egrep -q " $NET1 +macvlan" || \\
      docker network create -d macvlan --subnet=$SUBNET1 --gateway=192.168.0.2 -o parent=$IFACE1 $NET1
    <BLANKLINE>
    """
    if gw:
        gw_line = f'\n    GW{index}={gw}'
    else:
        gw_line = ''
    # macvlan gateway is always needed to suit
    second_ip_in_subnet = misc.get_index_ip_in_subnet(subnet, 2)
    return misc.del_indent(f"""
    
    NET{index}={name}
    SUBNET{index}={subnet}
    IFACE{index}={iface}
    IP{index}={ip}{gw_line}
    docker network ls | egrep -q " $NET{index} +macvlan" || \\
      docker network create -d macvlan --subnet=$SUBNET{index} --gateway={second_ip_in_subnet} -o parent=$IFACE{index} $NET{index}

    """)


ex_macvlan_list = [
    {
        'macvlan_name': 'native',
        'subnet': '10.30.0.0/24',
        'macvlan_iface': 'eth1',
        'ip': '10.30.0.55',
        'gateway': '10.30.0.1',
        'routes': [['192.168.202.0/24', '10.30.0.52']]
    },
    {
        'macvlan_name': 'v4084',
        'subnet': '192.168.10.0/24',
        'macvlan_iface': 'eth1.4084',
        'ip': '192.168.10.55',
    }
]
ex_additional_scripts = [
    'sh ${CURRENT}/rule.sh'
]


def create_macvlan_prepost_str(macvlan_net_list, additional_scripts: list[str]=[]):
    """
    >>> [pre_str, netop, post_str] = create_macvlan_prepost_str(ex_macvlan_list, ex_additional_scripts)
    >>> print(pre_str)
    <BLANKLINE>
    NET1=native
    SUBNET1=10.30.0.0/24
    IFACE1=eth1
    IP1=10.30.0.55
    GW1=10.30.0.1
    docker network ls | egrep -q " $NET1 +macvlan" || \\
      docker network create -d macvlan --subnet=$SUBNET1 --gateway=10.30.0.2 -o parent=$IFACE1 $NET1
    <BLANKLINE>
    NET2=v4084
    SUBNET2=192.168.10.0/24
    IFACE2=eth1.4084
    IP2=192.168.10.55
    docker network ls | egrep -q " $NET2 +macvlan" || \\
      docker network create -d macvlan --subnet=$SUBNET2 --gateway=192.168.10.2 -o parent=$IFACE2 $NET2
    <BLANKLINE>
    >>> print(post_str)
    CONT_NS=NS_$CONTAINER_NAME
    CONT_ID=`docker ps -q -f name=^$CONTAINER_NAME$`
    CONT_PID=`docker inspect $CONT_ID --format '{{.State.Pid}}'`
    sudo ip netns add testing
    sudo ip netns del testing
    sudo ip netns del $CONT_NS > /dev/null 2>&1
    sudo ln -s /proc/$CONT_PID/ns/net /var/run/netns/$CONT_NS
    <BLANKLINE>
    docker network connect --ip $IP2 $NET2 $CONT_ID
    <BLANKLINE>
    sudo ip netns exec $CONT_NS ip r d default
    sudo ip netns exec $CONT_NS ip r a default via 10.30.0.1
    sudo ip netns exec $CONT_NS ping 10.30.0.1 -c 2
    sudo ip netns exec $CONT_NS ip r a 192.168.202.0/24 via 10.30.0.52
    sudo ip netns exec $CONT_NS ping 10.30.0.52 -c 2
    sudo ip netns exec $CONT_NS sh ${CURRENT}/rule.sh
    sudo ip netns exec $CONT_NS ip -br l
    sudo ip netns exec $CONT_NS ip r
    sudo ip netns exec $CONT_NS ip -4 -br a
    <BLANKLINE>
    """
    pre_str = ''
    netop = '--network=${NET1} --ip=${IP1}'
    post_str = netns_str.prepare_netns_str()
    gateway_list = []
    routes = []
    for num, macvlan in enumerate(macvlan_net_list):
        index = num + 1
        name = macvlan['macvlan_name']
        subnet = macvlan['subnet']
        iface = macvlan['macvlan_iface']
        ip = macvlan['ip']
        if 'gateway' in macvlan:
            gw = macvlan['gateway']
            gateway_list += [gw]
        else:
            gw = None
        if 'routes' in macvlan:
            routes += macvlan['routes']
        pre_str += create_macvlan_str(index, name, subnet, iface, ip, gw)
        if num > 0:
            post_str += f'\ndocker network connect --ip $IP{index} $NET{index} $CONT_ID\n\n'

    if len(gateway_list) > 0:
        routes = [['default', gateway_list[0]]] + routes
    post_str += netns_str.create_netns_routes_str(routes) 
    if len(additional_scripts) > 0:
        post_str += netns_str.create_netns_scripts_str(additional_scripts)
    post_str += netns_str.create_netns_info_str()
    return [pre_str, netop, post_str]
