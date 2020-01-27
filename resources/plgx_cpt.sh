#!/bin/sh
#
# IMPORTANT! If osquery is not installed, it will be installed.

_PROJECT="POLYLOGYX"

_SECRET_LINUX=/etc/osquery/secret.txt
_FLAGS_LINUX=/etc/osquery/osquery.flags
_CERT_LINUX=/etc/osquery/certificate.crt

_SECRET_OSX=/private/var/osquery/secret.txt
_FLAGS_OSX=/private/var/osquery/osquery.flags
_CERT_OSX=/private/var/osquery/certificate.crt

_PLIST_OSX=/Library/LaunchDaemons/com.facebook.osqueryd.plist
_OSQUERY_PLIST=/private/var/osquery/com.facebook.osqueryd.plist

_SECRET_FREEBSD=/usr/local/etc/secret.txt
_FLAGS_FREEBSD=/usr/local/etc/osquery.flags
_CERT_FREEBSD=/usr/local/etc/certificate.crt

_OSQUERY_PKG="darwin/osquery-4.0.2.pkg"
_OSQUERY_DEB="linux/osquery_4.0.2_1.linux.amd64.deb"
_OSQUERY_RPM="linux/osquery-4.0.2-1.linux.x86_64.rpm"

_OSQUERY_SERVICE_LINUX="osqueryd"
_OSQUERY_SERVICE_OSX="com.facebook.osqueryd"
_OSQUERY_SERVICE_FREEBSD="osqueryd"

_SECRET_FILE=""
_FLAGS=""
_CERT=""
_SERVICE=""
_ACTION=""
_LINUX_FLAVOUR=""
_BASE_URL=""

parseCLArgs(){
  port="9000"
  while [ $# -gt 0 ]
  do
    key="${1}"
  case ${key} in
    -i)
    ip="${2}"
    shift # past argument=value
    ;;
    -port)
    port="${2}"
    shift # past argument=value
    ;;
    -p)
    _ACTION="install"
    shift # past argument=value
    ;;
    -u)
    if [ ${2}  = 'd' ]
    then
      _ACTION='uninstall'
    fi 
    shift # past argument=value
    ;;
    
    -h|--help)
    echo "Usage : ./plgx_cpt.sh -p -ip <IP/FQDN> -port 9000"
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

  
  if [ $_ACTION = 'install' ]; then
    if  [ -z "$ip" ]; then
      echo "Please provide an ip"
      echo "Usage : ./plgx_cpt.sh -p -i <IP/FQDN> -port 9000"
      exit
    else
      _install
    fi
  elif [ $_ACTION = 'uninstall' ]; then
    _uninstall
  else
    echo "Usage : ./plgx_cpt.sh -p -i <IP/FQDN> -port 9000"
  fi
}

whatOS() {
  OS=$(echo `uname`|tr '[:upper:]' '[:lower:]')
  log "OS=$OS"
  if [ "$OS" = "linux" ]; then
    distro=$(/usr/bin/rpm -q -f /usr/bin/rpm >/dev/null 2>&1)
    if [ "$?" = "0" ]; then
      log "RPM based system detected"
      _LINUX_FLAVOUR="rpm"
	else
      _LINUX_FLAVOUR="debian"	
      log "Debian based system detected"
    fi
  fi   
}

downloadDependents() {
  _BASE_URL="https://$ip:$port"
  _BASE_URL="$_BASE_URL"/downloads/
  echo "$_BASE_URL"

  echo "Downloading flags file, secret file, cert file for $OS os"
  if [ "$OS" = "linux" ]; then
    mkdir -p /etc/osquery
    curl -o /etc/osquery/osquery.flags  "$_BASE_URL"linux/osquery.flags -k || wget -O /etc/osquery/osquery.flags "$_BASE_URL"linux/osquery.flags --no-check-certificate
    curl -o /etc/osquery/secret.txt   "$_BASE_URL"secret.txt -k || wget -O /etc/osquery/secret.txt "$_BASE_URL"secret.txt --no-check-certificate
    curl -o /etc/osquery/certificate.crt  "$_BASE_URL"certificate.crt -k || wget  -O /etc/osquery/certificate.crt "$_BASE_URL"certificate.crt --no-check-certificate 
  fi
  if [ "$OS" = "darwin" ]; then
    mkdir -p /private/var/osquery
    curl -o /private/var/osquery/osquery.flags  "$_BASE_URL"darwin/osquery.flags -k || wget -O /private/var/osquery/osquery.flags "$_BASE_URL"darwin/osquery.flags --no-check-certificate
    curl -o /private/var/osquery/secret.txt  "$_BASE_URL"secret.txt -k|| wget -O /private/var/osquery/secret.txt "$_BASE_URL"secret.txt --no-check-certificate
    curl -o /private/var/osquery/certificate.crt  "$_BASE_URL"certificate.crt -k || wget  -O /private/var/osquery/certificate.crt "$_BASE_URL"certificate.crt --no-check-certificate
  fi
  if [ "$OS" = "freebsd" ]; then
    mkdir -p /usr/local/etc
    curl -o /usr/local/etc/osquery.flags  "$_BASE_URL"freebsd/osquery.flags -k || wget -O /usr/local/etc/osquery.flags "$_BASE_URL"freebsd/osquery.flags --no-check-certificate
    curl -o /usr/local/etc/secret.txt   "$_BASE_URL"secret.txt -k || wget -O /usr/local/etc/secret.txt "$_BASE_URL"secret.txt --no-check-certificate
    curl -o /usr/local/etc/certificate.crt  "$_BASE_URL"certificate.crt -k || wget  -O /usr/local/etc/certificate.crt "$_BASE_URL"certificate.crt --no-check-certificate
  fi
}


