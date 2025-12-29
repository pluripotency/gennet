from gennet.lib import misc
from gennet.docker import common

def create_start_cmd(smtp_port, http_port, delay=False):
    cmd_base = f"mailcatcher --no-quit --foreground --ip=0.0.0.0 --http-path='/' --smtp-port {smtp_port} --http-port {http_port}"
    if delay:
        return f'sh -c "sleep 2 && {cmd_base}"'
    return f'sh -c "{cmd_base}"'

def create_start_str(container_name, netop, preup_script, docker_cmd=''):
    return misc.del_indent(rf"""
    #! /bin/bash
    CURRENT=$(cd $(dirname $0);pwd)
    IMAGE_NAME=schickling/mailcatcher
    CONTAINER_NAME={container_name}
    
    """) + preup_script + misc.del_indent(rf"""
    docker run -t -d {netop} \
        --name=$CONTAINER_NAME \
        $IMAGE_NAME {docker_cmd}
    
    """)

def create_macvlan_start_str(container_name, net_list, smtp_port, http_port):
    from gennet.docker.macvlan import macvlan_str
    [pre_str, netop, post_str] = macvlan_str.create_macvlan_prepost_str(net_list)
    preup_script = 'sh ${CURRENT}/stop.sh\n' + pre_str
    cmd = create_start_cmd(smtp_port, http_port)
    container_macvlan_str = create_start_str(container_name, netop, preup_script, cmd)
    container_macvlan_str += post_str
    return container_macvlan_str

def create_macvlan_files(output_dir, container_name, net_list, item):
    http_port = 1080
    if 'http_port' in item:
        http_port = item['http_port']
    smtp_port = 1025
    if 'smtp_port' in item:
        smtp_port = item['smtp_port']
    cont_dir = f'{output_dir}/{container_name}'
    misc.prepare_clean_dir(cont_dir)
    file_list = [
        [f'{cont_dir}/start.sh', create_macvlan_start_str(container_name, net_list, smtp_port, http_port)],
        [f'{cont_dir}/stop.sh', common.create_stop_sh_str(container_name)],
    ]
    misc.write_file_list(file_list)
    return container_name
