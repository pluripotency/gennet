from gennet.lib import misc
from gennet.docker import common
IMAGE_NAME='tftpd'
tftp_user = 'tftp_user'
default_cmd_in_dockerfile = [
    "/usr/sbin/in.tftpd",
    "--foreground",
    "--user",
    tftp_user,
    "--create",
    "--address",
    "0.0.0.0:69",
    "--secure",
    f"/home/{tftp_user}/tftpboot"
]


def create_default_cmd_in_dockerfile():
    """
    >>> print(create_default_cmd_in_dockerfile())
    ["/usr/sbin/in.tftpd","--foreground","--user","tftp_user","--create","--address","0.0.0.0:69","--secure","/home/tftp_user/tftpboot"]
    """
    return '[' + ','.join([f'"{arg}"' for arg in default_cmd_in_dockerfile]) + ']'


def create_delay_default_cmd():
    """
    >>> print(create_delay_default_cmd())
    /bin/sh -c "sleep 2 && /usr/sbin/in.tftpd --foreground --user tftp_user --create --address 0.0.0.0:69 --secure /home/tftp_user/tftpboot"
    """
    default_cmd_str = ' '.join(default_cmd_in_dockerfile)
    return f'/bin/sh -c "sleep 2 && {default_cmd_str}"'


def create_tftpd_dockerfile_str(uid=1000, gid=1000):
    return misc.del_indent(f"""
    FROM ubuntu:22.04

    RUN apt-get update && apt-get install -y tftpd-hpa tftp-hpa && apt-get clean && rm -rf /var/lib/apt/lists/*
    ARG USERNAME={tftp_user}
    ARG UID={uid}
    ARG GID={gid}
    RUN groupadd -g $GID $USERNAME && useradd -u $UID -g $UID -m $USERNAME
    USER $USERNAME
    WORKDIR /home/$USERNAME
    RUN mkdir tftpboot
    USER root
    CMD {create_default_cmd_in_dockerfile()}
    """)


def create_tftpd_start_str(container_name, netop, preup_script, docker_cmd=''):
    start_sh_str = misc.del_indent(f"""
    #! /bin/bash
    CURRENT=$(cd $(dirname $0);pwd)
    IMAGE_NAME={IMAGE_NAME}
    CONTAINER_NAME={container_name}
    
    """)
    start_sh_str += preup_script
    start_sh_str += misc.del_indent(rf"""

    TFTPBOOT_DIR=$CURRENT/tftpboot
    mkdir -p $TFTPBOOT_DIR
    docker run -d {netop} \
        --name=$CONTAINER_NAME \
        -v $TFTPBOOT_DIR:/home/{tftp_user}/tftpboot:rw \
        $IMAGE_NAME {docker_cmd}
    
    """)
    return start_sh_str

def create_base_files(output_dir, container_name, net_list):
    cont_dir = f'{output_dir}/{container_name}'
    misc.prepare_clean_dir(cont_dir)
    file_list = [
        [f'{cont_dir}/Dockerfile', create_tftpd_dockerfile_str()],
        [f'{cont_dir}/build.sh', common.create_build_sh_str(IMAGE_NAME)],
        [f'{cont_dir}/stop.sh', common.create_stop_sh_str(container_name)],
    ]
    return cont_dir, file_list

def create_bridge_files(output_dir, container_name, net_list, item):
    cont_dir, file_list = create_base_files(output_dir, container_name, item)
    netop = '-p 69:69/udp'
    preup_script = common.create_build_and_stop_str()
    file_list += [
        [f'{cont_dir}/start.sh', create_tftpd_start_str(container_name, netop, preup_script)],
    ]
    misc.write_file_list(file_list)
    return container_name

def create_hostnet_files(output_dir, container_name, net_list, item):
    cont_dir, file_list = create_base_files(output_dir, container_name, item)
    netop = '--network=host'
    preup_script = common.create_build_and_stop_str()
    file_list += [
        [f'{cont_dir}/start.sh', create_tftpd_start_str(container_name, netop, preup_script)],
    ]
    misc.write_file_list(file_list)
    return container_name

def create_macvlan_start_str(container_name, net_list):
    from gennet.docker.macvlan import macvlan_str
    [pre_str, netop, post_str] = macvlan_str.create_macvlan_prepost_str(net_list)
    preup_script = common.create_build_and_stop_str() + pre_str
    tftpd_macvlan_str = create_tftpd_start_str(container_name, netop, preup_script)
    tftpd_macvlan_str += post_str
    return tftpd_macvlan_str

def create_macvlan_files(output_dir, container_name, net_list):
    cont_dir, file_list = create_base_files(output_dir, container_name, net_list)
    file_list = [
        [f'{cont_dir}/start.sh', create_macvlan_start_str(container_name, net_list)],
    ]
    misc.write_file_list(file_list)
    return container_name
