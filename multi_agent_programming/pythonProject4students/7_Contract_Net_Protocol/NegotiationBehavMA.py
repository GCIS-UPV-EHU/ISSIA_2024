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
            if self.t_propose.match(msg): # CFP received
                print("[" + str(self.agent.jid) + "]" + " [NEGOTIATION " + thread + "] PROPOSE message" \
                      + " received from " + str(msg.sender).split('/')[0] + ": " + msg.body)

                # MANAGE MESSAGES RECEIVED FROM CONTRACTORS


