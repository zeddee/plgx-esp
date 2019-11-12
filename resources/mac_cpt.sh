#!/bin/bash
for i in "$@"
do
case $i in
    -ip=*|--extension=*)
    ip="${i#*=}"
    shift # past argument=value
    ;;
    -port=*|--searchpath=*)
    port="${i#*=}"
    shift # past argument=value
    ;;
    *)
          # unknown option
    ;;
esac
done

port="${port:-9000}"
if [ -z "$ip" ];
then
   echo "Please provide a ip"
   echo "Usage : ./linux_cpt.sh -ip=34.231.100.218 -port=9000"
   exit
fi
url="https://$ip:$port"

url="$url"/downloads/
echo "$url"

curl -O  "$url"osquery-3.3.0.pkg -k
sudo installer -pkg osquery-3.3.0.pkg -target /

echo 'Installing osquery..'
mkdir osquery_mac
cd osquery_mac

echo 'Downloading flags file..'
curl -o osquery.flags "$url"osquery_linux.flags -k
# exec `wget "$url"osquery.flags --no-check-certificate`
echo 'Downloading certificate file..'
curl -O "$url"certificate.crt -k
echo 'Downloading secret file..'
curl -O "$url"secret.txt -k
osqueryd --flagfile osquery.flags
