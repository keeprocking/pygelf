#!/bin/bash

API_URL="http://localhost:9000/api"
INPUTS_URL="$API_URL/system/inputs"

TCP_INPUT='{
    "title": "tcp",
    "configuration": {
        "bind_address": "0.0.0.0",
        "port": 12201
    },
    "type": "org.graylog2.inputs.gelf.tcp.GELFTCPInput",
    "global": true
}'

UDP_INPUT='{
    "title": "udp",
    "configuration": {
        "bind_address": "0.0.0.0",
        "port": 12202
    },
    "type": "org.graylog2.inputs.gelf.udp.GELFUDPInput",
    "global": true
}'

HTTP_INPUT='{
    "title": "http",
    "configuration": {
        "bind_address": "0.0.0.0",
        "port": 12203
    },
    "type": "org.graylog2.inputs.gelf.http.GELFHttpInput",
    "global": true
}'

TLS_INPUT='{
    "title": "tls",
    "configuration": {
        "bind_address": "0.0.0.0",
        "port": 12204,
        "tls_enable": true,
        "tls_cert_file": "/usr/share/graylog/data/cert.pem",
        "tls_key_file": "/usr/share/graylog/data/key.pem"
    },
    "type": "org.graylog2.inputs.gelf.tcp.GELFTCPInput",
    "global": true
}'

HTTPS_INPUT='{
    "title": "https",
    "configuration": {
        "bind_address": "0.0.0.0",
        "port": 12205,
        "tls_cert_file": "/usr/share/graylog/data/cert.pem",
        "tls_client_auth": "disabled",
        "tls_client_auth_cert_file": "",
        "tls_enable": true,
        "tls_key_file": "/usr/share/graylog/data/key.pem"
    },
    "type": "org.graylog2.inputs.gelf.http.GELFHttpInput",
    "global": true  
}'

curl -u admin:admin "$API_URL/search/universal/relative?query=test&range=5&fields=message" > /dev/null

curl -u admin:admin -X "POST" -H "Content-Type: application/json" -H "X-Requested-By: cli" -d "${TCP_INPUT}" "$INPUTS_URL"
curl -u admin:admin -X "POST" -H "Content-Type: application/json" -H "X-Requested-By: cli" -d "${UDP_INPUT}" "$INPUTS_URL"
curl -u admin:admin -X "POST" -H "Content-Type: application/json" -H "X-Requested-By: cli" -d "${HTTP_INPUT}" "$INPUTS_URL"
curl -u admin:admin -X "POST" -H "Content-Type: application/json" -H "X-Requested-By: cli" -d "${TLS_INPUT}" "$INPUTS_URL"
curl -u admin:admin -X "POST" -H "Content-Type: application/json" -H "X-Requested-By: cli" -d "${HTTPS_INPUT}" "$INPUTS_URL"

sleep 10

# Due to some reason graylog seems to just ignore a couple of first incoming messages.
# Without this workaround one or two tests from the whole test suite will always fail.
for _ in {1..5}; do
    curl -X "POST" -H "Content-Type: application/json" "http://localhost:12203/gelf" -p0 -d '{"short_message": "warm-up", "host": "localhost"}'
    sleep 1
    curl -k -X "POST" -H "Content-Type: application/json" "https://localhost:12205/gelf" -p0 -d '{"short_message": "warm-up", "host": "localhost"}'
    sleep 1
done

docker exec -u 0 $(docker ps |grep graylog | awk '{print $1}') chown graylog data/key.pem
docker exec -u 0 $(docker ps |grep graylog | awk '{print $1}') chmod 0600 data/key.pem