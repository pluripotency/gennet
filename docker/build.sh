#! /bin/sh
CURRENT=$(cd $(dirname $0);pwd)
IMAGE_NAME=gennet

docker build -f ${CURRENT}/Dockerfile -t ${IMAGE_NAME} ${CURRENT}/..
