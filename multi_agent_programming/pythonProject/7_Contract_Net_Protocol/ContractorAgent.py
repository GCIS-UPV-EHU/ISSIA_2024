import spade
from spade.agent import Agent
from spade.template import Template
from RunningBehavCA import RunningBehavCA


class ContractorAgent(Agent):

    async def setup(self):
        t1 = Template()
        t1.set_metadata("performative", "CFP")
        t1.set_metadata("ontology", "negotiation")

        t2 = Template()
        t2.set_metadata("performative", "ACCEPT")
        t2.set_metadata("ontology", "negotiation")

        t3 = Template()
        t3.set_metadata("performative", "REJECT")
        t3.set_metadata("ontology", "negotiation")

        rb = RunningBehavCA(t1, t2, t3)
        self.add_behaviour(rb, t1 | t2 | t3)

async def main():
    contractor1_jid = "contractoragent1@ubuntu.min.vm"
    contractor2_jid = "contractoragent2@ubuntu.min.vm"
    contractor3_jid = "contractoragent3@ubuntu.min.vm"
    passwd = "passwd"

    ca1 = ContractorAgent(contractor1_jid, passwd)
    await ca1.start(auto_register=True)
    ca2 = ContractorAgent(contractor2_jid, passwd)
    await ca2.start(auto_register=True)
    ca3 = ContractorAgent(contractor3_jid, passwd)
    await ca3.start(auto_register=True)

    await spade.wait_until_finished(ca1)
    await spade.wait_until_finished(ca2)
    await spade.wait_until_finished(ca3)


if __name__ == "__main__":
    spade.run(main())