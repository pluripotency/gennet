#! /bin/sh
IMAGE_NAME=gennet

CURRENT=$(cd $(dirname $0);pwd)
sh ${CURRENT}/build.sh

docker save -o ${CURRENT}/${IMAGE_NAME}.tar ${IMAGE_NAME}
gzip -f ${CURRENT}/${IMAGE_NAME}.tar
