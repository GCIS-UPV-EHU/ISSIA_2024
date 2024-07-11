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

            self.t = Template()
            self.t.set_metadata("performative", "request")

        async def run(self):
            print("[" + str(self.agent.jid) + "] [CommsBehaviour] entering run")

            msg = await self.receive(timeout=10)  # wait for a message for 10 seconds
            if msg:
                if self.t.match(msg):
                    print("[" + str(self.agent.jid) + "] [CommsBehaviour] message received!")
                    sender = msg.sender
                    thread = msg.thread
                    performative = msg.metadata.get('performative')
                    ontology = msg.metadata.get('ontology')
                    body = msg.body
                    print("[" + str(self.agent.jid) + "] [CommsBehaviour] message: " + str(sender) + ", " +
                          str(thread) + ", " + str(performative) + ", " + str(ontology) + ", " + str(body))

                    msg2 = Message(to=str(sender))  # Instantiate the message
                    msg2.set_metadata("performative", "accept")  # Set the "inform" performative
                    msg2.set_metadata("ontology", "myOntology")  # Set the ontology of the message content
                    msg2.thread = thread
                    msg2.body = "available"  # Set the message content

                    await self.send(msg2)
                    print("[" + str(self.agent.jid) + "] [CommsBehaviour] accept message sent")

                    await asyncio.sleep(1)

                    msg3 = Message(to=str(sender))  # Instantiate the message
                    msg3.set_metadata("performative", "reject")  # Set the "inform" performative
                    msg3.set_metadata("ontology", "myOntology")  # Set the ontology of the message content
                    msg3.thread = thread
                    msg3.body = "unavailable"  # Set the message content

                    await self.send(msg3)
                    print("[" + str(self.agent.jid) + "] [CommsBehaviour] reject message sent")
            else:
                print("[" + str(self.agent.jid) + "] [CommsBehaviour] did not received any message after 10 seconds")

    async def setup(self):
        print("[" + str(self.jid) + "] entering setup")

        self.cb = self.CommsBehaviour()
        self.add_behaviour(self.cb)
        print("[" + str(self.jid) + "] CommsBehaviour added to behaviours queue")

async def main():
    recverAgent = Recver("recver@ubuntu.min.vm", "passwd")
    await recverAgent.start()
    await spade.wait_until_finished(recverAgent)

if __name__ == "__main__":
    spade.run(main())  # event loop