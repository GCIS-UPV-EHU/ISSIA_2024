""" Authors: Ane López Mena & Maite López Mena """
import logging
from spade.template import Template
from Agents.ResourceAgent import ResourceAgent
from spade.behaviour import FSMBehaviour, State
from Behaviours.IdleBehaviour import IdleBehaviour
from Behaviours.RunningBehaviour import RunningBehaviour
from Behaviours.NegotiationBehaviour import NegotiationBehaviour
from Behaviours.AssetManagementBehaviour import AssetManagementBehaviour

# Definir los estados del FSM
STATE_ONE = "BOOTING"
STATE_TWO = "RUNNING"
STATE_THREE = "STOPPING"
STATE_FOUR = "IDLE"

_logger = logging.getLogger(__name__)

# ========================================================================== #
#                          ** MFC RESOURCE AGENT **                          #
# ========================================================================== #
class MFCResourceAgent(ResourceAgent):

    # Heredado de la clase ResourceAgent, hace override del metodo de la clase madre
    async def setup(self):
        print("[MFCResourceAgent] entering setup")

        # Esta lista debería ser cargada a través del SRA con todos dispositivos disponibles.
        # Para esta demostración, esta lista será estática
        self.targets = ['transportagent_1@ubuntu.min.vm', 'transportagent_2@ubuntu.min.vm']

        # El comportamiento FSM implementa 2 métodos:
        #   * add_state(name:String, state:State,  initial: boolean)
        #        |__Se indican los estados que forman la máquina de estados
        #   * add_transition(source:String, dest:String)
        #        |__Se definen las transiciones entre los estados de la máquina de estados

        # Instanciar el comportamiento FSM para el agente
        fsm = FSMBehaviour()

        # Cada estado del FSM, debe estar definido con un STRING y una clase STATE
        fsm.add_state(name=STATE_ONE, state=self.StateBooting(), initial=True)
        fsm.add_state(name=STATE_TWO, state=self.StateRunning())
        fsm.add_state(name=STATE_THREE, state=self.StateStopping())
        fsm.add_state(name=STATE_FOUR, state=self.StateIdle())

        # Las transiciones definen de qué estado a que otro estado está permitido pasar
        fsm.add_transition(source=STATE_ONE, dest=STATE_TWO)
        fsm.add_transition(source=STATE_TWO, dest=STATE_THREE)
        fsm.add_transition(source=STATE_TWO, dest=STATE_FOUR)
        fsm.add_transition(source=STATE_FOUR, dest=STATE_TWO)
        fsm.add_transition(source=STATE_FOUR, dest=STATE_THREE)

        # Añadir comportamiento FSM al agente
        self.add_behaviour(fsm)

        print("[MFCResourceAgent] exiting setup")

    # ========================================================================== #
    #                           ** ESTADO 1: BOOTING **                          #
    # ========================================================================== #
    # Heredado de la clase ResourceAgent

    # ========================================================================== #
    #                           ** ESTADO 2: RUNNING **                          #
    # ========================================================================== #
    # Heredado de la clase ResourceAgent, override de la clase madre
    class StateRunning(State):

        async def run(self):
            print("[" + self.agent.id + "] entering StateRunning")

    # Este estado de RUNNING está compuesto de 3 comportamientos:
        #   1)  [Negotiation Behaviour]
        #   Comportamiento que participa en las negociaciones para la
        #   asignación de servicios (‘comportamiento de negociación’).
            nb = NegotiationBehaviour(self.agent)

            # [PLANTILLAS / TEMPLATES]
            # Son necesarias para gestionar la correcta recepción de los mensajes ACL
            # Los mensajes tienen una plantilla asociada. Los atributos para la plantilla son:
            # 1) TO: String que indica el JID del receptor del mensaje
            # 2) SENDER: String que indica el JID del emisor del mensaje
            # 3) BODY: Cuerpo del mensaje
            # 4) THREAD: El ID de la conversación
            # 5) METADATA: Diccionario (clave, valor) que define la metadata del mensaje
            template = Template()
            template.thread = "MY_VALUE"

            template2 = Template()
            template2.thread = "WINNER"

            template3 = Template()
            template3.thread = "CFP"

            # Añadir comportamiento de negociación y las plantillas para la recepción de mensajes ACL
            self.agent.add_behaviour(nb, template | template2 | template3 )
            print("[" + self.agent.id + "] adding NegotiationBehaviour")

        #   2) [Running Behaviour]
        #   Comportamiento para gestionar las peticiones de servicio que llegan de la
        #   fábrica (mensajes ACL solicitando que la máquina ejecute un servicio determinado)
            rb = RunningBehaviour(self.agent)

            # [PLANTILLAS / TEMPLATES]
            # Son necesarias para gestionar la correcta recepción de los mensajes ACL
            # -------
            # Templates para servicio: DELIVERY
            template = Template()
            template.sender = "transportagent_1@ubuntu.min.vm"
            template.sender = "senderagent_1@ubuntu.min.vm"
            template.thread = "DELIVERY"

            template2 = Template()
            template2.to = "machineagent_1@ubuntu.min.vm"
            template2.sender = "transportagent_1@ubuntu.min.vm"
            template2.thread = "READY"

            # Templates para servicio: COLLECTION
            template3 = Template()
            template3.to = "machineagent_1@ubuntu.min.vm"
            template3.sender = "senderagent_1@ubuntu.min.vm"
            template3.thread = "COLLECTION"

            template4 = Template()
            template4.to = "transportagent_1@ubuntu.min.vm"
            template4.sender = "machineagent_1@ubuntu.min.vm"
            template4.thread = "READY"

            template5 = Template()
            template5.to = "transportagent_2@ubuntu.min.vm"
            template5.sender = "machineagent_1@ubuntu.min.vm"
            template5.thread = "READY"
            # -------

            self.agent.add_behaviour(rb, template | template2 | template3 | template4 | template5)
            print("[" + self.agent.id + "] adding RunningBehaviour")

        #   3)  [Asset Management Behaviour]
        #   Comportamiento para gestionar el propio comportamiento del activo.
        #   Como parte de la gestión del comportamiento del activo, hay que definir una
        #   interfaz en la que se declaren dos métodos (sendDataToAsset y rcvDataFromAsset) para
        #   estandarizar la interacción entre un agente y su correspondiente agente pasarela.
            amb = AssetManagementBehaviour(self.agent)

            # [PLANTILLAS / TEMPLATES]
            # Son necesarias para gestionar la correcta recepción de los mensajes ACL
            # -------
            # Templates para servicio: DELIVERY
            template = Template()
            template.sender = "gwagentros_1@ubuntu.min.vm"
            template.thread = "READY"

            template2 = Template()
            template2.sender = "gwagentros_2@ubuntu.min.vm"
            template2.thread = "READY"

            template3 = Template()
            template3.sender = "gwagentopcua_1@ubuntu.min.vm"
            template3.thread = "DONE"

            # -------

            # Añade el comportamiento al estado y sus plantillas
            self.agent.add_behaviour(amb, template | template2 | template3 )
            print("[" + self.agent.id + "] adding AssetManagementBehaviour")

            # Si este comportamiento se detiene, volver a iniciarlo
            if (amb.is_killed()):
                amb.start()

            # Si terminan los tres comportamientos, pasar al siguiente estado
            if (rb.is_done() and nb.is_done() and amb.is_done()):
                self.set_next_state(STATE_THREE)

    # ========================================================================== #
    #                           ** ESTADO 3: STOPPING **                         #
    # ========================================================================== #
    # Heredado de la clase ResourceAgent

    # ========================================================================== #
    #                             ** ESTADO 4: IDLE **                           #
    # ========================================================================== #
    class StateIdle(State):
        async def run(self):
            print("[" + self.agent.id + "] entering StateIdle")

            ib = IdleBehaviour(self.agent)
            self.agent.add_behaviour(ib)
            print("[" + self.agent.id + "] adding AssetManagementBehaviour")

            # No se ha indicado un estado final, por lo que este se considera el último

