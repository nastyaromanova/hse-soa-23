import pika
import threading
import time

index = []
index.append(0)

def listen():
    time.sleep(1)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='logs', exchange_type='fanout')

    result = channel.queue_declare(queue=username, exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(exchange='logs', queue=queue_name)

    print('> Listening. To exit press CTRL + Z')

    def callback(ch, method, properties, body):
        if body[:26] == " Displaying instructions @":
            if body[:(26 + len(username))] == " Displaying instructions @" + username:
                print(f'> {body}')
        else:
            print(f'> {body}')

    channel.basic_consume(
        queue=queue_name, on_message_callback=callback, auto_ack=True)

    channel.start_consuming()

def talk():
    while True:
        time.sleep(1)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

        channel.queue_declare(queue='serverChannel')
        message = input()
        message = username + "$$$$$" + message + "$$$$$" + str(index[0])
        channel.basic_publish(exchange='', routing_key='serverChannel', body=message)
        index[0] = index[0] + 1
        connection.close()


time.sleep(10)

print('Enter your name: ')
username = input()
messageHome = "New_User " + username
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_declare(queue='serverChannel')
channel.basic_publish(exchange='', routing_key='serverChannel', body=messageInicio)
print(" **** Connected to server ****")
connection.close()

threadListen = threading.Thread(target=listen)
threadTalk = threading.Thread(target=talk)
threadListen.start()
threadTalk.start()