#!/usr/bin/env bash

umask 077

answers() {
	echo --
	echo CO
	echo Boulder
	echo pygelf
	echo pygelf
	echo localhost
	echo hello@world.com
}

PEM1=`/bin/mktemp /tmp/openssl.XXXXXX`
PEM2=`/bin/mktemp /tmp/openssl.XXXXXX`
trap "rm -f $PEM1 $PEM2" SIGINT
answers | openssl req -newkey rsa:2048 -keyout $PEM1 -nodes -x509 -days 3650 -out $PEM2 2> /dev/null
cat $PEM1 > key.pem
cat $PEM2 > cert.pem
rm -f $PEM1 $PEM2
