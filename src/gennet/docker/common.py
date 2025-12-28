from gennet.lib import misc


def create_build_sh_str(image_name):
    return misc.del_indent(f"""
    #! /bin/bash
    IMAGE_NAME={image_name}""" + r"""
    CURRENT=$(cd $(dirname $0);pwd)
    docker build -f ${CURRENT}/Dockerfile -t ${IMAGE_NAME} ${CURRENT}
    """)


def create_stop_sh_str(container_name):
    return misc.del_indent(f"""
    #! /bin/bash
    CONTAINER_NAME={container_name}
    """ + r"""
    if docker ps -a | grep -q ${CONTAINER_NAME}; then
      docker rm -f `docker ps -aq -f name=^${CONTAINER_NAME}$`
    fi
    """)


def create_build_and_stop_str():
    return misc.del_indent("""

    if docker images | grep -q ${IMAGE_NAME}; then
      echo "use existing image: ${IMAGE_NAME}"
    else
      echo "start building: ${IMAGE_NAME}"
      sh ${CURRENT}/build.sh
    fi
    sh ${CURRENT}/stop.sh

    """)


def create_build1up_and_stop_str():
    return misc.del_indent("""

    if docker images | grep -q ${IMAGE_NAME}; then
      echo "use existing image: ${IMAGE_NAME}"
    else
      echo "start building: ${IMAGE_NAME}"
      sh ${CURRENT}/../build.sh
    fi
    sh ${CURRENT}/stop.sh

    """)
