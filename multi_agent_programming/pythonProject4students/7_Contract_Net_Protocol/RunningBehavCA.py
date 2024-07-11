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
            # MANAGE MESSAGES RECEIVED FROM MANAGER

        else:
            print("[" + str(self.agent.jid) + "]" + " [RUNNING] Did not received any message after 60 seconds")