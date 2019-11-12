if [[ $EUID -ne 0 ]]; then
  echo "You must be a root user" 2>&1
  exit 1
fi
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
   echo "Please provide an ip"
   echo "Usage : ./linux_cpt.sh -ip=<IP/FQDN> -port=9000"
   exit
fi

systemctl stop osquery
url="https://$ip:$port"
url="$url"/downloads/
echo "$url"



mkdir /tmp/osquery

mkdir /opt/osquery
cd /opt/osquery

echo 'Downloading osquery bundle..'
wget -O ./osquery-4.0.2_1.linux_x86_64.tar.gz "$url"osquery-4.0.2_1.linux_x86_64.tar.gz --no-check-certificate || curl -o ./osquery-4.0.2_1.linux_x86_64.tar.gz  "$url"osquery-4.0.2_1.linux_x86_64.tar.gz -k

echo 'Extracting osquery bundle..'
tar zxvf ./osquery-4.0.2_1.linux_x86_64.tar.gz -C /tmp/osquery

cp /tmp/osquery/usr/bin/osqueryd ./osqueryd

echo 'Downloading flags file..'
wget -O ./osquery.flags "$url"osquery_linux.flags --no-check-certificate || curl -o ./osquery.flags  "$url"osquery_linux.flags -k

actual_cert_path='./certificate.crt'
final_cert_path=$PWD'/certificate.crt'

actual_secret_path='./secret.txt'
final_secret_path=$PWD'/secret.txt'

actual_flags_path='osquery.flags'
final_flags_path=$PWD'/osquery.flags'


actual_osqueryd_path='osqueryd'
final_osqueryd_path=$PWD'/osqueryd'


echo 'Downloading certificate file..'
wget  -O ./certificate.crt "$url"certificate.crt --no-check-certificate || curl  -o ./certificate.crt  "$url"certificate.crt -k

echo $PWD
sed  -i "s|${actual_cert_path}|${final_cert_path}|" osquery.flags
echo 'Downloading secret file..'
wget -O ./secret.txt "$url"secret.txt --no-check-certificate || curl -o ./secret.txt   "$url"secret.txt -k
sed -i "s|${actual_secret_path}|${final_secret_path}|" osquery.flags

wget  -O /usr/bin/osquery.sh "$url"osquery.sh --no-check-certificate || curl  -o /usr/bin/osquery.sh  "$url"osquery.sh -k
sed -i "s|${actual_flags_path}|${final_flags_path}|" /usr/bin/osquery.sh
sed -i "s|${actual_osqueryd_path}|${final_osqueryd_path}|" /usr/bin/osquery.sh

wget -O /lib/systemd/system/osquery.service  "$url"osquery.service --no-check-certificate || curl -o /lib/systemd/system/osquery.service   "$url"osquery.service -k
systemctl enable osquery
systemctl start osquery
systemctl status osquery