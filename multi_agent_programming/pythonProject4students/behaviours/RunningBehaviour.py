import time
# IMPORT "CyclicBehaviour" PATTERN BEHAVIOUR

class RunningBehaviour(# "CyclicBehaviour" PATTERN BEHAVIOUR):

    async def on_start(self):
        print("[" + str(self.agent.jid) + "] [RunningBehaviour] entering on_start")
        # INITIALIZE "timer" attribute on the agent to 0

    async def run(self):
        print("[" + str(self.agent.jid) + "] [RunningBehaviour] timer: {}".format(self.agent.timer))
        # INCREMENT "timer" attribute"
        time.sleep(1)
