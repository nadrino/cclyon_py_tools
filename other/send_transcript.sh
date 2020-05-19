#! /bin/bash

scp -r $1 ablanche@adrien-blanchet.duia.eu:/var/www/html/transcript/.
echo "http://www.nadrino.com/transcript/$1"

