#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#      client.py
#
#      Copyright 2014 Recursos Python - www.recursospython.com
#
#
from socket import socket
import threading


TITLE = "Redi 0.1v"

# Compatibilidad con Python 3
try:
    raw_input
except NameError:
    raw_input = input
    
def recv(s):
    while True:
        input_data = s.recv(2048)
        if input_data:
            # En Python 3 recv() retorna los datos leídos
            # como un vector de bytes. Convertir a una cadena
            # en caso de ser necesario.
            print(input_data.decode("utf-8") if
                isinstance(input_data, bytes) else input_data)
           

def main():
    s = socket()
    s.connect(("localhost", 8000))
    t = threading.Thread(target=recv, args=(s,))
    t.start()


    while True:
        output_data = raw_input("> ")
        
        if output_data:
            # Enviar entrada. Comptabilidad con Python 3.
            try:
                s.send(output_data)
            except TypeError:
                s.send(bytes(output_data, "utf-8"))
            
if __name__ == "__main__":
    main()