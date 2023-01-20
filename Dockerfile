FROM python:3.10

RUN mkdir bot/
RUN mkdir bot/src/
RUN mkdir bot/logs/
RUN mkdir bot/db/

COPY requirements.txt /bot/

RUN python -m pip install -r /bot/requirements.txt

COPY bot /bot/src/

WORKDIR /bot/

EXPOSE 80:80

ENTRYPOINT ["python", "src/main.py"]