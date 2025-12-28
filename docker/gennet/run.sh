#! /bin/sh
CURRENT=$(cd $(dirname $0);pwd)
CONTAINER_NAME=gennet
IMAGE_NAME=gennet

[ -f ${CURRENT}/../build.sh ] && sh ${CURRENT}/../build.sh

OUTDIR_NAME=generated
CONF_NAME=config.toml

OUTDIR_PATH=$CURRENT/generated
mkdir -p $OUTDIR_PATH

docker run -it --rm \
    --name $CONTAINER_NAME \
    --net none \
    -e OUTDIR_PATH=/tmp/$OUTDIR_NAME \
    -e TOML_PATH=/tmp/$CONF_NAME \
    -v $OUTDIR_PATH:/tmp/$OUTDIR_NAME:rw \
    -v $CURRENT/$CONF_NAME:/tmp/$CONF_NAME:ro \
    $IMAGE_NAME python ./src/gennet/main.py

