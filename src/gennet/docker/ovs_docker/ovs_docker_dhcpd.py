from gennet.lib import misc
from gennet.docker.containers import dhcpd
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
    return dhcpd.create_dhcpd_start_str('$1', netop, preup_script, dhcpd.create_cmd_as_delayed_cmd_arg())


def create_files(output_dir, container_name, net_list, item):
    subnets = None
    if 'subnets' in item:
        subnets = item['subnets']
    cont_dir = f'{output_dir}/{container_name}'
    misc.prepare_clean_dir(cont_dir)
    misc.prepare_clean_dir(f'{cont_dir}/conf')
    file_list = [
        [f'{cont_dir}/Dockerfile', dhcpd.create_dhcpd_dockerfile_str()],
        [f'{cont_dir}/run_container.sh', create_run_container_str()],
        [f'{cont_dir}/add_ovsnet.sh', ops.create_add_ovsnet_str(net_list)],
        [f'{cont_dir}/start.sh', ops.create_start_str(container_name)],
        [f'{cont_dir}/stop.sh', ops.create_stop_str(container_name)],
        [f'{cont_dir}/conf/dhcpd.conf', dhcpd.create_dhcpd_conf_str(subnets)],
        [f'{cont_dir}/conf/dhcpd.leases', ''],
    ]

    misc.write_file_list(file_list)
    return container_name
