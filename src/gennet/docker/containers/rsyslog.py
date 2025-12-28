from gennet.lib import misc
from gennet.docker import common


def create_rsyslog_dockerfile_str():
    return misc.del_indent(f"""
    FROM alpine:latest
    RUN apk --no-cache add rsyslog
    CMD /usr/sbin/rsyslogd -n -x -f /etc/rsyslog.conf
    """)


def create_rsyslog_start_str(container_name, netop, preup_script, docker_cmd=''):
    start_sh_str = misc.del_indent(f"""
    #! /bin/bash
    CURRENT=$(cd $(dirname $0);pwd)
    IMAGE_NAME=alpine-rsyslogd
    CONTAINER_NAME={container_name}
    
    """)
    start_sh_str += preup_script
    start_sh_str += misc.del_indent(rf"""

    docker run -d {netop} \
        --name=$CONTAINER_NAME \
        -v $CURRENT/conf/rsyslog.conf:/etc/rsyslog.conf:ro \
        -v $CURRENT/log:/var/log:rw \
        $IMAGE_NAME {docker_cmd}
    
    """)
    return start_sh_str


def create_rsyslog_conf_str(rules=None):
    if rules is None:
        rules = misc.del_indent("""
    local1.*                                                  /var/log/local1.log
    
    """)
    return misc.del_indent(f"""
    # rsyslog configuration file
    #
    # For more information see /usr/share/doc/rsyslog-*/rsyslog_conf.html
    # or latest version online at http://www.rsyslog.com/doc/rsyslog_conf.html
    # If you experience problems, see http://www.rsyslog.com/doc/troubleshoot.html


    #### Global directives ####

    # Sets the directory that rsyslog uses for work files.
    $WorkDirectory /var/lib/rsyslog

    # Sets default permissions for all log files.
    $FileOwner root
    $FileGroup adm
    $FileCreateMode 0640
    $DirCreateMode 0755
    $Umask 0022

    # Check config syntax on startup and abort if unclean (default off).
    #$AbortOnUncleanConfig on

    # Reduce repeating messages (default off).
    #$RepeatedMsgReduction on


    #### Modules ####

    # Provides --MARK-- message capability.
    module(load="immark")

    # Provides support for local system logging (e.g. via logger command).
    module(load="imuxsock")

    # Reads kernel messages.
    #module(load="imklog")
    
    module(load="imudp")
    input(type="imudp" port="514")
    
    module(load="imtcp")
    input(type="imtcp" port="514")

    #### Config files ####

    # Include all config files in /etc/rsyslog.d/.
    include(file="/etc/rsyslog.d/*.conf" mode="optional")

    #### Rules ####
    
    {rules}

    # Log all kernel messages to kern.log.
    #kern.*                                                  /var/log/kern.log

    # Log anything (except mail) of level info or higher.
    # Don't log private authentication messages!
    # NOTE: The minus sign in front of filename disables buffer flush.
    #*.info;authpriv.none;cron.none;kern.none;mail.none      -/var/log/messages

    # The authpriv file has restricted access.
    #authpriv.*                                              /var/log/auth.log

    # Log all the mail messages in one place.
    #mail.*                                                  -/var/log/mail.log

    # Log cron stuff.
    #cron.*                                                  -/var/log/cron.log

    # Everybody gets emergency messages.
    #*.emerg                                                 :omusrmsg:*

    # Log all kernel messages to the console.
    # Logging much else clutters up the screen.
    #kern.*                                                 /dev/console


    ### Examples ####

    # Send all logs to remote syslog via UDP.
    # An on-disk queue is created for this action. If the remote host is
    # down, messages are spooled to disk and sent when it is up again.
    #*.* action(
    #       type="omfwd"
    #       target="192.168.0.1"
    #       port="514"
    #       protocol="udp"
    #       queue.filename="fwdRule1"  # unique name prefix for spool files
    #       queue.type="LinkedList"
    #       queue.maxDiskSpace="256m"
    #       queue.saveOnShutdown="on"
    #       action.resumeRetryCount="-1"
    #       action.resumeInterval="30"
    #)

    # Receive messages from remote host via UDP
    # for parameters see http://www.rsyslog.com/doc/imudp.html
    #module(load="imudp")  # needs to be done just once
    #input(
    #       type="imudp"
    #       port="514"
    #)

    """)


def create_start_sh_str(container_name):
    netop = '-p 514:514/udp -p 514:514:tcp'
    preup_script = common.create_build_and_stop_str()
    return create_rsyslog_start_str(container_name, netop, preup_script)


def create_files():
    container_name = 'rsyslogd'
    cont_dir = f'/tmp/rsyslogd'
    misc.prepare_clean_dir(cont_dir)
    misc.prepare_clean_dir(cont_dir + '/conf')
    file_list = [
        [f'{cont_dir}/Dockerfile', create_rsyslog_dockerfile_str()],
        [f'{cont_dir}/start.sh', create_start_sh_str(container_name)],
        [f'{cont_dir}/stop.sh', common.create_stop_sh_str(container_name)],
        [f'{cont_dir}/build.sh', common.create_build_sh_str('alpine-rsyslogd')],
        [f'{cont_dir}/conf/rsyslog.conf', create_rsyslog_conf_str()],
    ]
    misc.write_file_list(file_list)
    return cont_dir


