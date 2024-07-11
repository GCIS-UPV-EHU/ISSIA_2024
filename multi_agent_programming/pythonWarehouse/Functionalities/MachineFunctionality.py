""" Authors: Ane López Mena & Maite López Mena """
from spade.message import Message
from RAInterface import RAInterface
from Agents.GWAgentOPCUA import GWAgentOPCUA

# ========================================================================== #
#                      ** MACHINE FUNCTIONALITY **                           #
# ========================================================================== #
# Esta clase heredará dos métodos de la interfaz 'RAInterface'
#   1) rcvDataFromAsset
#   2) sendDataToAsset
class MachineFunctionality(RAInterface):
    #   [BOOTING BEHAVIOUR]
    async def init(self, myAgent):
        # Método de inicialización del agente MÁQUINA
        print("[" + myAgent.id + "] booting")

        # Inicializar variables:
        #   1) Flag WIP (WorkInProgress)
        self.WIP = False
        #   2) Flag AskForProposals, para iniciar la negociación
        self.askForProposals = False
        #   3) JID del ganador de la negociación
        self.winner_jid = ""

        # Guardar JID + password de GWAgentOPCUA
        gw_jid = "gwagentopcua_" + myAgent.id.split('_')[1]
        myAgent.gw_jid = gw_jid
        passwd = "upv123"

        # Instanciar el GWAgentOPCUA que enviará una solicitud al Asset Físico (PLC).
        ga = GWAgentOPCUA(gw_jid, passwd)
        await ga.start()

        print("[" + myAgent.id + "] booting finished")

# ============================================================================================================
#   [RUNNING BEHAVIOUR]
    async def execute(self, behav, myAgent):
        # Método de ejecución de las funcionalidades del agente máquina. Aquí, el agente se
        # quedará a la escucha de mensajes, y tras recibir una petición, la añadirá al plan de máquina
        print("[" + myAgent.id + "] running")

        if not myAgent.ready:
            myAgent.ready = True

        # A espera de recibir mensajes
        receivedMsg = await behav.receive(timeout=60)

        if receivedMsg:
            print("\n[" + myAgent.id + "] message from " + str(receivedMsg.sender) + ": {}".format(receivedMsg.body))

            # Añadir petición al plan de transporte
            myAgent.machinePlan.append(receivedMsg.body)
            print("[" + myAgent.id + "] request added to machinePlan: " + str(myAgent.machinePlan))

        else:
            # No ha recibido mensaje en un intervalo de 1 minuto
            print("[" + myAgent.id + "] No message received within 60 seconds\n")

# ============================================================================================================
#   [ASSET MANAGEMENT BEHAVIOUR]
    async def sendDataToAsset(self, behav, myAgent):
        # Evalúa el valor de un flag de “trabajo en proceso”(WIP) para determinar
        # si un recurso físico está disponible. Si es así, también comprueba las peticiones de
        # servicio pendientes relacionadas con el recurso (plan de máquina).
        # Si se dan esas condiciones, la información relativa a la siguiente petición de servicio
        # se envía al gateway (pasarela). Una vez se haya envíado la información, el flag “trabajo
        # en proceso” se activa para bloquear el envío de nueva información, hasta que el servicio actual
        # se haya completado (WIP=True).

        # Si no hay trabajo en progreso y hay tareas pendientes
        if (not self.WIP and len(myAgent.machinePlan) > 0):

            # Coge la primera tarea de la lista
            task = myAgent.machinePlan[0]

            # Identifica el tipo de tarea
            taskType = task.split(":")[0]
            # Obtiene la posición del almacén
            target = task.split(":")[1]

            # Si el servicio es "DELIVERY"
            if (taskType == "DELIVERY"):

                # Se marca como 'ocupado'
                self.WIP = True

                # Instancia un mensaje e informa a GWAgent OPCUA mediante el thread 'READY'
                msg2send = Message(to=myAgent.gw_jid, sender=myAgent.id, body=str(task))
                msg2send.thread = "READY"

                # Envía al mensaje al GWAgentOPCUA
                await behav.send(msg2send)
                print("[" + myAgent.id + "] message to " + str(msg2send.to) + ": {}".format(msg2send.body))

            # Si el servicio es "COLLECTION"
            else:
                # Se marca como 'ocupado'
                self.WIP = True

                # Instancia un mensaje e informa a GWAgent OPCUA mediante el thread 'COLLECTION'
                msg2send = Message(to=myAgent.gw_jid, sender=myAgent.id, body=str(task))
                msg2send.thread = "COLLECTION"

                # Envía al mensaje al GWAgentOPCUA
                await behav.send(msg2send)
                print("[" + myAgent.id + "] message to " + str(msg2send.to) + ": {}".format(msg2send.body))

    # ----------------------------------------------------------------------------------------------------
    async def rcvDataFromAsset(self, behav, myAgent):
        # Si el servicio se ha completado, su información es borrada de la cola de servicios asociados
        # a un recurso y el flag “trabajo en proceso” es desactivado (WIP=False).

        # Espera al mensaje que indica que la tarea ha terminado
        receivedMsg = await behav.receive()

        # Si recibe un mensaje
        if receivedMsg:

            # Tarea finalizada
            task = myAgent.machinePlan[0]
            print("\n[" + myAgent.id + "] task " + str(task) + " finished")

            # Quitar tarea del plan de máquina
            myAgent.machinePlan.pop(0)
            print("[" + myAgent.id + "] request removed from MachinePlan: " + str(myAgent.machinePlan))

            # Desactivar el flag WIP para permitir la recepción de nuevas tareas encoladas
            self.WIP = False

            # Identifica el tipo de tarea
            taskType = str(task).split(":")[0]
            # Si el tipo de servicio es 'COLLECTION'
            if (taskType == "COLLECTION"):
                # [NEGOCIACIÓN TRANSPORTE]
                # Activar señal para comienzo de negociación entre transportes
                self.askForProposals = True

