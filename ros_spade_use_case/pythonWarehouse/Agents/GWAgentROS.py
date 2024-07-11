""" Authors: Ane López Mena & Maite López Mena """
import asyncio
import time
import rospy
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from std_msgs.msg import String
from Behaviours.SendData2TransportBehaviour import SendData2TransportBehaviour
from Behaviours.ReceiveDataFromTransportBehaviour import ReceiveDataFromTransportBehaviour

# ========================================================================== #
#                              ** GW AGENT ROS **                            #
# ========================================================================== #
class GWAgentROS(Agent):

    def __init__(self, jid, password):
        Agent.__init__(self, jid, password)
        self.id = str(jid)

    async def setup(self):
        print("[" + self.id + "] entering setup")

        # Variables de gestión del estado del transporte
        self.state = "IDLE"

        # Se ejecuta un nodo ROS correspondiente al GWAgentROS
        rospy.init_node('GWAgentROS', anonymous=True)

        # Se crean además dos nodos:
        #   1) Un PUBLISHER, que dará la señal de comienzo del servicio por el tópico (coordinateIDLE)
        self.pub = rospy.Publisher('/coordinateIDLE', String, queue_size=10)

        #   2) Otro PUBLISHER, que comunicará el destino o coordenada a la que debe desplazarse el transporte.
        #   Utiliza para ello el tópico /coordinate
        self.pubCoord = rospy.Publisher('/coordinate', String, queue_size=10)  # Coordinate, queue_size=10)

        # Instancia el comportamiento 'SendData2TransportBehaviour' para transmitir datos al transporte
        sd2t = SendData2TransportBehaviour(self)

        # Añade el comportamiento al agente
        self.add_behaviour(sd2t)
        print("[" + self.id + "] adding SendData2TransportBehaviour")

        # Instancia el comportamiento 'ReceiveDataFromTransportBehaviour' para transmitir datos al transporte
        rdft = ReceiveDataFromTransportBehaviour(self)

        # Añade el comportamiento al agente
        self.add_behaviour(rdft)
        print("[" + self.id + "] adding ReceiveDataFromTransportBehaviour")

