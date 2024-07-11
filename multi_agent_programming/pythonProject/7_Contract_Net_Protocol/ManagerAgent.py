import random
import string
import spade
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message
from spade.template import Template
from NegotiationBehavMA import NegotiationBehavMA


class SRA(Agent):

    targets = ['contractoragent1@ubuntu.min.vm', 'contractoragent2@ubuntu.min.vm', 'contractoragent3@ubuntu.min.vm']

    async def setup(self):
        b1 = self.SendCFP_Behav()
        self.add_behaviour(b1)

    class SendCFP_Behav(OneShotBehaviour):

        async def run(self):
            negotiation_criteria = "memory"
            thread = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))

            negotiation = {'thread': thread,
                           'neg_criteria': negotiation_criteria,
                           'contractors':  self.agent.targets}

            t1 = Template()
            t1.set_metadata("performative", "PROPOSE")
            t1.set_metadata("ontology", "negotiation")
            t1.thread = thread

            t2 = Template()
            t2.set_metadata("performative", "REJECT")
            t2.set_metadata("ontology", "negotiation")
            t2.thread = thread

            b = NegotiationBehavMA(negotiation, t1, t2)
            self.agent.add_behaviour(b, t1 | t2)

            for jid in self.agent.targets:
                msg = Message(to=jid, sender=str(self.agent.jid), body=negotiation_criteria)
                msg.set_metadata("performative", "CFP")
                msg.set_metadata("ontology", "negotiation")
                msg.thread = thread
                await self.send(msg)
                print("[" + str(self.agent.jid) + "]" + " CFP message sent to " + jid)


async def main():
    ma = SRA("manager1@ubuntu.min.vm", "12345")
    await ma.start(auto_register=True)
    await spade.wait_until_finished(ma)


if __name__ == "__main__":
    spade.run(main())