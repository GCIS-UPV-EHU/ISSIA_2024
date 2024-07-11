# IMPORT SPADE
from spade.agent import Agent
from spade import wait_until_finished

class MyAgent(Agent):
    async def setup(self):
        # DEBUG MSG

async def main():
    # INSTANCE AGENT
    # START AGENT
    await wait_until_finished(myAgent)

if __name__ == "__main__":
    # RUN main() IN SPADE'S EVENT LOOP