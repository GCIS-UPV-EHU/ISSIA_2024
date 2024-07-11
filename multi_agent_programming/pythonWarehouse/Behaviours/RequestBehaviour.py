""" Authors: Ane López Mena & Maite López Mena """
from spade.message import Message
from spade.behaviour import OneShotBehaviour

# ========================================================================== #
#                           ** REQUEST BEHAVIOUR **                          #
# ========================================================================== #
# Define el comportamiento del Agente como "OneShotBehaviour"
class RequestBehaviour(OneShotBehaviour):

    def __init__(self, a):
        # Heredamos el init de la clase super
        super().__init__()
        # Definir atributos propios del agente:
        #  1) Instancia del agente que ejecuta el comportamiento
        self.myAgent = a

    # ------------------------------------------------------------------

    async def run(self):
        # Servicio 1: DELIVERY
        if (self.myAgent.nServ == 1):
            # 1) Envía mensaje de solicitud a TransportAgent
            # Define el mensaje : TO, SENDER Y THREAD
            msg2send = Message(to=str(self.myAgent.transport1_jid),
                               sender=self.myAgent.id,
                               body="DELIVERY:" + str(self.myAgent.targetPos))
            msg2send.thread = "DELIVERY"

            # Envía al mensaje a TransportAgent
            await self.send(msg2send)
            print("[" + self.myAgent.id + "] message to " + self.myAgent.transport1_jid)

        # Servicio 2: COLLECTION
        else:
            # 1) Envía mensaje de solicitud a MachineAgent
            # Define el mensaje : TO, SENDER Y THREAD
            msg2send = Message(to = self.myAgent.machine_jid,
                               sender=self.myAgent.id,
                               body="COLLECTION:" + str(self.myAgent.targetPos))
            msg2send.thread = "COLLECTION"

            # Envía al mensaje a MachineAgent
            await self.send(msg2send)
            print("[" + self.myAgent.id + "] message to " + self.myAgent.machine_jid)
