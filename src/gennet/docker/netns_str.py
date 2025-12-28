from gennet.lib import misc


def prepare_netns_str():
    """
    >>> print(prepare_netns_str())
    CONT_NS=NS_$CONTAINER_NAME
    CONT_ID=`docker ps -q -f name=^$CONTAINER_NAME$`
    CONT_PID=`docker inspect $CONT_ID --format '{{.State.Pid}}'`
    sudo ip netns add testing
    sudo ip netns del testing
    sudo ip netns del $CONT_NS > /dev/null 2>&1
    sudo ln -s /proc/$CONT_PID/ns/net /var/run/netns/$CONT_NS
    <BLANKLINE>
    """
    return misc.del_indent("""
    CONT_NS=NS_$CONTAINER_NAME
    CONT_ID=`docker ps -q -f name=^$CONTAINER_NAME$`
    CONT_PID=`docker inspect $CONT_ID --format '{{.State.Pid}}'`
    sudo ip netns add testing
    sudo ip netns del testing
    sudo ip netns del $CONT_NS > /dev/null 2>&1
    sudo ln -s /proc/$CONT_PID/ns/net /var/run/netns/$CONT_NS
    
    """)


def create_netns_routes_str(routes):
    """
    >>> print(create_netns_routes_str([['default', '192.168.0.254'], ['172.16.0.0/24', '192.168.0.1']]))
    sudo ip netns exec $CONT_NS ip r d default
    sudo ip netns exec $CONT_NS ip r a default via 192.168.0.254
    sudo ip netns exec $CONT_NS ping 192.168.0.254 -c 2
    sudo ip netns exec $CONT_NS ip r a 172.16.0.0/24 via 192.168.0.1
    sudo ip netns exec $CONT_NS ping 192.168.0.1 -c 2
    <BLANKLINE>
    """
    netns_routes_str = ''
    for route in routes:
        [target, gw] = route
        if target == 'default':
            netns_routes_str += 'sudo ip netns exec $CONT_NS ip r d default\n'
        netns_routes_str += misc.del_indent(f"""
        sudo ip netns exec $CONT_NS ip r a {target} via {gw}
        sudo ip netns exec $CONT_NS ping {gw} -c 2

        """, indent=8)
    return netns_routes_str


def create_netns_scripts_str(scripts: list[str]):
    scripts_str = ""
    for line in scripts:
        scripts_str += f"sudo ip netns exec $CONT_NS {line}\n"
    return scripts_str


def create_netns_info_str():
    """
    >>> print(create_netns_info_str())
    sudo ip netns exec $CONT_NS ip -br l
    sudo ip netns exec $CONT_NS ip r
    sudo ip netns exec $CONT_NS ip -4 -br a
    <BLANKLINE>
    """
    return misc.del_indent(f"""
    sudo ip netns exec $CONT_NS ip -br l
    sudo ip netns exec $CONT_NS ip r
    sudo ip netns exec $CONT_NS ip -4 -br a
    
    """)


def create_basic_netns_str(routes):
    """
    >>> print(create_basic_netns_str([['default', '192.168.0.254'], ['172.16.0.0/24', '192.168.0.1']]))
    CONT_NS=NS_$CONTAINER_NAME
    CONT_ID=`docker ps -q -f name=^$CONTAINER_NAME$`
    CONT_PID=`docker inspect $CONT_ID --format '{{.State.Pid}}'`
    sudo ip netns add testing
    sudo ip netns del testing
    sudo ip netns del $CONT_NS > /dev/null 2>&1
    sudo ln -s /proc/$CONT_PID/ns/net /var/run/netns/$CONT_NS
    sudo ip netns exec $CONT_NS ip r d default
    sudo ip netns exec $CONT_NS ip r a default via 192.168.0.254
    sudo ip netns exec $CONT_NS ping 192.168.0.254 -c 2
    sudo ip netns exec $CONT_NS ip r a 172.16.0.0/24 via 192.168.0.1
    sudo ip netns exec $CONT_NS ping 192.168.0.1 -c 2
    sudo ip netns exec $CONT_NS ip -br l
    sudo ip netns exec $CONT_NS ip r
    sudo ip netns exec $CONT_NS ip -4 -br a
    <BLANKLINE>
    """
    netns_str = prepare_netns_str()
    netns_str += create_netns_routes_str(routes)
    netns_str += create_netns_info_str()
    return netns_str


