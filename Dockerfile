FROM python:slim-bookworm
ENV TERM xterm
LABEL authors="kamalsaidevarapalli"

ARG AIRLINER_PROJECT_DIR=/Users/kamalsaidevarapalli/Desktop/Workshop/AirlinerAdminstration
ARG AIRLINER_SRC_DIR=$AIRLINER_PROJECT_DIR/src
ARG REGISTRATION_APP_DIR=$AIRLINER_SRC_DIR/registration_service
ARG REGISTRATION_VENV=$REGISTRATION_APP_DIR/user_venv
ARG REGISTRATION_APP=$REGISTRATION_APP_DIR/registration_service.py


WORKDIR $AIRLINER_PROJECT_DIR
COPY src $AIRLINER_SRC_DIR
COPY src/registration_service/requirements.txt $REGISTRATION_APP_DIR/requirements.txt
RUN chmod 777 -R $AIRLINER_PROJECT_DIR


RUN apt-get update && apt-get install -y python3 python3-pip build-essential python3-dev libffi-dev
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools


RUN pip3 install -r $REGISTRATION_APP_DIR/requirements.txt


EXPOSE 9091
#ENTRYPOINT ["/bin/sh", "-c", "flask run"]

CMD ["gunicorn", "-b", "0.0.0.0:9091", "src.registration_service.registration_service:registration_app"]
