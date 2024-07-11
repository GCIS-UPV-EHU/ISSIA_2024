import spade
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour

class Recver(Agent):

    class CommsBehaviour(CyclicBehaviour):

        async def on_start(self):
            print("[" + str(self.agent.jid) + "] [CommsBehaviour] entering on_start")

        async def run(self):
            print("[" + str(self.agent.jid) + "] [CommsBehaviour] entering run")

            # wait for a message for 10 seconds
            if msg:
                print("[" + str(self.agent.jid) + "] [CommsBehaviour] message received!")
                sender = # Get sender from msg
                thread = # Get thread from msg
                performative = # Get performative from msg
                ontology = # Get ontology from msg
                body = # Get body from msg
                print("[" + str(self.agent.jid) + "] [CommsBehaviour] message: " + str(sender) + ", " +
                      str(thread) + ", " + str(performative) + ", " + str(ontology) + ", " + str(body))
            else:
                print("[" + str(self.agent.jid) + "] [CommsBehaviour] did not received any message after 10 seconds")

    async def setup(self):
        print("[" + str(self.jid) + "] entering setup")

        self.cb = self.CommsBehaviour()
        self.add_behaviour(self.cb)
        print("[" + str(self.jid) + "] CommsBehaviour added to behaviours queue")

async def main():
    recverAgent = Recver(# JID, # PASSWD)
    await recverAgent.start()
    await spade.wait_until_finished(recverAgent)

if __name__ == "__main__":
    spade.run(main())  # event loop