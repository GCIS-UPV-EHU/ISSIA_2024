import spade
from spade.agent import Agent
from behaviours.RunningBehaviour import RunningBehaviour

class MyAgent(Agent):

    async def setup(self):
        print("[" + str(self.jid) + "] entering setup")

        self.rb = RunningBehaviour()
        self.add_behaviour(self.rb)
        print("[" + str(self.jid) + "] RunningBehaviour added to behaviour queue")

async def main():
    myAgent = MyAgent("myagent@ubuntu.min.vm", "passwd")
    await myAgent.start()
    await spade.wait_until_finished(myAgent)

if __name__ == "__main__":
    spade.run(main()) # event loop