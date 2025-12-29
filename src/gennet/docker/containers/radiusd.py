from gennet.lib import misc
from gennet.docker import common


def create_radiusd_dockerfile_str():
    return misc.del_indent(f"""
    FROM alpine:latest
    RUN apk add --no-cache freeradius freeradius-radclient freeradius-utils
    CMD ["radiusd","-X"]
    """)


def create_radiusd_start_str(container_name, netop, preup_script):
    return misc.del_indent(f"""
    #! /bin/bash
    CURRENT=$(cd $(dirname $0);pwd)
    IMAGE_NAME=alpine-freeradius
    CONTAINER_NAME={container_name}
    
    """) + preup_script + misc.del_indent(rf"""

    docker run -d {netop} \
        --name=$CONTAINER_NAME \
        -v $CURRENT/conf/proxy.conf:/etc/raddb/proxy.conf:ro \
        -v $CURRENT/conf/clients.conf:/etc/raddb/clients.conf:ro \
        -v $CURRENT/conf/users:/etc/raddb/users:ro \
        $IMAGE_NAME
    
    """)


def create_start_sh_str(container_name):
    netop = '-p 1812:1812/udp -p 1813:1813/udp'
    preup_script = common.create_build_and_stop_str()
    return create_radiusd_start_str(container_name, netop, preup_script)


def create_check_sh_str(container_name):
    return misc.del_indent(f"""
    #! /bin/bash
    CONTAINER_NAME={container_name}
    USER=v2000
    PASS=v2000
    IP=127.0.0.1
    IPPASS=testing123
    # this doesn't work in case of ovsdocker
    docker exec `docker ps -q -f name=^$CONTAINER_NAME$` radtest $USER $PASS $IP 0 $IPPASS
    """)


def create_proxy_conf_str(proxy_conf=None):
    if proxy_conf:
        return proxy_conf
    return misc.del_indent("""
    proxy server {
        default_fallback = no
    }

    # home_server example1 {
    #     type = auth
    #     ipaddr = 192.168.0.10
    #     port = 1812
    #     secret = password
    #     require_message_authenticator = yes
    #     response_window = 20
    #     zombie_period = 40
    #     revive_interval = 120
    #     #status_check = status-server
    #     status_check = none
    #     check_interval = 30
    #     num_answers_to_alive = 3
    #     max_outstanding = 65536
    #     coa {
    #         irt = 2
    #         mrt = 16
    #         mrc = 5
    #         mrd = 30
    #     }
    # }

    # home_server example2 {
    #     type = auth
    #     ipaddr = 192.168.0.20
    #     port = 1812
    #     secret = password
    #     require_message_authenticator = yes
    #     response_window = 20
    #     zombie_period = 40
    #     revive_interval = 120
    #     #status_check = status-server
    #     status_check = none
    #     check_interval = 30
    #     num_answers_to_alive = 3
    #     max_outstanding = 65536
    #     coa {
    #         irt = 2
    #         mrt = 16
    #         mrc = 5
    #         mrd = 30
    #     }
    # }
    # 
    # home_server_pool example_failover {
    #     type = fail-over
    #     home_server = example1
    #     home_server = example2
    # }

    # realm ~.*test\.example\.local$ {
    #     auth_pool = example_failover
    #     nostrip
    # }
    # realm NULL {
    #     auth_pool = example_failover
    #     nostrip
    # }
    # realm DEFAULT {
    #     auth_pool = example_failover
    #     nostrip
    # }

    realm LOCAL {                      
        #  If we do not specify a server pool, the realm is LOCAL, and
        #  requests are not proxied to it.                     
    }

    """)


def create_clients_conf_str(clients_conf=None):
    if clients_conf:
        return clients_conf
    return misc.del_indent("""
    client  localhost {
      ipaddr = 127.0.0.1
      secret = testing123
    }
    client  192.168.0.0/24 {
      secret = testing123
    }

    """)


def create_users_str(users=None):
    if users:
        return users
    else:
        return misc.del_indent("""
    525400112233 Cleartext-Password := "525400112233"
            Tunnel-Type = VLAN,
            Tunnel-Medium-Type = IEEE-802,
            Tunnel-Private-Group-Id = 2000
    v2000   Cleartext-Password := "v2000"
            Tunnel-Type = VLAN,
            Tunnel-Medium-Type = IEEE-802,
            Tunnel-Private-Group-Id = 2000

    """)

def create_base_files(output_dir, container_name, item):
    clients_conf = None
    if 'clients_conf' in item:
        clients_conf = item['clients_conf']
    users = None
    if 'users' in item:
        users = item['users']
    proxy_conf = None
    if 'proxy_conf' in item:
        proxy_conf = item['proxy_conf']
    cont_dir = f'{output_dir}/{container_name}'
    misc.prepare_clean_dir(cont_dir)
    misc.prepare_clean_dir(f'{cont_dir}/conf')
    file_list = [
        [f'{cont_dir}/Dockerfile', radiusd.create_radiusd_dockerfile_str()],
        [f'{cont_dir}/build.sh', common.create_build_sh_str('alpine-freeradius')],
        [f'{cont_dir}/stop.sh', common.create_stop_sh_str(container_name)],
        [f'{cont_dir}/conf/clients.conf', radiusd.create_clients_conf_str(clients_conf)],
        [f'{cont_dir}/conf/users', radiusd.create_users_str(users)],
        [f'{cont_dir}/conf/proxy.conf', radiusd.create_proxy_conf_str(proxy_conf)],
    ]
    return cont_dir, file_list

def create_macvlan_start_str(container_name, net_list):
    from gennet.docker.macvlan import macvlan_str
    [pre_str, netop, post_str] = macvlan_str.create_macvlan_prepost_str(net_list)
    preup_script = common.create_build_and_stop_str() + pre_str
    container_macvlan_str = radiusd.create_radiusd_start_str(container_name, netop, preup_script)
    container_macvlan_str += post_str
    return container_macvlan_str

def create_macvlan_files(output_dir, container_name, net_list, item):
    cont_dir, file_list = create_base_files(output_dir, container_name, item)
    file_list = [
        [f'{cont_dir}/start.sh', create_macvlan_start_str(container_name, net_list)],
    ]
    misc.write_file_list(file_list)
    return container_name
