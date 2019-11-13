FROM nickgryg/alpine-pandas

RUN apk add --update tmux runit libpq libffi-dev
RUN pip install --upgrade pip 
COPY ./plgx_esp/requirements/prod.txt /tmp/requirements.txt
RUN \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
 python3 -m pip install -r /tmp/requirements.txt  && \
 apk --purge del .build-deps
RUN pip install -r /tmp/requirements.txt 
# Copy and install our requirements first, so they can be cached
# Add our application to the container
COPY ./plgx_esp/. /src/plgx_esp/
COPY ./resources/. /src/plgx_esp/resources/
COPY ./nginx/certificate.crt /src/plgx_esp/resources/certificate.crt
RUN chmod a+x /src/plgx_esp/docker-entrypoint.sh

ENTRYPOINT ["sh","/src/plgx_esp/docker-entrypoint.sh"]
