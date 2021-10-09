#!/bin/sh
find ./GetNews2Onet -type f | grep .py$ > list
cat list | xargs sha1sum >> GetNews2Onet-`date +%b%d-%H%M`.txt
echo =========*=========*=========*=========*=========*=========*=========*=========* >> GetNews2Onet-`date +%b%d-%H%M`.txt
cat list | xargs pr -n -f -l 84 >> GetNews2Onet-`date +%b%d-%H%M`.txt
rm list

