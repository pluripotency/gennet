from gennet.lib import misc
from gennet.docker.containers import dnsmasq
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
    return dnsmasq.create_dnsmasq_start_str('$1', netop, preup_script)


def create_files(output_dir, container_name, net_list, item):
    hosts = None
    if 'hosts' in item:
        hosts = item['hosts']
    resolv_conf = None
    if 'resolv_conf' in item:
        resolv_conf = item['resolv_conf']
    cont_dir = f'{output_dir}/{container_name}'
    misc.prepare_clean_dir(cont_dir)
    misc.prepare_clean_dir(f'{cont_dir}/conf')
    file_list = [
        [f'{cont_dir}/Dockerfile', dnsmasq.create_dnsmasq_dockerfile_str()],
        [f'{cont_dir}/run_container.sh', create_run_container_str()],
        [f'{cont_dir}/add_ovsnet.sh', ops.create_add_ovsnet_str(net_list)],
        [f'{cont_dir}/start.sh', ops.create_start_str(container_name)],
        [f'{cont_dir}/stop.sh', ops.create_stop_str(container_name)],
        [f'{cont_dir}/conf/dnsmasq.conf', dnsmasq.create_dnsmasq_conf_str()],
        [f'{cont_dir}/conf/resolv.conf', dnsmasq.create_resolv_conf_str(resolv_conf)],
        [f'{cont_dir}/conf/hosts', dnsmasq.create_hosts_str(hosts)],
    ]

    misc.write_file_list(file_list)
    return container_name

