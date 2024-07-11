""" Authors: Ane López Mena & Maite López Mena """
import asyncio
import time
import logging
from spade.message import Message
from spade.behaviour import CyclicBehaviour

# ========================================================================== #
#                  ** SEND DATA 2 TRANSPORT BEHAVIOUR **                     #
# ========================================================================== #
# Define el comportamiento del Agente como "CyclicBehaviour", para enviar los
# mensajes recibidos del TransportAgent al Transporte implementado mediante nodos ROS
class SendData2TransportBehaviour(CyclicBehaviour):

    def __init__(self, a):
        # Heredamos el init de la clase super
        super().__init__()
        # Definir atributos propios del agente:
        #  1) Instancia del agente que ejecuta el comportamiento
        self.myAgent = a
        #  2) Flag de control de trabajo en progreso (WorkInProgress)
        self.WIP = False

    # ------------------------------------------------------------------
    async def run(self):
        # Si el transporte no está ocupado
        if not self.WIP:
            # Queda a la espera de recibir un mensaje
            msg = await self.receive(timeout=60)
            if msg: # Se ha recibido un mensaje
                self.sender = str(msg.sender)
                print("\n[" + self.myAgent.id + "] message from " + str(msg.sender) + ": {}".format(msg.thread))

                # Si el thread del mensaje recibido es DELIVERY o COLLECTION
                if msg.thread == "DELIVERY" or  msg.thread == "COLLECTION":
                    # Marcar el flag para indicar trabajo en proceso
                    self.WIP = True

                    if self.myAgent.state == "IDLE":
                        self.agent.pub.publish("GO")
                        await asyncio.sleep(1)

                    # Se le ordena a un publicista que publique las coordenadas objetivo
                    # Para este ejemplo, son coordenadas estáticas, que representan la
                    # posición fija e invariable del almacén
                    self.myAgent.pubCoord.publish("1.43,0.59")
                    print("[" + self.myAgent.id + "] send warehouse coordinates")
                    print("[" + self.myAgent.id + "] wait while moving to warehouse")

                    await asyncio.sleep(1)
                    while not self.myAgent.state == "ACTIVE":
                        await asyncio.sleep(1)

                    # Avisar a TransportAgent de que el robot ya ha llegado a la máquina.
                    msg2 = Message(to=str(self.sender), sender=self.myAgent.id, body="ALREADY IN WAREHOUSE")
                    msg2.thread = "READY"
                    await self.send(msg2)
                    print("[" + self.myAgent.id + "] message to " + str(msg2.to) + ": {}".format(msg2.thread))

                    await asyncio.sleep(1)

                    # Coordenadas estáticas que representan la posición de ORIGEN del turtlebot3
                    self.myAgent.pubCoord.publish("-1.65,-0.56")
                    print("\n[" + self.myAgent.id + "] send collection/delivery point coordinates")
                    print("[" + self.myAgent.id + "] wait while moving to collection/delivery point")

                    await asyncio.sleep(1)
                    while not self.myAgent.state == "ACTIVE":
                        await asyncio.sleep(1)

                    self.WIP = False
