#!/bin/sh

while [ $# -gt 0 ]
do
    key="${1}"
case ${key} in
    -path|--path)
    OLD_PLGX_DIR_PATH="${2}"
    shift # past argument=value
    ;;

    -h|--help)
    echo "Usage : ./upgrade_script.sh -path <Old_Plgx_Server_Base_Dir_Path>"
    shift # past argument
    ;;

    *)    
    shift # past argument=value
    ;;
    
    *)
          # unknown option
    ;;
esac
done
if [ -z "$OLD_PLGX_DIR_PATH" ]
then
      echo "Please provide the existing installation directory"
      echo "Usage : ./upgrade_script.sh -path <Old_Plgx_Server_Base_Dir_Path>"
      exit

fi
echo "Provided path is" "${OLD_PLGX_DIR_PATH}"


echo "detecting the ip from existing server"
#IP_FOUND=$(cat "${OLD_PLGX_DIR_PATH}"resources/osquery.flags | grep tls_hostname | cut -d: -f1 | cut -d= -f2)

IP_FOUND=$( sed -n 's/--tls_hostname=//p' "${OLD_PLGX_DIR_PATH}"resources/osquery.flags | cut -d':' -f1)
echo "IP detected from the flags file is""${IP_FOUND}"

makeFlagsFile(){
    read -p "Enter IP to make flags file for: " NEW_IP
    sh ./osquery_flags.sh "${NEW_IP}"
}
copyCert(){
    echo "copying nginx certificate....."
    cp -r "${OLD_PLGX_DIR_PATH}"nginx/certificate.crt ./nginx/
    cp -r "${OLD_PLGX_DIR_PATH}"nginx/private.key ./nginx/

}

while true; do
    read -p "Do you wish to continue with the same IP(Y/N)?" yn
    case $yn in
        [Yy]* ) sh ./osquery_flags.sh "${IP_FOUND}"; break;;
        [Nn]* ) makeFlagsFile; break;;
        * ) echo "Please answer yes or no.";;
    esac
done

while true; do
    read -p "Do you wish to continue with the nginx certificate(Y/N)?" yn
    case $yn in
        [Yy]* ) copyCert; break;;
        [Nn]* ) break;;
        * ) echo "Please answer yes or no.";;
    esac
done

echo "PolyLogyx Server necessary files were copied Successfully!"

#end
