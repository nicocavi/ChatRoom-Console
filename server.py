import socket
import threading
import psycopg2
import time

IP = "localhost"
PORT = 8000
BUFFER_SIZE = 2048

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((IP, PORT))
s.listen(100)

list_cliente = []
list_sala = []
mensajes = []

class Sala(threading.Thread):

	def __init__(self, name):
		# Inicializar clase padre.
		threading.Thread.__init__(self)
		self.name = name
		self.list_cliente_sala = []
		self.mensajes = []
		
	def addCliente(self, cliente):
		self.list_cliente_sala.append(cliente)

	def getUsers(self):
		return len(self.list_cliente_sala)

	def delCliente(self, cliente):
		self.list_cliente_sala.remove(cliente)

	def run(self):
		while True:
			while(len(self.mensajes) != 0):
				for mensaje in self.mensajes:
					m = mensaje[0]
					addr = mensaje[1]
				for cliente in self.list_cliente_sala:
					if(str(addr) != str(cliente.addr)):
						aux = "> "+str(addr) + " " + m
						try:
							cliente.conn.send(aux.encode())
						except:
							self.list_cliente_sala.remove(cliente)
				self.mensajes.remove(self.mensajes[0])

class Comando():

	def __init__(self):
		self.opciones = ["/new","/c"]

	def analisisComando(self, texto, cliente):
		comando = texto.split(" ", 1)[0]
		b= False
		for o in self.opciones:
			if(comando == o):
				b = True
		if(b):		
			self.run(comando, texto.split(" ", 1)[1], cliente)
		else:
			cliente.sala.mensajes.append([texto, cliente.addr])

	def run(self,comando, args, cliente):
		if (comando == self.opciones[0]):
			aux = existeSala(args)
			if (aux == None):
				if(cliente.sala != None):
					cliente.sala.delCliente(cliente)
				newSala = Sala(args)
				newSala.start()
				cliente.sala.mensajes.append(["Ha salido de la sala.", cliente.addr])
				list_sala.append(newSala)
				newSala.addCliente(cliente)
				cliente.addSala(newSala)
				cliente.conn.send(b"Sala creada." )
			else: 
				cliente.conn.send(b"Ya existe una sala con ese nombre, por favor elija otro.")	
		elif (comando == self.opciones[1]):
			aux = existeSala(args)
			if (aux != None):
				if(cliente.sala != None):
					cliente.sala.mensajes.append(["Ha salido de la sala.", cliente.addr])
					cliente.sala.delCliente(cliente)
				aux.addCliente(cliente)
				aux.mensajes.append(["Ha ingresado a la sala.", cliente.addr])
				cliente.addSala(aux)
			else:
				cliente.conn.send(b"No existe la sala.")

class Client(threading.Thread):

	def __init__(self, conn, addr, conPsql, curPsql):
		threading.Thread.__init__(self)
		self.curPsql = curPsql
		self.conPsql = conPsql
		self.conn = conn
		self.addr = addr
		self.sala = None

	def addSala(self, sala):
		self.sala = sala

	def run(self):
		while True:
			try:
				
				input_data = self.conn.recv(BUFFER_SIZE)
			except:
				print("Error de lectura.")
				break
			else:
				
				if input_data:
					try:
						self.curPsql.execute("""insert into mensaje (data, usuario, time) values (%s, %s, %s)""", (input_data.decode("utf-8"), str(self.addr),'NOW()'))
						self.conPsql.commit()
						comandos.analisisComando(input_data.decode(), self)
					except psycopg2.IntegrityError as error:
						print("Error en almacenar mensaje en la base de datos")

def home():
	aux = "Salas disponibles: \n\n\n"
	i = 1
	for sala in list_sala:
		aux = aux + str(i) +" || "+sala.name + "\n"
		i += 1
	return aux

def existeSala(sala):
	for i in list_sala:
		if(i.name == sala):
			return i
	return None

conPsql = psycopg2.connect("dbname=chat user=cavi password=ejemplo")
curPsql = conPsql.cursor()
print("Conexion a la BD correcta...")

sala = Sala("los cochinillos de tormes")
sala.start()

list_sala.append(sala)

comandos = Comando()

print("Creacion de Thread correcta...")

while True:

	conn, addr = s.accept()
	list_cliente.append([conn,addr,])
	c = Client(conn, addr, conPsql, curPsql)

	sala.addCliente(c)
	
	c.addSala(sala)
	c.start()

	print('Connection address:', addr)

	