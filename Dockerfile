FROM python:3.6

WORKDIR /app
COPY . /app

RUN apt-get update \
    && apt-get -y --no-install-recommends install apt-utils xmlsec1 \
    && apt-get clean
RUN ./scripts/load_templates.sh
RUN pip3 install Flask-Cors requests pipenv
RUN pipenv install --deploy --system
RUN groupadd -g 984 fsdrui && \
    useradd -r -u 984 -g fsdrui fsdrui

USER fsdrui
EXPOSE 9293

ENTRYPOINT ["python3"]
CMD ["run.py"]
