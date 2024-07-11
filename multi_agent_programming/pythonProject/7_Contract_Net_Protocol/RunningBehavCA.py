import random
from spade.behaviour import CyclicBehaviour
from spade.message import Message


class RunningBehavCA(CyclicBehaviour):

    def __init__(self, t1, t2, t3):
        super().__init__()

        self.t_CFP = t1
        self.t_accept = t2
        self.t_reject = t3

        self.value = random.randint(0, 1024)

    async def on_start(self):
        print("[" + str(self.agent.jid) + "]" + " starting")

    async def run(self):
        msg = await self.receive(timeout=60)
        if msg:
            thread = str(msg.thread)
            if self.t_CFP.match(msg):
                print("[" + str(self.agent.jid) + "]" + " [NEGOTIATION " + thread + "] " + str(self.value))
                msg2 = Message(to=str(msg.sender), sender=str(self.agent.jid), body=str(self.value))
                msg2.set_metadata("performative", "PROPOSE")
                msg2.set_metadata("ontology", "negotiation")
                msg2.thread = thread
                await self.send(msg2)

            elif self.t_reject.match(msg): # si el msg recibido es un REJECT, hará match
                print("[" + str(self.agent.jid) + "]" + " [NEGOTIATION " + thread + "] REJECTION received")

            elif self.t_accept.match(msg):  # si el msg recibido es un ACCEPT, hará match
                print("[" + str(self.agent.jid) + "]" + " [NEGOTIATION " + thread + "] ACCEPTANCE received")

        else:
            print("[" + str(self.agent.jid) + "]" + " [RUNNING] Did not received any message after 60 seconds")