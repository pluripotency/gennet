from gennet.lib import misc


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
