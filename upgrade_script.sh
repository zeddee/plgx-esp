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

length=${#OLD_PLGX_DIR_PATH}
last_char=${OLD_PLGX_DIR_PATH:length-1:1}

[[ $last_char != "/" ]] && OLD_PLGX_DIR_PATH="$OLD_PLGX_DIR_PATH/"; :

if [ -z "$OLD_PLGX_DIR_PATH" ]; then
      echo "Please provide the existing installation directory"
      echo "Usage : ./upgrade_script.sh -path <Old_Plgx_Server_Base_Dir_Path>"
      exit
elif [ ! -d $OLD_PLGX_DIR_PATH ]; then
      echo "Provided path is" "${OLD_PLGX_DIR_PATH}"
      echo "Please provide a valid installation directory"
      echo "Usage : ./upgrade_script.sh -path <Old_Plgx_Server_Base_Dir_Path>"
      exit

fi
echo "Provided path is" "${OLD_PLGX_DIR_PATH}"


echo "Detecting the ip from existing installation.."
if [ -f ${OLD_PLGX_DIR_PATH}resources/osquery.flags ] ; then
   SERVER_IP=$( sed -n 's/--tls_hostname=//p' "${OLD_PLGX_DIR_PATH}"resources/osquery.flags | cut -d':' -f1)
   echo "IP detected from the flags file is ""${SERVER_IP}"
elif [ -f ${OLD_PLGX_DIR_PATH}resources/windows/x64/osquery.flags ] ; then
   SERVER_IP=$( sed -n 's/--tls_hostname=//p' "${OLD_PLGX_DIR_PATH}"resources/windows/x64/osquery.flags | cut -d':' -f1)
   echo "IP detected from the flags file is ""${SERVER_IP}"
else
   echo "Unable to detect the existing flags file"
fi



if [ -f ${OLD_PLGX_DIR_PATH}.env ] ; then
    CREDENTIALS=("RABBITMQ_URL" "POSTGRES_ADDRESS" "POSTGRES_PORT" "POSTGRES_DB_NAME" "POSTGRES_DB" "POSTGRES_USER" "POSTGRES_PASSWORD" "ENROLL_SECRET" "RSYSLOG_FORWARDING")
    for i in "${CREDENTIALS[@]}"; do
        sed -i 's/'$i'=.*/'$i'='"$( sed -n 's/'$i'=//p' "${OLD_PLGX_DIR_PATH}".env | cut -d':' -f1)"'/g' "$(pwd)/.env"
    done
    echo "Postgres credentials and rabbitmq URL are copied successfully from the existing POLYLOGYX server folder path!"
else
    echo "Unable to detect the existing .env file"
fi



makeFlagsFile(){
      while true; do
    		read -p "Enter IP to make flags file for: " NEW_IP
    		if [[ -z "$NEW_IP" ]]; then
   				printf '%s\n' "No input entered"
    		elif ! valid_ip "$NEW_IP"; then
    		    echo "Please provide a valid server ip"
	
			else
 				sh ./osquery_flags.sh "${NEW_IP}"
 				echo "Flags file updated successfully with server ip"
 				break
			fi  
	  done
}
copyCert(){
    cp -r "${OLD_PLGX_DIR_PATH}"nginx/certificate.crt ./nginx/
    cp -r "${OLD_PLGX_DIR_PATH}"nginx/private.key ./nginx/
    echo "Certificates copied successfully."
}


valid_ip(){
	ip=$1
    local  stat=1
	
    if [[ $ip == localhost ]] || [[ $ip =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
        OIFS=$IFS
        IFS='.'
        ip=($ip)
        IFS=$OIFS
        [[ ${ip[0]} -le 255 && ${ip[1]} -le 255 \
            && ${ip[2]} -le 255 && ${ip[3]} -le 255 ]]
        stat=$?
    fi
    return $stat
}



if test -z "$SERVER_IP"; then
      makeFlagsFile
else
      while true; do
    		read -p "Do you wish to continue with the same IP(Y/N)?" yn
    		case $yn in
        		[Yy]* ) sh ./osquery_flags.sh "${SERVER_IP}"; echo "Flags file updated successfully with server ip"; break;;
        		[Nn]* ) makeFlagsFile; break;;
        		* ) echo "Please answer yes or no.";;
    		esac    
	  done
fi

echo "Copying SSL certificate....."


if ! [ -f ${OLD_PLGX_DIR_PATH}nginx/certificate.crt ] && [ -f ${OLD_PLGX_DIR_PATH}nginx/private.key ] ; then
    echo "Could not find existing certificates. Please copy the certificates under the nginx directory or generate new one using 'bash certificate-generate.sh <SERVER_IP>'"

else
	while true; do
    	read -p "Do you wish to continue with the existing certificate(Y/N)?" yn
    	case $yn in
        	[Yy]* ) copyCert; break;;
        	[Nn]* ) echo "Please copy the certificates under the nginx directory or generate new one using 'bash certificate-generate.sh <SERVER_IP>'"; break;;
        	* ) echo "Please answer yes or no.";;
    	esac
	done
fi
echo "Stopping plgx-esp-ui container to avoid port mapping confusion between nginx and plgx-esp-ui container"
sudo docker stop "$(sudo docker ps -a | grep 'plgx-esp_plgx-esp-ui' | awk '{ print $1 }')"

echo "To build the server run : docker-compose -p 'plgx-esp' up --build -d"

# end
