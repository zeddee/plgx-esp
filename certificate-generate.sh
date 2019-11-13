touch "$(dirname "$(pwd)")"/.rnd
a=$1
echo $a
if [ -e nginx/private.key ]
then
    echo "Certificate already exists. Please remove the existing certificates and then try again"
else
        openssl req -x509 -sha256 -nodes -days 365 -newkey rsa:2048 -keyout nginx/private.key -out nginx/certificate.crt -subj '/CN='$a'/O=PolyLogyx LTD./C=US'
fi

sed  's/tls_hostname=.*/tls_hostname='"$a"':9000/g' resources/osquery.flags > resources/osquery.flags1
sed  's/tls_hostname=.*/tls_hostname='"$a"':9000/g' resources/osquery_linux.flags > resources/osquery_linux.flags1
sed  's/tls_hostname=.*/tls_hostname='"$a"':9000/g' resources/linux/osquery.flags > resources/linux/osquery.flags1
sed  's/tls_hostname=.*/tls_hostname='"$a"':9000/g' resources/freebsd/osquery.flags > resources/freebsd/osquery.flags1
sed  's/tls_hostname=.*/tls_hostname='"$a"':9000/g' resources/darwin/osquery.flags > resources/darwin/osquery.flags1

rm -rf resources/osquery.flags
mv resources/osquery.flags1 resources/osquery.flags

rm -rf resources/osquery_linux.flags
mv resources/osquery_linux.flags1 resources/osquery_linux.flags

rm -rf resources/linux/osquery.flags
mv resources/linux/osquery.flags1 resources/linux/osquery.flags

rm -rf resources/darwin/osquery.flags
mv resources/darwin/osquery.flags1 resources/darwin/osquery.flags

rm -rf resources/freebsd/osquery.flags
mv resources/freebsd/osquery.flags1 resources/freebsd/osquery.flags

rm -rf "$(dirname "$(pwd)")"/.rnd
