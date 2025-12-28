from gennet.lib import misc
from gennet.docker import netns_str


def create_start_str(container_name):
    return misc.del_indent(f"""
    #! /bin/bash
    CURRENT=$(cd $(dirname $0);pwd)
    CONTAINER_NAME={container_name}
    bash $CURRENT/stop.sh
    bash $CURRENT/run_container.sh $CONTAINER_NAME
    bash $CURRENT/add_ovsnet.sh $CONTAINER_NAME

    """)


def create_stop_str(container_name):
    return misc.del_indent(f"""
    #! /bin/bash
    CONTAINER_NAME={container_name}

    """) + misc.del_indent("""
    sudo ovs-vsctl list-br | xargs -I{} sudo ovs-docker del-ports {} $CONTAINER_NAME
    if docker ps -a -f name=^$CONTAINER_NAME$ | grep -q $CONTAINER_NAME; then
      docker rm -f `docker ps -aq -f name=^$CONTAINER_NAME$`
    fi

    """)


def create_ovs_docker_net_str(index, ovsbr, ifname, ip, pfx, gw=None):
    if gw:
        gwstr = f'GW{index}={gw}\n'
        gwsetstr = f' --gateway=$GW{index}'
    else:
        gwstr = ''
        gwsetstr = ''
    return misc.del_indent(fr"""
    
    OVSBR{index}={ovsbr}
    IFNAME{index}={ifname}
    IP{index}={ip}
    PFX{index}={pfx}
    {gwstr}
    sudo ovs-docker add-port $OVSBR{index} $IFNAME{index} $CONTAINER_NAME \
      --ipaddress=$IP{index}/$PFX{index}{gwsetstr}

    """)


def create_add_ovsnet_str(net_list, add_lines=''):
    add_ovsnet_str = misc.del_indent("""
    #! /bin/bash
    CONTAINER_NAME=$1
    
    """)
    for num, ovs_net in enumerate(net_list):
        index = num + 1
        ovsbr = ovs_net['ovsbr']
        ifname = ovs_net['ifname']
        ip = ovs_net['ip']
        pfx = ovs_net['pfx']
        if num == 0 and 'gw' in ovs_net:
            gw = ovs_net['gw']
            add_lines += f'sudo ip netns exec $CONT_NS ping $GW{index} -c 2\n'
        else:
            gw = None
        add_ovsnet_str += create_ovs_docker_net_str(index, ovsbr, ifname, ip, pfx, gw)

    return add_ovsnet_str + '\n' + netns_str.prepare_netns_str() + add_lines + netns_str.create_netns_info_str()


def ex1_create_add_ovsnet_str():
    """
    >>> print(ex1_create_add_ovsnet_str())
    #! /bin/bash
    CONTAINER_NAME=$1
    <BLANKLINE>
    OVSBR1=br1.3000
    IFNAME1=eth0
    IP1=10.30.0.69
    PFX1=24
    GW1=10.30.0.1
    <BLANKLINE>
    sudo ovs-docker del-ports $OVSBR1 $CONTAINER_NAME
    sudo ovs-docker add-port $OVSBR1 $IFNAME1 $CONTAINER_NAME \\
      --ipaddress=$IP1/$PFX1 --gateway=$GW1
    <BLANKLINE>
    CONT_NS=NS_$CONTAINER_NAME
    CONT_ID=`docker ps -q -f name=^$CONTAINER_NAME$`
    CONT_PID=`docker inspect $CONT_ID --format '{{.State.Pid}}'`
    sudo ip netns add testing
    sudo ip netns del testing
    sudo ip netns del $CONT_NS > /dev/null 2>&1
    sudo ln -s /proc/$CONT_PID/ns/net /var/run/netns/$CONT_NS
    sudo ip netns exec $CONT_NS ping $GW1 -c 2
    sudo ip netns exec $CONT_NS ip -br l
    sudo ip netns exec $CONT_NS ip r
    sudo ip netns exec $CONT_NS ip -4 -br a
    <BLANKLINE>
    """
    ex1_net_list = [
        {
            'ovsbr': 'br1.3000',
            'ifname': 'eth0',
            'ip': '10.30.0.69',
            'pfx': '24',
            'gw': '10.30.0.1'
        }
    ]
    return create_add_ovsnet_str(ex1_net_list)


def ex2_create_add_ovsnet_str():
    """
    >>> print(ex2_create_add_ovsnet_str())
    #! /bin/bash
    CONTAINER_NAME=$1
    <BLANKLINE>
    OVSBR1=br1.3000
    IFNAME1=eth0
    IP1=10.30.0.69
    PFX1=24
    GW1=10.30.0.1
    <BLANKLINE>
    sudo ovs-docker del-ports $OVSBR1 $CONTAINER_NAME
    sudo ovs-docker add-port $OVSBR1 $IFNAME1 $CONTAINER_NAME \\
      --ipaddress=$IP1/$PFX1 --gateway=$GW1
    <BLANKLINE>
    OVSBR2=br1.4084
    IFNAME2=eth1
    IP2=192.168.10.69
    PFX2=24
    <BLANKLINE>
    sudo ovs-docker del-ports $OVSBR2 $CONTAINER_NAME
    sudo ovs-docker add-port $OVSBR2 $IFNAME2 $CONTAINER_NAME \\
      --ipaddress=$IP2/$PFX2
    <BLANKLINE>
    CONT_NS=NS_$CONTAINER_NAME
    CONT_ID=`docker ps -q -f name=^$CONTAINER_NAME$`
    CONT_PID=`docker inspect $CONT_ID --format '{{.State.Pid}}'`
    sudo ip netns add testing
    sudo ip netns del testing
    sudo ip netns del $CONT_NS > /dev/null 2>&1
    sudo ln -s /proc/$CONT_PID/ns/net /var/run/netns/$CONT_NS
    sudo ip netns exec $CONT_NS ping $GW1 -c 2
    sudo ip netns exec $CONT_NS ip -br l
    sudo ip netns exec $CONT_NS ip r
    sudo ip netns exec $CONT_NS ip -4 -br a
    <BLANKLINE>
    """
    ex2_net_list = [
        {
            'ovsbr': 'br1.3000',
            'ifname': 'eth0',
            'ip': '10.30.0.69',
            'pfx': '24',
            'gw': '10.30.0.1'
        },
        {
            'ovsbr': 'br1.4084',
            'ifname': 'eth1',
            'ip': '192.168.10.69',
            'pfx': '24',
            'gw': '192.168.10.62'
        }
    ]
    return create_add_ovsnet_str(ex2_net_list)
