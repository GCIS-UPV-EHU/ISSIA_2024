""" Authors: Ane López Mena & Maite López Mena """
from spade.agent import Agent
from Behaviours.RequestBehaviour import RequestBehaviour


# ========================================================================== #
#                              ** SENDER AGENT **                            #
# ========================================================================== #
class SenderAgent(Agent):

    def __init__(self, jid, password, nService, nTarget):
        # Esta clase hereda de la clase Agent, propia de pythonWarehouse
        Agent.__init__(self, jid, password)

        # Definir atributos propios del agente Transporte:
        #  1) JID del agente
        self.id = str(jid)
        #  2) Número identificador del servicio
        self.nServ = nService
        #  3) Posición en el almacen
        self.targetPos = nTarget

        # Guardar JID + password, ya que el sender debe comunicarse con
        # los demás agentes y necesita su JID para enviarles mensajes
        self.machine_jid = "machineagent_1@ubuntu.min.vm"
        self.transport1_jid = "transportagent_1@ubuntu.min.vm"
        self.transport2_jid = "transportagent_2@ubuntu.min.vm"
        self.sender_jid = "senderagent_1@ubuntu.min.vm"
        self.passwd = "upv123"

    # -------------------------------------------------------------
    async def setup(self):
        print("[" + self.sender_jid + "] entering setup")

        # Instancia el comportamiento RequestBehaviour
        rb = RequestBehaviour(self)

        # Añade el comportamiento al agente
        self.add_behaviour(rb)

