FROM ubuntu:22.04

RUN apt update
RUN apt install software-properties-common -y && \
        add-apt-repository ppa:deadsnakes/ppa && \
        apt install python3.10 python3-pip git -y

WORKDIR /slr_app

COPY slr_app/requirements.txt /slr_app/requirements.txt

RUN pip install wheel setuptools pip --upgrade && \
    pip install --no-cache-dir --upgrade -r requirements.txt \

COPY ./slr_app /slr_app/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]


