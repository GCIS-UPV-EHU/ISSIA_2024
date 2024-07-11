import spade
from spade.agent import Agent
# IMPORT "BootingBehaviour" CUSTOM BEHAVIOUR
from behaviours.RunningBehaviour import RunningBehaviour

class MyAgent(Agent):

    async def setup(self):
        print("[" + str(self.jid) + "] entering setup")

        self.rb = RunningBehaviour()
        self.add_behaviour(self.rb)
        print("[" + str(self.jid) + "] RunningBehaviour added to behaviours queue")

        # INSTANCE BEHAVIOUR FROM CUSTOM "BootingBehaviour" BEHAVIOUR
        # ADD BEHAVIOUR TO AGENT BEHAVIOUR QUEUE
        # DEBUG MSG

async def main():
    myAgent = MyAgent(# YOUR JID, # SAME PASSWD USED BEFORE)
    await myAgent.start()
    await spade.wait_until_finished(myAgent)

if __name__ == "__main__":
    spade.run(main()) # event loop