fail() {
  echo "[!] $1"
  exit 1
}

log() {
  echo "[+] $1"
}

installOsquery() {
  _OSQUERY_RPM="$_BASE_URL$_OSQUERY_RPM"
  _OSQUERY_DEB="$_BASE_URL$_OSQUERY_DEB"
  _OSQUERY_PKG="$_BASE_URL$_OSQUERY_PKG"
  echo $_OSQUERY_PKG
  log "Installing osquery for $OS"
  if [ "$OS" = "linux" ]; then
    if [ $_LINUX_FLAVOUR = "rpm" ]; then
      _RPM="$(echo $_OSQUERY_RPM | cut -d"/" -f6)"
      sudo curl -# "$_OSQUERY_RPM" -o "/tmp/$_RPM" -k
      sudo rpm -ivh "/tmp/$_RPM"
    else
      _DEB="$(echo $_OSQUERY_DEB | cut -d"/" -f6)"
      sudo curl -# "$_OSQUERY_DEB" -o "/tmp/$_DEB" -k
      sudo dpkg -i "/tmp/$_DEB"
    fi
  fi
  if [ "$OS" = "darwin" ]; then
    _PKG="$(echo $_OSQUERY_PKG | cut -d"/" -f6)"
    sudo curl -# "$_OSQUERY_PKG" -o "/tmp/$_PKG" -k
    sudo installer -pkg "/tmp/$_PKG" -target /
  fi
  if [ "$OS" = "freebsd" ]; then
    sudo ASSUME_ALWAYS_YES=YES pkg install osquery
  fi
  log "Installed osquery for $OS"
}

verifyOsquery() {
   installOsquery
}

prepareDependents() {
  if [ "$OS" = "linux" ]; then
    _SECRET_FILE="$_SECRET_LINUX"
    _FLAGS="$_FLAGS_LINUX"
    _CERT="$_CERT_LINUX"
    _SERVICE="$_OSQUERY_SERVICE_LINUX"
  fi
  if [ "$OS" = "darwin" ]; then
    _SECRET_FILE="$_SECRET_OSX"
    _FLAGS="$_FLAGS_OSX"
    _CERT="$_CERT_OSX"
    _SERVICE="$_OSQUERY_SERVICE_OSX"
  fi
  if [ "$OS" = "freebsd" ]; then
    _SECRET_FILE="$_SECRET_FREEBSD"
    _FLAGS="$_FLAGS_FREEBSD"
    _CERT="$_CERT_FREEBSD"
    _SERVICE="$_OSQUERY_SERVICE_FREEBSD"
  fi
  log "_SECRET_FILE=$_SECRET_FILE"
  log "_FLAGS=$_FLAGS"
  log "_CERT=$_CERT"
  log "IMPORTANT! If osquery is not installed, it will be installed."
}

stopOsquery() {
  if [ "$OS" = "linux" ]; then
    log "Stopping $_OSQUERY_SERVICE_LINUX"
    if which systemctl >/dev/null; then
      sudo systemctl stop "$_OSQUERY_SERVICE_LINUX"
    elif which service >/dev/null; then
      sudo service "$_OSQUERY_SERVICE_LINUX" stop
    else
      sudo /etc/init.d/"$_OSQUERY_SERVICE_LINUX" stop
    fi
  fi
  if [ "$OS" = "darwin" ]; then
    log "Stopping $_OSQUERY_SERVICE_OSX"
    if launchctl list | grep -qcm1 "$_OSQUERY_SERVICE_OSX"; then
      sudo launchctl unload "$_PLIST_OSX"
    fi
  fi
  if [ "$OS" = "freebsd" ]; then
    log "Stopping $_OSQUERY_SERVICE_FREEBSD"
    if [ "$(service osqueryd onestatus)" = "osqueryd is running." ]; then
      sudo service "$_OSQUERY_SERVICE_FREEBSD" onestop
    fi
  fi
}

