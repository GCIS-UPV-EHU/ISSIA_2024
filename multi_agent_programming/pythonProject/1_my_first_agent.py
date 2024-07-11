import spade
from spade.agent import Agent
from spade import wait_until_finished

class MyAgent(Agent):
    async def setup(self):
        print("[" + str(self.jid) + "] setup")

async def main():
    myAgent = MyAgent("myagent@ubuntu.min.vm", "passwd")
    await myAgent.start()
    await wait_until_finished(myAgent)

if __name__ == "__main__":
    spade.run(main()) # async loop