#!/bin/bash

# Define default port
PORT=8080

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -p|--port) PORT="$2"; echo "PORT: $2"; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

docker build -t flask-server .

docker run -d -p $PORT:8080 --name flask-container flask-server