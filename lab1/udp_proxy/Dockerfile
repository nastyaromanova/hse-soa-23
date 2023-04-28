FROM python:3.9-alpine3.17

COPY . /lab1

RUN pip install --no-cache-dir -r /lab1/requirements_proxy.txt

CMD ["python3", "/lab1/udp_proxy.py"]