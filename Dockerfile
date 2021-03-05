FROM nickgryg/alpine-pandas:3.7.0

RUN apk add --update tmux runit libpq libffi-dev postgresql-client
RUN pip install --upgrade pip 
COPY ./plgx-esp/requirements/prod.txt /tmp/requirements.txt
RUN \
  apk add --no-cache postgresql-libs && \
  apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
  python3 -m pip install -r /tmp/requirements.txt  && \
  apk --purge del .build-deps
RUN pip install -r /tmp/requirements.txt 
# Copy and install our requirements first, so they can be cached
# Add our application to the container
COPY ./plgx-esp/. /src/plgx-esp/
COPY ./resources/. /src/plgx-esp/resources/
RUN chmod a+x /src/plgx-esp/docker-entrypoint.sh

ENTRYPOINT ["sh","/src/plgx-esp/docker-entrypoint.sh"]
