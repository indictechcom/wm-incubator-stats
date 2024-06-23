#!/bin/bash

source ~/www/python/venv/bin/activate
cd ~/www/python/src
python process_data.py
cd #
toolforge webservice --backend=kubernetes python3.11 restart
