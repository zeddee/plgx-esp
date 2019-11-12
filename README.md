# PolyLogyx Endpoint Security Platform (ESP) - Community Edition
PolyLogyx ESP levarages the <href>Osquery tool, with <href>PolyLogx Extension to provide endpoint visibility and monitoring at scale. To get the details of the architecture of the full platofrm, please read the [platform docs](https://github.com/polylogyx/platform-docs). This repository provides the community release of the platform which focuses on the Osquery based agent management to provide visbility into endpoint activities, query configuration management, a live query interface and alerting capabilities based on security critical events.

## Build and deploy
The platform is packaged as a Docker image and following instructions will help set the server up.
- Clone this repository on a system that has [docker-compose 1.21.1]](https://docs.docker.com/compose/install/#install-compose) (or above) and docker engine 18.03.1-CE (or above) available. (Recommended to use an Ubuntu <> system)
- Generate certificate using sh ./certificate-generate.sh <IP_ADDRESS>
- docker-compose -p 'plgx_docker' up -d

## PolyLogyx ESP Components
- [plgx_fleet](https://github.com/polylogyx/plgx-esp/src/master/plgx_fleet/README.md) - Manages requests coming from endpoint
- [plgx_fleet_ui](https://github.com/polylogyx/plgx-esp/src/master/plgx_fleet_ui/README.md) - Mangement server for taking actions, modifying properties  of an endpoint.
- RabbitMQ
- nginx
- rSysLogF
- postgres

## Agent Configuration
PolyLogyx ESP leverages osquery's TLS configuration, logger, and distributed read/write endpoints and provides a basic set of default configurations to simplify Osquery deployment. The platform also provides a Client Provisioning Tool (CPT) that wraps the agent installation via a thin installer. The CPT tool can be downloaded from the main page on the server UI which also gives the instruction on running the CPT at individual endpoint. For mass deployment, a centralized system like SCCM can be used.

## Supported Endpoints
Osquery is cross platform agent that supports 64 bit variants of Windows (7 and above), MacOS and all the popular Linux distributions (Ubuntu, Centos, RedHat etc). PolyLogyx ESP's agent is built upon Osquery and therefore the supported endpoints are the ones as supported by Osquery.

## PolyLogyx ESP API SDK
PolyLogyx ESP can be programatically interacted with using the extensive  [REST API](https://github.com/polylogyx/platform-docs/tree/master/13_Rest_API) interface. This allows for multiple use case like Incident Response, Threat Hunting, Compromise Assessment, Compliance checks etc to be easily served with the platform. This also provides an easy for integration with SOAR platforms (href demo vide of PolyLogyx Phantom video)## Integration with Big Data/Analytic systems
PolyLogyx ESP is packaged with an rSysLog container. This container can be configured to stream the query results and other logs from the endpoint population to the back-end systems like Splunk, ELK, GreyLog etc for cross-product correlation, alert enrichments and other SIEM related use cases.

## PolyLogyx ESP - Community Edition License
Please read the LICENSE file for details on the license.

## PolyLogyx ESP - Enterprise Edition
PolyLogyx ESP comes with an enterprise flavor with advanced set of features and dedicated support. More about the enterprise edition of ESP can be learned [here](https://github.com/polylogyx/platform-docs)  or send an email to info@polylogyx.com