# ============================================================================================================
#   [NEGOTIATION BEHAVIOUR]
    async def negotiation(self, behav, myAgent):
    # Este método implementa el algoritmo de negociación entre los agentes transporte disponibles en la planta.
    # El agente máquina manda un mensaje CFP (Call For Proposals) a todos los transportes disponibles (los que
    # están registrados; se supone que dicha lista se obtendría a través del SRA). Ese mensaje incluye, a su vez,
    # dicha lista (parámetro “contractors”) y el criterio de negociación (parámetro “negotiationCriteria” del
    # contenido del mensaje).

    # Para determinar quién ejecutará el servicio, se toma como criterio de selección el nivel de batería más alto.
    # Es decir, siempre realizará el porte el recurso que disponga de más batería en el momento de la negociación.

        # Si se activa la señal de solicitud de negociación
        if (self.askForProposals):

            self.WIP = False

            # Prepara el cuerpo del mensaje a enviar a todos los transportes de la planta (contractors+negotiationCriteria)
            CFPmsg = "contractors="+str(myAgent.targets)+"#negotiationCriteria=battery".replace('"', "")

            print()
            print("[" + myAgent.id + "] request a transportation service")
            print("[" + myAgent.id + "] start negotiation: call for proposal")

            # El agente máquina envía un mensaje CFP (Call For Proposals) a TODOS los transportes disponibles
            for jid in myAgent.targets:
                print("[" + myAgent.id + "] CFP message to " + jid)
                msg2Send = Message(to=jid, sender=myAgent.id, body=str(CFPmsg))
                msg2Send.thread = "CFP"
                await behav.send(msg2Send)
            print()

            # Esperar a la respuesta del 'ganador'
            replyMsg = await behav.receive(timeout=360)
            myAgent.winner = replyMsg.body

            # Si el ganador ha respondido
            if replyMsg:
                winner = replyMsg.body
                print("\n[" + myAgent.id + "] winner is " + str(winner))

            if (winner):
                # Guardar JID del ganador
                self.winner_jid = str(winner)

                # Desactivar flag de negocicación
                self.askForProposals  = False

                # Envíar solicitud de servicio al TransportAgent ganador con el thread 'COLLECTION'
                msg2Send = Message(to=winner, sender=myAgent.id, body=str("COLLECTION"))
                msg2Send.thread = "READY"
                await behav.send(msg2Send)
                print("[" + myAgent.id + "] message to " + winner + ": {}".format(msg2Send.body))

# ============================================================================================================
#   [STOPPING BEHAVIOUR]
    def stop(self):
        print("            + OK!\n")

# ============================================================================================================
#   [IDLE BEHAVIOUR]
    def idle(self):
        print("Machine status: IDLE")