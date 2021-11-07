FROM debian:stable-slim
WORKDIR .
COPY . .
RUN apt update && apt install python3-pip -y
RUN pip3 install -e .
