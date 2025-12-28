from gennet.lib import misc
from gennet.docker.containers import radiusd
from gennet.docker.ovs_docker import ops


def create_run_container_str():
    """
    >>> print(create_run_container_str())

    """
    preup_script = misc.del_indent("""
    if ! docker images | egrep -q "^${IMAGE_NAME} "; then
      echo building $IMAGE_NAME image...
      docker build -t ${IMAGE_NAME} ${CURRENT}
    fi
    
    """)
    netop = '--net=none'
    return radiusd.create_radiusd_start_str('$1', netop, preup_script)


def create_files(output_dir, container_name, net_list, item):
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
        [f'{cont_dir}/run_container.sh', create_run_container_str()],
        [f'{cont_dir}/add_ovsnet.sh', ops.create_add_ovsnet_str(net_list)],
        [f'{cont_dir}/start.sh', ops.create_start_str(container_name)],
        [f'{cont_dir}/stop.sh', ops.create_stop_str(container_name)],
        [f'{cont_dir}/conf/clients.conf', radiusd.create_clients_conf_str(clients_conf)],
        [f'{cont_dir}/conf/users', radiusd.create_users_str(users)],
        [f'{cont_dir}/conf/proxy.conf', radiusd.create_proxy_conf_str(proxy_conf)],
    ]

    misc.write_file_list(file_list)
    return container_name

