FROM python:3.9

RUN mkdir /lab2_soa/
WORKDIR /lab2_soa/
COPY /src/requirements.txt .

RUN apt-get update
RUN pip install --no-cache-dir -r /lab2_soa/requirements.txt

COPY . .
ENV PYTHONPATH "${PYTHONPATH}:/lab2_soa"

CMD ["/bin/bash"]