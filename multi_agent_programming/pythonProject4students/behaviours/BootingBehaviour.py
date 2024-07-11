# IMPORT "OneShotBehaviour" PATTERN BEHAVIOUR

class BootingBehaviour(# "OneShotBehaviour" PATTERN BEHAVIOUR):

    async def run(self):
        print("[" + str(self.agent.jid) + "] [BootingBehaviour] only runs once")
        # INITIALIZE "timer" attribute on the agent to 5

