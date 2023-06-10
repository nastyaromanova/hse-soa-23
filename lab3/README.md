# Voice chat using rabbitmq and sockets

## Docker rabbtmq
```
docker compose up
```

## Docker sockets
```
docker build -t aaromanova/lab3_soa . -f Dockerfile 
```

```
docker run --name voicechat -t aaromanova/lab3_soa /bin/bash
```

```
docker exec -it voicechat /bin/bash
python server.py
```

```
docker exec -it voicechat /bin/bash
python client.py
```



