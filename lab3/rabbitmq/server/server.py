#!/usr/bin/env python
import pika
import threading
from datetime import datetime
import time

userIds = []   

try:
    time.sleep(10)

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='serverChannel')


    def callback(ch, method, properties, body):

        print("received: " + str(body).replace("$$$$$", " "))
        
        if body[:14] == "New_user ":
            userIds.append(str(body[14:]))

            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host='localhost'))
            channel = connection.channel()

            channel.exchange_declare(exchange='logs', exchange_type='fanout')

            result = channel.queue_declare(queue=body[14:], exclusive=True)
            queue_name = result.method.queue

            channel.queue_bind(exchange='logs', queue=body[14:])
            connection.close()

            now = now = datetime.now()
            current_time = now.strftime("%H:%M:%S")            

            log = open("log.txt","a")
            log.write("User login " + str(body[14:]) + "     ID: " + str(userIds.index(body[14:])) + "       Time: "+current_time +"\n")
            log.close()

        else:
            receivedUser = str(body).split("$$$$$") 
            mensaje = receivedUser[0] + ": " + receivedUser[1]
            idmensaje = str(userIds.index(receivedUser[0])) + "." + receivedUser[2]
            log = open("log.txt","a")
            now = now = datetime.now()
            current_time = now.strftime("%H:%M:%S")            
            log.write(mensaje + "      ID: " + idmensaje +"        TIME: " + current_time +"\n")
            log.close()

            if receivedUser[1] == "@historial":
                historial = " Desplegando instruccion @" + str(receivedUser[0] + "\n")  
                log = open("log.txt","r")
                longname = len(receivedUser[0])
                for linea in log:
                    if linea[:longname] == receivedUser[0]: 
                        historial = historial + "      [H]" + linea + "\n"
                log.close()
                connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host='localhost'))
                channel = connection.channel()

                channel.exchange_declare(exchange='logs', exchange_type='fanout')

                channel.basic_publish(exchange='logs', routing_key='', body=historial)
                connection.close()

            if receivedUser[1] == "@users":
                available = " Displaying instructions @" + str(receivedUser[0] + "\n")
                for usuario in userIds:
                    available = available + "       *" + str(usuario) + "ID: " + str(userIds.index(usuario))

                connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host='localhost'))
                channel = connection.channel()

                channel.exchange_declare(exchange='logs', exchange_type='fanout')

                channel.basic_publish(exchange='logs', routing_key='', body=available)
                connection.close()
                
            else:
                connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host='localhost'))
                channel = connection.channel()

                channel.exchange_declare(exchange='logs', exchange_type='fanout')

                channel.basic_publish(exchange='logs', routing_key='', body=mensaje)
                connection.close()

    channel.basic_consume(
        queue='serverChannel', on_message_callback=callback, auto_ack=True)
    print('> Press CTRL + C')
    channel.start_consuming()

finally:
    channel.close()