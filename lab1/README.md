# Docker. Сокеты. Сериализация и десериализация данных

**Задача:** реализовать приложение для тестирования различных форматов сериализации.

## Подробности реализации

### Dockerfile

- Ссылаемся на базовый образ из публичного репозитория.
```
FROM python:3.9-alpine3.17
```

- Копируем в контейнер все папки и файлы в /lab1
```
COPY . /lab1
```

- Файл `requirements.txt` используется для установки всех необходимых зависимостей. Запускается с помощью команды с параметром, который отключает кэширование:
```
RUN pip install --no-cache-dir -r requirements.txt
```

### Docker Compose

Подробное описание создания данного файла находится в комментариях [docker-compose.yaml](docker-compose.yaml).

### Идея решения
Идея решения заключается в создании proxy-сервиса, который принимает json-запросы от клиента по адресу `0.0.0.0:2000`, выполняет некий парсинг полученного запроса и в зависимости от него выполняет одно из двух действий:

- Если приходит обычный запрос (то есть `request['method'] != 'all'`), то proxy-сервис адресует запрос на необходимый контейнер и потом ждет результата с этого контейнера.
- Если приходит запрос `all`, то proxy-сервис интерпретирует запрос в multicast запрос и тогда все развёрнутые экземпляры приложения возвращают результат своих вычислений. 

Реализация обычного и мультикаст запросов происходит с помощью двух отдельных threads для обычных запросов и для мультикаст запросов, которые работают на определенных адресах. 

Решение реализовано на языке `Python`. Время выполнения сериализации и десериализации измеряется с помощью библиотеки `timeit`. 

Также выполнено дополнительное задание на 0.5 баллов (публикация образов в docker-hub и использование этих образов в docker-compose):
- Собираем два образа `aaromanova/lab1_server:latest` и `aaromanova/lab1_proxy:latest`.
```
docker build . -f udp_server/Dockerfile -t lab1_server
docker build . -f udp_proxy/Dockerfile -t lab1_proxy
```

- Создаем тег, который ссылается на образ
```
docker tag lab1_server aaromanova/lab1_server
docker tag lab1_proxy aaromanova/lab1_proxy
```

- Загружаем образ в реестр
```
docker push aaromanova/lab1_server
docker push aaromanova/lab1_proxy
```

### Входные параметры

- Тестируемая структура
```
data = {
    'number' : 1488,
    'float' : 3.141592,
    'bool' : True,
    'string' : 'some_string',
    'list_number' : [1, 2, 3, 4],
    'list_string': ['one', 'two', 'three', 'four'],
    'dict': {'one' : 1, 'two' : 2, 'three' : 3, 'four' : 4}
}
```

- Время сериализации и десериализации измеряется в `ms`, которое вычисляется как из среднее 1000 итераций сериализации и десериализации.

### Используемые источники

- [Docker и docker-compose](https://habr.com/ru/articles/694872/) для настройки docker и docker-compose
- [Docker-compose](https://ru.hexlet.io/courses/docker-basics/lessons/docker-compose/theory_unit) для настройки docker-compose
- [Transports and Protocols in Python](https://docs.python.org/3/library/asyncio-protocol.html) для асинхронных протоколов 
- [Threading in Python](https://docs.python.org/3/library/threading.html) для использования thread
- [Socket in Python](https://docs.python.org/3/library/socket.html) для использования socket и выбора правильных параметров
- [Timeit in Python](https://docs.python.org/3/library/timeit.html) для замера времени выполнения сериализации и десериализации

## Взаимодействие с сервисом

### Работа с контейнером

- Сборка производится с помощью команды
```
docker compose build
```

- Запуск производится с помощью команды
```
docker-compose up
```

### Формат запросов
В данном решении доступен следующий список тестируемых форматов:
1.   Нативный вариант сериализации (в зависимости от языка)
2.   XML
3.   JSON
4.   Google Protocol Buffers
5.   Apache Avro
6.   YAML
7.   MessagePack

Каждый из них в запросе имеет соответствующее название из списка `["native", "json", "xml", "protobuf", "avro", "yaml", "msgpack"]`, которое не чувствительно к регистру.

- Для запроса некоторых методов из списка выше используется команда
```
{"type" : "get_result", "method" : /* список тестируемых форматов */}
```
Например
```
{"type" : "get_result", "method" : "native"}    # если метод один
{"type" : "get_result", "method" : ["protobuf", "yaml"]}
{"type" : "get_result", "method" : ["XML", "AvRo"]}
{"type" : "get_result", "method" : ["native", "json", "xml", "protobuf", "avro", "yaml", "msgpack"]}
```

- Для запроса всех методов используется команда
```
{"type" : "get_result", "method" : "all"}
```

## Результаты (с обработкой ошибок)
![Image](/lab1/images/results.png)


