import asyncio
import time
from spade.behaviour import CyclicBehaviour

class RunningBehaviour(CyclicBehaviour):

    async def on_start(self):
        print("[" + str(self.agent.jid) + "] [RunningBehaviour] entering on_start")
        self.agent.timer = 0

    async def run(self):
        print("[" + str(self.agent.jid) + "] [RunningBehaviour] timer: {}".format(self.agent.timer))
        self.agent.timer += 1
        time.sleep(1)
        #await asyncio.sleep(1)
