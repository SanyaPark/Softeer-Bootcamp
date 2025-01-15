FROM ubuntu:24.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    curl \
    && apt-get clean

COPY W1 /workspace/

COPY W2 /workspace/

RUN python3 -m pip config set global.break-system-packages true

RUN pip3 install jupyterlab

RUN pip3 install numpy pandas matplotlib beautifulsoup4 wordcloud

WORKDIR /workspace

EXPOSE 8888

CMD [ "jupyter-lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root" ]

# how to build? -->
# docker build -t image_name:latest .
