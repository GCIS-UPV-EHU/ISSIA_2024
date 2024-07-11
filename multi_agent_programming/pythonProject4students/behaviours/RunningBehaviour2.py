import asyncio
from spade.behaviour import CyclicBehaviour

class RunningBehaviour2(CyclicBehaviour):

    async def run(self):
        print("[" + str(self.agent.jid) + "] [RunningBehaviour2] waiting for 5s...")
        await asyncio.sleep(5)
        self.agent.timer = 0
        print("[" + str(self.agent.jid) + "] [RunningBehaviour2] have I really been waiting for 5s?")


