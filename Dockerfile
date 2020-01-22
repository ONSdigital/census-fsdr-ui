FROM python:3.6

WORKDIR /app
COPY . /app
EXPOSE 9293
RUN pip3 install Flask-Cors requests
RUN pip3 install pipenv && pipenv install --deploy --system
RUN groupadd -g 984 fsdrui && \
    useradd -r -u 984 -g fsdrui fsdrui
USER fsdrui
ENTRYPOINT ["python3"]
CMD ["run.py"]
