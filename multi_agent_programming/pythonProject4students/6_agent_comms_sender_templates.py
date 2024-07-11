import random
import string
import spade
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template

class Sender(Agent):

    class CommsBehaviour(CyclicBehaviour):

        async def on_start(self):
            print("[" + str(self.agent.jid) + "] [CommsBehaviour] entering on_start")

            msg = Message(to="recver@ubuntu.min.vm")  # Instantiate the message
            msg.set_metadata("performative", "request")  # Set the "inform" FIPA performative
            msg.set_metadata("ontology", "myOntology")  # Set the ontology of the message content
            msg.thread = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
            msg.body = "transportation service"  # Set the message content

            await self.send(msg)
            print("[" + str(self.agent.jid) + "] [CommsBehaviour] message sent")

        async def run(self):
            print("[" + str(self.agent.jid) + "] [CommsBehaviour] entering run")

            msg = await self.receive(timeout=10)  # wait for a message for 10 seconds
            if msg:
                print("[" + str(self.agent.jid) + "] [CommsBehaviour] message received!")
                sender = msg.sender
                thread = msg.thread
                performative = msg.metadata.get('performative')
                ontology = msg.metadata.get('ontology')
                body = msg.body
                print("[" + str(self.agent.jid) + "] [CommsBehaviour] message: " + str(sender) + ", " +
                      str(thread) + ", " + str(performative) + ", " + str(ontology) + ", " + str(body))
            else:
                print("[" + str(self.agent.jid) + "] [CommsBehaviour] did not received any message after 10 seconds")

    async def setup(self):
        print("[" + str(self.jid) + "] entering setup")

        # INSTANCE TEMPLATE
        # CONFIGURE TEMPLATE WITH PERFORMATIVE "accept"

        self.cb = self.CommsBehaviour()
        # ADD BEHAVIOUR TO TEMPLATE
        print("[" + str(self.jid) + "] CommsBehaviour added to behaviours queue")

async def main():
    senderAgent = Sender(# YOUR JID, # SAME PASSWD USED BEFORE)
    await senderAgent.start()
    await spade.wait_until_finished(senderAgent)

if __name__ == "__main__":
    spade.run(main()) # event loop