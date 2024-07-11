""" Authors: Ane López Mena & Maite López Mena """
import logging
import time
from opcua import Client
from spade.agent import Agent
from spade.template import Template
from Behaviours.ReceiveBehaviour import ReceiveBehaviour

# ========================================================================== #
#                             ** GW AGENT OPCUA **                           #
# ========================================================================== #
class GWAgentOPCUA(Agent):

    def __init__(self, jid, password):
        Agent.__init__(self, jid, password)
        # Definir atributos propios del agente Transporte:
        #  1) JID del agente
        self.id = str(jid)

        #print("[" + self.id + "] setting OPC UA client")
        #self.client = Client("opc.tcp://192.168.0.101:4840")
        #print("[" + self.id + "] connecting to OPC UA server")
        #self.client.connect()

        # Llevar máquina a producción normal
        #self.machineSetUp()

        #self.client.close_session()

    async def setup(self):
        print("[" + self.id + "] entering setup")

        # Instancia el comportamiento ReceiveBehaviour
        rb = ReceiveBehaviour(self)

        # [PLANTILLAS / TEMPLATES]
        #    | Son necesarias para gestionar la correcta recepción de los mensajes ACL
        # -------
        template = Template()
        template.thread = "READY"
        template.to = "gwagentopcua_1@ubuntu.min.vm"
        template.sender = "machineagent_1@ubuntu.min.vm"

        template2 = Template()
        template2.thread = "COLLECTION"
        template2.to = "gwagentopcua_1@ubuntu.min.vm"
        template2.sender = "machineagent_1@ubuntu.min.vm"
        # -------

        # Añade el comportamiento al agente y la plantilla para que sepa que "formato" de mensaje espera
        self.add_behaviour(rb, template | template2)
        print("[" + self.id + "] adding ReceiveBehaviour")

    def machineSetUp(self):
        # Instanciar nodos
        node_AuxInit = self.client.get_node("ns=4;i=9")
        node_Marcha = self.client.get_node("ns=4;i=7")

        # ------- Simular arranque de máquina
        node_AuxInit.set_value(True)
        time.sleep(1)
        node_AuxInit.set_value(False)

        # ------- Simular pulso de "Marcha"
        node_Marcha.set_value(True)
        time.sleep(1)
        node_Marcha.set_value(False)
