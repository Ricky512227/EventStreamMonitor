FROM alpine:latest
ENV TERM xterm
LABEL authors="kamalsaidevarapalli"


ENV AIRLINER_PROJECT_DIR /airliner_app
ENV AIRLINER_SRC_DIR $AIRLINER_PROJECT_DIR/src
ENV AIRLINER_VENV $AIRLINER_PROJECT_DIR/airlinervenv
ENV AIRLINER_APP $AIRLINER_SRC_DIR/app.py

ENV AIRLINER_ENV_TYPE DEVELOPMENT

WORKDIR $AIRLINER_PROJECT_DIR
COPY requirements.txt $AIRLINER_PROJECT_DIR/requirements.txt
COPY src $AIRLINER_SRC_DIR
COPY airlinervenv $AIRLINER_VENV

RUN apk add --no-cache python3 py3-pip build-base python3-dev libffi-dev


RUN pip3 install -r $AIRLINER_PROJECT_DIR/requirements.txt

ENV FLASK_ENV $AIRLINER_VENV
ENV FLASK_APP $AIRLINER_APP

CMD ["/bin/sh", "-c", "source $AIRLINER_VENV/bin/activate && flask run","--host", "0.0.0.0", "--port", "5000"]



