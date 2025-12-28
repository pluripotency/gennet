from gennet.lib import misc


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
