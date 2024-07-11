from spade.behaviour import OneShotBehaviour

class BootingBehaviour(OneShotBehaviour):

    async def run(self):
        print("[" + str(self.agent.jid) + "] [BootingBehaviour] only runs once")
        print("[" + str(self.agent.jid) + "] [BootingBehaviour] set timer: 5")
        self.agent.timer = 5