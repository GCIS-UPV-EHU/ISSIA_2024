import asyncio
import spade
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template

class Recver(Agent):

    class CommsBehaviour(CyclicBehaviour):

        async def on_start(self):
            print("[" + str(self.agent.jid) + "] [CommsBehaviour] entering on_start")

            # INSTANCE TEMPLATE
            # CONFIGURE TEMPLATE WITH PERFORMATIVE "request"

        async def run(self):
            print("[" + str(self.agent.jid) + "] [CommsBehaviour] entering run")

            msg = await self.receive(timeout=10)  # wait for a message for 10 seconds
            if msg:
                if # MATCH MESSAGE AGAINST TEMPLATE
                    print("[" + str(self.agent.jid) + "] [CommsBehaviour] message received!")
                    sender = msg.sender
                    thread = msg.thread
                    performative = msg.metadata.get('performative')
                    ontology = msg.metadata.get('ontology')
                    body = msg.body
                    print("[" + str(self.agent.jid) + "] [CommsBehaviour] message: " + str(sender) + ", " +
                          str(thread) + ", " + str(performative) + ", " + str(ontology) + ", " + str(body))

                    # CODE MESSAGE SENDING WITH "accept" PERFORMATIVE
                    print("[" + str(self.agent.jid) + "] [CommsBehaviour] accept message sent")

                    await asyncio.sleep(1)

                    # CODE MESSAGE SENDING WITH "reject" PERFORMATIVE
                    print("[" + str(self.agent.jid) + "] [CommsBehaviour] reject message sent")
            else:
                print("[" + str(self.agent.jid) + "] [CommsBehaviour] did not received any message after 10 seconds")

    async def setup(self):
        print("[" + str(self.jid) + "] entering setup")

        self.cb = self.CommsBehaviour()
        self.add_behaviour(self.cb)
        print("[" + str(self.jid) + "] CommsBehaviour added to behaviours queue")

async def main():
    recverAgent = Recver(# YOUR JID, # SAME PASSWD USED BEFORE)
    await recverAgent.start()
    await spade.wait_until_finished(recverAgent)

if __name__ == "__main__":
    spade.run(main())  # event loop