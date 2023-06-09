# Mafia game GRPC

**Простейшая реализация игры мафия с двумя мирными игроками, одним шрифом и одной мафией.**

Связь между клиентами и сервером на основе технологии gRPC. 
Когда к серверу подключаются 4 игрока, игра начинается автоматически. 
Минимальное количество игроков можно настроить в поле `MIN_USERS_NUM`.


# gRPC
```
python -m grpc_tools.protoc -I=. --python_out=. --pyi_out=. --grpc_python_out=. mafia.proto
```

# Запуск игры
**Выполнять команды нужно именно в представленном ниже порядке**

- Подгружаем образ:
```
docker build -t aaromanova/soa_mafia . -f Dockerfile
```

- Запускаем сервер:
```
docker run --name soa_mafia -t aaromanova/soa_mafia /bin/bash
python3 src/server.py
```

- Запускаем клиента:
```
docker exec -it soa_mafia /bin/bash
python3 src/client.py
```

# Доступные команды для клиента

**Для любой роли:**
- `GET_USERS` -- получить список игроков (доступно в любое время)
- `BROADCAST <text>` -- написать сообщение (днем –- для всех, ночью –- индивидуальные чаты для группы мафии и шрифов)
- `FINISH_DAY` -- проголосовать за окончание дня (доступно только днем)
- `VOTE <user_id>` -- проголосовать за казнь игрока (доступно только днем)
- `HELP` -- выводь всех доступных команд с описанием (доступно в любое время)

**Мафия:**
- `DECISION <user_id>` -- убить игрока (доступно только ночью), *нельзя убить себя или игрока с аналогичной ролью*

**Шриф:**
- `DECISION <user_id>` -- действие "проверить, является ли игрок мафией" (доступно только ночью), *нельзя проверить себя или игрока с аналогичной ролью*
- `VERIFY` -- опубликовать данные о найденной в прошедшую ночь мафии (доступно только днем)

# Реализовано
- Клиент обеспечивает:
    - Установку имени пользователя
    - Подключение к серверу по сетевому имени/адресу
    - Отображение списка подключившихся игроков
    - Автоматический вход в сессию игры, когда набирается достаточное число игроков
    - Отображение состояния игрока и действий, происходящих в игре
    - Случайный выбор действий среди возможных на каждом этапе игры 

- Сервер обеспечивает:
    - Подключение игроков
    - Рассылку уведомлений о подключившихся/отключившихся игроках
    - Создание одной сессии игры при подключении достаточного количества игроков
    - Назначение игрокам случайных ролей в соответствии с требованиями
    - Получение от игроков выбранных действий, их выполнение и изменение состояния игроков
    - Учет статуса игры и завершение игры при выигрыше мирных жителей или мафии

# Не реализовано 
- Сервер обеспечивает:
    - Возможность ведения нескольких сеансов игры одновременно, назначая каждому из сеансов уникальный идентификатор