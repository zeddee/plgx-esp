# PolyLogyx Endpoint Visibility And Control Platform

## Endpoint Visibilty And Control At Scale
PolyLogyx Endpoint Visibility and Control platform is built on a osquery community provided 'doorman' fleet manager. 
The platform is packaged as a Docker image and following instruction will help set the server up 


## Environment needed

### Build
git
plgx_fleet
plgx_fleet_ui
rSyslog
postgres - 9.6 and above
redis  - 5.0.2 and above
rabbitMQ - 3.7 and above



### Docker
git
docker-compose: 1.21.1 (or above)
docker: 18.03.1-CE

  
## Components
- [plgx_fleet](https://bitbucket.org/polylogyx/plgx-osq-server/src/master/plgx_fleet/README.md) - Manages requests coming from endpoint
- [plgx_fleet_ui](https://bitbucket.org/polylogyx/plgx-osq-server/src/master/plgx_fleet_ui/README.md) - Mangement server for taking actions, modifying properties  of an endpoint.
- RabbitMQ
- nginx
- rSysLogF
- redis
- postgres
- Premantel

## Running As a Docker 
Generate certificates : sh ./certificate-generate.sh <IP_Address>
docker-compose up

## git setup
https://www.atlassian.com/git/tutorials/install-git
Follow the link to install git
