FROM python:3.9

RUN mkdir /lab3_soa/
WORKDIR /lab3_soa/
COPY . .

RUN apt-get update
RUN apt-get install libasound-dev libportaudio2 libportaudiocpp0 portaudio19-dev -y
RUN pip install --no-cache-dir -r /lab3_soa/requirements.txt

CMD ["/bin/bash"]