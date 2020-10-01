FROM python:3.6

# user setup
RUN groupadd -g 984 fsdrui && \
    useradd -r -u 984 -g fsdrui fsdrui

# updates and packages
RUN apt-get update \
    && apt-get -y --no-install-recommends install libxml2-dev libxmlsec1-dev libxmlsec1-openssl \
    && apt-get clean
RUN pip3 install pipenv

# infrequently-changed scripts
RUN mkdir /opt/ui
WORKDIR /opt/ui
RUN mkdir /opt/ui/scripts
COPY ./scripts ./scripts
RUN ls
RUN mkdir -p app/templates
RUN ./scripts/load_templates.sh
COPY Pipfile* ./
RUN pipenv install --deploy --system

COPY . .

USER fsdrui
EXPOSE 9293
CMD ["python3", "run.py"]
