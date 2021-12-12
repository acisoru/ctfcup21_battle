FROM ubuntu:latest
MAINTAINER tg:@greg0r0

RUN apt-get update -y
RUN apt-get install -y python3-pip python-dev build-essential
RUN python3 -m pip install numpy pycrypto flask
COPY . /app
WORKDIR /app
ENTRYPOINT [ "python3" ]
CMD ["server.py"]