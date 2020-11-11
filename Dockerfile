FROM python:3.8

# user setup
RUN groupadd -g 984 fsdrui && \
    useradd -r -u 984 -g fsdrui fsdrui

# updates and packages
RUN apt-get update \
    && apt-get -y --no-install-recommends install libxml2-dev libxmlsec1-dev libxmlsec1-openssl \
    && apt-get clean
RUN pip3 install pipenv

# infrequently-changed scripts
RUN mkdir -p /opt/app
WORKDIR /opt/app
COPY ./scripts/load_templates.sh .
RUN ./load_templates.sh
COPY Pipfile* ./
RUN pipenv install --deploy --system

COPY ./fsdr-ui .

USER fsdrui
EXPOSE 9293
CMD ["python3", "run.py"]
