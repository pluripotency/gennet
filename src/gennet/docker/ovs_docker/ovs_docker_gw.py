from gennet.lib import misc
from gennet.docker.containers import gw
from gennet.docker.ovs_docker import ops


def create_run_container_str():
    """
    >>> print(create_run_container_str())

    """
    netop = '--net=none'
    return gw.create_gw_start_str('$1', netop, '')


def create_files(output_dir, container_name, net_list, item):
    rules = None
    if 'rules' in item:
        rules = item['rules']
    cont_dir = f'{output_dir}/{container_name}'
    add_lines = ''
    # for num in range(0, len(net_list)):
    #     add_lines += f'sudo ip netns exec $CONT_NS arping -A $IP{num+1}\n'
    add_lines += 'sudo ip netns exec $CONT_NS arping -A $GW1\n'
    add_lines += 'sudo ip netns exec $CONT_NS /bin/bash ./rules.sh\n'

    file_list = [
        [f'{cont_dir}/run_container.sh', create_run_container_str()],
        [f'{cont_dir}/add_ovsnet.sh', ops.create_add_ovsnet_str(net_list, add_lines)],
        [f'{cont_dir}/start.sh', ops.create_start_str(container_name)],
        [f'{cont_dir}/stop.sh', ops.create_stop_str(container_name)],
        [f'{cont_dir}/rules.sh', gw.create_ipbales_str(rules)],
    ]

    misc.prepare_clean_dir(cont_dir)
    misc.write_file_list(file_list)

    return container_name

