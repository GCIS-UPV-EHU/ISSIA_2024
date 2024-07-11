import random
import string
import asyncio
import spade
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message

class Sender(Agent):

    class CommsBehaviour(CyclicBehaviour):

        async def on_start(self):
            print("[" + str(self.agent.jid) + "] [CommsBehaviour] entering on_start")

            # Instantiate the message
            # Set the "inform" performative
            # Set the ontology of the message content
            msg.thread = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
            # Set the message content

            # Send msg
            print("[" + str(self.agent.jid) + "] [CommsBehaviour] message sent")

        async def run(self):
            print("[" + str(self.agent.jid) + "] [CommsBehaviour] entering run")
            await asyncio.sleep(10)

    async def setup(self):
        print("[" + str(self.jid) + "] entering setup")

        self.cb = self.CommsBehaviour()
        self.add_behaviour(self.cb)
        print("[" + str(self.jid) + "] CommsBehaviour added to behaviours queue")

async def main():
    senderAgent = Sender(# JID, # PASSWD)
    await senderAgent.start()
    await spade.wait_until_finished(senderAgent)

if __name__ == "__main__":
    spade.run(main()) # event loop