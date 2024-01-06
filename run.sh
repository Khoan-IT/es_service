#!/bin/bash

es_ver=`cat version.txt`

# gcloud auth login --cred-file "./cert.json"
gcloud auth login --cred-file=/etc/gcloud-credentials/cert.json

mkdir -p checkpoint

gsutil -m cp -r \
    "gs://model_es/${es_ver}/*" checkpoint
# Start server
while true
do
    echo "Running server..."
    python3 server.py

    sleep 0.2
done

echo "Server stopped..."