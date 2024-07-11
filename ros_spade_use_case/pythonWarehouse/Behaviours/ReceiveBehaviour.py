""" Authors: Ane López Mena & Maite López Mena """
import asyncio
import random
import time
import logging
import opcua.ua
from opcua import Client
from spade.message import Message
from spade.behaviour import CyclicBehaviour

# ========================================================================== #
#                          ** RECEIVE BEHAVIOUR **                           #
# ========================================================================== #
# Define el comportamiento del Agente como "CyclicBehaviour"
class ReceiveBehaviour(CyclicBehaviour):

    def __init__(self, a):
        # Heredamos el init de la clase super
        super().__init__()
        # Definir atributos propios del agente:
        #  1) Instancia del agente que ejecuta el comportamiento
        self.myAgent = a

    async def run(self):
        # Queda a la espera de recibir un mensaje
        msg = await self.receive()

        # Si recibe un mensaje:
        if msg:
            # Se configura la información de logging: Imprime líneas con información sobre la conexión

            print("\n[" + self.myAgent.id + "] message from " + str(msg.sender) + ": {}".format(msg.body))

            # Se extraen del mensaje recibido el tipo de servicio y la posición
            taskType = str(msg.body).split(":")[0]
            target = str(msg.body).split(":")[1]

            # Si el tipo de servicio es 'DELIVERY'
            if taskType == "DELIVERY":
                print("[" + self.myAgent.id + "] introduce package into shelf " + str(target))

                result = await self.sendDataOPCUA(taskType, target)

                if (result == "FINISHED"):
                    print("[" + self.myAgent.id + "] package stored")

                    # Mensaje para actualizar plan de máquina
                    msg2Send = Message(to=str(msg.sender), sender=str(self.myAgent.id))
                    msg2Send.thread = "DONE"

                    # Envía al mensaje al GWAgent
                    await self.send(msg2Send)
                else:
                    print("[" + self.myAgent.id + "] shelf " + str(target) +" is already occupied")

            else:
                # Si el tipo de servicio es 'COLLECTION'
                print("[" + self.myAgent.id + "] extract package from shelf " + str(target))

                result = await self.sendDataOPCUA(taskType, target)

                if (result == "FINISHED"):
                    print("[" + self.myAgent.id + "] package extracted")

                    # Mensaje para actualizar plan de máquina
                    msg2Send = Message(to=str(msg.sender), sender=str(self.myAgent.id))
                    msg2Send.thread = "DONE"

                    # Envía al mensaje al GWAgent
                    await self.send(msg2Send)
                else:
                    print("[" + self.myAgent.id + "] shelf No. " + str(target) + " empty")

# ====================================================================

    async def sendDataOPCUA(self, serviceType, target):
    # En este método se realiza toda la lógica de lectura/escritura de nodos
    # publicados en la interfaz del servidor OPC UA

        print("[" + self.myAgent.id + "] set OPC UA client")
        self.myAgent.client = Client("opc.tcp://192.168.0.101:4840")
        print("[" + self.myAgent.id + "] connect to OPC UA server")
        self.myAgent.client.connect()

        # Instanciar nodos con los que se realizarán las operaciones rw
        node_Reset = self.myAgent.client.get_node("ns=4;i=8")
        node_DejarCoger = self.myAgent.client.get_node("ns=4;i=10")
        node_Posicion = self.myAgent.client.get_node("ns=4;i=66")
        node_NewService = self.myAgent.client.get_node("ns=4;i=67")
        node_ServiceFinished = self.myAgent.client.get_node("ns=4;i=68")
        node_AlmacenOcupacion = self.myAgent.client.get_node("ns=4;i=11")

        print("[" + self.myAgent.id + "] check availability")
        busy = node_NewService.get_value()
        if busy:
            print("[" + self.myAgent.id + "] warehouse busy")
            while busy:
                espera = random.uniform(0, 50)
                print("[" + self.myAgent.id + "] waiting " + str(espera) + "s...")
                await asyncio.sleep(espera)
                busy = node_NewService.get_value()

        # Comprobar si la acción es realizable
        ok = self.servicePossible(node_AlmacenOcupacion, serviceType, int(target))
        if ok:

            # --------- Prod. Normal ------------
            # Escribir tipo de servicio solicitado
            # INTRODUCIR ( CogerDejar = 1 )
            if (serviceType == 'DELIVERY'):
                node_DejarCoger.set_value(True)
            # EXTRAER ( CogerDejar = 0 )
            else:
                node_DejarCoger.set_value(False)
            print("[" + self.myAgent.id + "] set operation " + serviceType + " in PLC")

            # Escribir posición objetivo de la solicitud
            node_Posicion.set_value(int(target), varianttype=opcua.ua.VariantType.Int16)
            print("[" + self.myAgent.id + "] set position " + str(target) + " in PLC")

            # Simular pulso de Reset
            node_Reset.set_value(True)
            node_Reset.set_value(False)
            print("[" + self.myAgent.id + "] action started in PLC")

            # Crear una variable que notifica del estado del proceso.
            # Cuando haya terminado la tarea, se pondrá en True
            finished = node_ServiceFinished.get_value()
            while not finished:
                await asyncio.sleep(1)
                finished = node_ServiceFinished.get_value()

            print("[" + self.myAgent.id + "] action finished in PLC")

            self.myAgent.client.close_session()

            # Devolver señal de tarea FINALIZADA
            return "FINISHED"

        else:
            self.myAgent.client.close_session()

            # Devolver señal de ERROR
            return "ERROR"

    def servicePossible(self, node_AlmacenOcupacion, service, target):
    # Este método permite saber si la operación solicitada puede realizarse
    # o si existe algún problema que no permita su puesta en marcha.

        # Obtener matriz de ocupación del almacén
        warehouseOcupation = node_AlmacenOcupacion.get_value()

        # Si se quiere INTRODUCIR Y la posición está ocupada
        if (service == 'DELIVERY' and warehouseOcupation[target - 1] == True):
            return False
        # Si se quiere EXTRAER Y la posición está vacía
        if (service == 'COLLECTION' and warehouseOcupation[target - 1] == False):
            return False

        return True