startOsquery() {
  if [ "$OS" = "linux" ]; then
    log "Starting $_OSQUERY_SERVICE_LINUX"
    if which systemctl >/dev/null; then
      sudo systemctl start "$_OSQUERY_SERVICE_LINUX"
      sudo systemctl enable "$_OSQUERY_SERVICE_LINUX"
    else
      sudo /etc/init.d/"$_OSQUERY_SERVICE_LINUX" start
      sudo update-rc.d "$_OSQUERY_SERVICE_LINUX" defaults
    fi
  fi
  if [ "$OS" = "darwin" ]; then
    log "Starting $_OSQUERY_SERVICE_OSX"
    sudo cp "$_OSQUERY_PLIST" "$_PLIST_OSX"
    sudo launchctl load "$_PLIST_OSX"
  fi
  if [ "$OS" = "freebsd" ]; then
    log "Starting $_OSQUERY_SERVICE_FREEBSD"
    echo 'osqueryd_enable="YES"' | sudo tee -a /etc/rc.conf
    sudo service "$_OSQUERY_SERVICE_FREEBSD" start
  fi
}


stopOsqueryAndRemoveService() {
  if [ "$OS" = "linux" ]; then
    log "Stopping $_OSQUERY_SERVICE_LINUX"
    if which systemctl >/dev/null; then
      sudo systemctl stop "$_OSQUERY_SERVICE_LINUX"
      sudo systemctl disable "$_OSQUERY_SERVICE_LINUX"
    elif which service >/dev/null; then
      sudo service "$_OSQUERY_SERVICE_LINUX" stop
      echo manual | sudo tee "/etc/init/$_OSQUERY_SERVICE_LINUX.override"
    else
      sudo /etc/init.d/"$_OSQUERY_SERVICE_LINUX" stop
      sudo update-rc.d -f "$_OSQUERY_SERVICE_LINUX" remove
    fi
    if [ $_LINUX_FLAVOUR = "rpm" ]; then
      log "RPM based system detected"
	  sudo rpm -e osquery 
    else
      log "DEB based system detected"
	  sudo apt-get autoremove osquery
    fi
  fi
  if [ "$OS" = "darwin" ]; then
    log "Stopping $_OSQUERY_SERVICE_OSX"
    if launchctl list | grep -qcm1 "$_OSQUERY_SERVICE_OSX"; then
      sudo launchctl unload "$_PLIST_OSX"
      sudo rm -f "$_PLIST_OSX"
    fi
    cd /
    sudo pkgutil --only-files --files com.facebook.osquery | tr '\n' '\0' | xargs -n 1 -0 sudo rm -f
	sudo rm -rf /private/var/osquery
    #sudo pkgutil --only-dirs --files com.facebook.osquery | tr '\n' '\0' | xargs -o -n 1 -0 sudo rm -ir
	sudo pkgutil --forget com.facebook.osquery
  fi
  if [ "$OS" = "freebsd" ]; then
    log "Stopping $_OSQUERY_SERVICE_FREEBSD"
    if [ "$(service osqueryd onestatus)" = "osqueryd is running." ]; then
      sudo service "$_OSQUERY_SERVICE_FREEBSD" onestop
    fi
    sudo pkg delete osquery
    cat /etc/rc.conf | grep "osqueryd_enable" | sed 's/YES/NO/g' | sudo tee /etc/rc.conf
  fi
}

removeSecret() {
  log "Removing osquery secret: $_SECRET_FILE"
  sudo rm -f "$_SECRET_FILE"
}

removeFlags() {
  log "Removing osquery flags: $_FLAGS"
  sudo rm -f "$_FLAGS"
}

removeCert() {
  log "Removing osquery certificate"
  sudo rm -f "$_CERT"
}
removeDB() {
  log "Removing osquery db"
  sudo rm -f /tmp/osquery.pid
  sudo rm -f /tmp/osquery.db

}

bye() {
  result=$?
  if [ "$result" != "0" ]; then
    if [ "$_ACTION" = "install" ]; then
      echo "[!] Fail to enroll $_PROJECT node"
    else
      echo "[!] Fail to remove $_PROJECT node"
    fi
  fi
  exit $result
}

_install() {
  downloadDependents
  prepareDependents
  verifyOsquery
  stopOsquery
  startOsquery

  log "Congratulations! The node has been enrolled in $_PROJECT"
  log "REMINDER! $_SERVICE has been started and enabled."
}

_uninstall() {
  stopOsqueryAndRemoveService
  removeSecret
  removeFlags
  removeCert
  
  log "Congratulations! The node has been removed from $_PROJECT"
  log "WARNING! $_SERVICE has been stopped and disabled."
}
trap "bye" EXIT
whatOS
set -e
parseCLArgs "$@"

# EOF