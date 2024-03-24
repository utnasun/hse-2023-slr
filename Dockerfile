FROM ubuntu:22.04

RUN apt update
RUN apt install software-properties-common ffmpeg libsm6 libxext6 -y && \
        add-apt-repository ppa:deadsnakes/ppa && \
        apt install python3.10 python3-pip git -y 

COPY . project/

WORKDIR /project

RUN pip install wheel setuptools pip --upgrade && \
    pip install --no-cache-dir --upgrade -r slr_app/requirements.txt

CMD ["uvicorn", "slr_app.main:app", "--host", "0.0.0.0", "--port", "80"]


