#!/bin/bash
FLUME_PATH=/usr/local/apache-flume

cd $FLUME_PATH

bin/flume-ng agent --name source_agent --conf ./conf/ --conf-file conf/flume_mlapi.conf -Dflume.root.logger=INFO,console
