import spade
from spade.agent import Agent
from behaviours.RunningBehaviour import RunningBehaviour
from behaviours.RunningBehaviour2 import RunningBehaviour2

class MyAgent(Agent):

    async def setup(self):
        print("[" + str(self.jid) + "] entering setup")

        self.rb = RunningBehaviour()
        self.add_behaviour(self.rb)
        print("[" + str(self.jid) + "] RunningBehaviour added to behaviours queue")

        self.rb2 = RunningBehaviour2()
        self.add_behaviour(self.rb2)
        print("[" + str(self.jid) + "] RunningBehaviour2 added to behaviours queue")

async def main():
    myAgent = MyAgent(# YOUR JID, # SAME PASSWD USED BEFORE)
    await myAgent.start()
    await spade.wait_until_finished(myAgent)

if __name__ == "__main__":
    spade.run(main()) # event loop