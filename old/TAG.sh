#!/bin/sh
export LD_LIBRARY_PATH=`pwd`/export/linux2/lib:$LD_LIBRARY_PATH
python Player_TAG.py "$@"
