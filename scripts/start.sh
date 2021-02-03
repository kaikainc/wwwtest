#!/bin/bash

PROJECT="/home/hde/fintest"
cd $PROJECT

source /home/hde/.pyenv/versions/py3/bin/activate

exec gunicorn -w 8 -t 300 -b unix:/tmp/fintest.sock fintest:app