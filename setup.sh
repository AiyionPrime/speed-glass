#!/bin/bash

rm -r env
virtualenv env
env/bin/pip install -r requirements.txt
