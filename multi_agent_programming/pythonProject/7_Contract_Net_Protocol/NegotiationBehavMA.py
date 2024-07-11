from spade.behaviour import CyclicBehaviour
from spade.message import Message


class NegotiationBehavMA(CyclicBehaviour):

    def __init__(self, negotiation, t1, t2):
        super().__init__()

        self.t_propose = t1
        self.t_reject = t2

        self.negotiation = negotiation
        self.proposal_count = 0
        self.best_proposal = None
        self.winner = None

    async def run(self):
        msg = await self.receive(timeout=60)
        if msg:
            thread = str(msg.thread)
            if self.t_propose.match(msg):
                print("[" + str(self.agent.jid) + "]" + " [NEGOTIATION " + thread + "] PROPOSE message" \
                      + " received from " + str(msg.sender).split('/')[0] + ": " + msg.body)
                self.proposal_count = self.proposal_count + 1
                if self.best_proposal is None or self.best_proposal < int(msg.body):
                    self.best_proposal = int(msg.body)
                    self.winner = str(msg.sender).split('/')[0]

                if self.proposal_count == len(self.negotiation['contractors']):
                    losers = [jid for jid in self.negotiation['contractors'] if not jid == self.winner]
                    for jid in losers:
                        msg = Message(to=str(jid), sender=str(self.agent.jid))
                        msg.set_metadata("performative", "REJECT")
                        msg.set_metadata("ontology", "negotiation")
                        msg.thread = thread
                        await self.send(msg)
                        print("[" + str(self.agent.jid) + "]" + " [NEGOTIATION " + thread + "] " + jid + "'s PROPOSAL REJECTED")

                    msg = Message(to=self.winner, sender=str(self.agent.jid))
                    msg.set_metadata("performative", "ACCEPT")
                    msg.set_metadata("ontology", "negotiation")
                    msg.thread = thread
                    await self.send(msg)
                    print("[" + str(self.agent.jid) + "]" + " [NEGOTIATION " + thread + "] " + self.winner + "'s PROPOSAL ACCEPTED")


