FROM nickgryg/alpine-pandas

RUN apk add --update tmux runit libpq libffi-dev
RUN pip install --upgrade pip 
COPY ./plgx_fleet/requirements/prod.txt /tmp/requirements.txt
RUN \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
 python3 -m pip install -r /tmp/requirements.txt  && \
 apk --purge del .build-deps
RUN pip install -r /tmp/requirements.txt 
# Copy and install our requirements first, so they can be cached
# Add our application to the container
COPY ./plgx_fleet/. /src/plgx_fleet/
COPY ./resources/. /src/plgx_fleet/resources/
COPY ./nginx/certificate.crt /src/plgx_fleet/resources/certificate.crt
RUN chmod a+x /src/plgx_fleet/docker-entrypoint.sh

ENTRYPOINT ["sh","/src/plgx_fleet/docker-entrypoint.sh"]
