from gennet.lib import misc
from gennet.docker.containers import tftpd
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
    return tftpd.create_tftpd_start_str('$1', netop, preup_script, tftpd.create_delay_default_cmd())


def create_files(output_dir, container_name, net_list):
    cont_dir = f'{output_dir}/{container_name}'

    file_list = [
        [f'{cont_dir}/Dockerfile', tftpd.create_tftpd_dockerfile_str()],
        [f'{cont_dir}/run_container.sh', create_run_container_str()],
        [f'{cont_dir}/add_ovsnet.sh', ops.create_add_ovsnet_str(net_list)],
        [f'{cont_dir}/start.sh', ops.create_start_str(container_name)],
        [f'{cont_dir}/stop.sh', ops.create_stop_str(container_name)],
    ]

    misc.prepare_clean_dir(cont_dir)
    misc.write_file_list(file_list)
    return container_name
