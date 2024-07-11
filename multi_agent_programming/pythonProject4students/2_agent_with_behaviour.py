import spade
from spade.agent import Agent
# IMPORT CUSTOM "RunningBehaviour" BEHAVIOUR

class MyAgent(Agent):

    async def setup(self):
        print("[" + str(self.jid) + "] entering setup")

        # INSTANCE BEHAVIOUR FROM CUSTOM "RunningBehaviour" BEHAVIOUR
        # ADD BEHAVIOUR TO AGENT BEHAVIOUR QUEUE
        # DEBUG MSG

async def main():
    myAgent = MyAgent(# YOUR JID, # SAME PASSWD USED BEFORE)
    await myAgent.start()
    await spade.wait_until_finished(myAgent)

if __name__ == "__main__":
    spade.run(main()) # event loop