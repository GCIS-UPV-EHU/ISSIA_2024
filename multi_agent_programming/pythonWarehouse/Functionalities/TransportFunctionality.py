""" Authors: Ane López Mena & Maite López Mena """
import time
from spade.message import Message
from RAInterface import RAInterface
from Agents.GWAgentROS import GWAgentROS

# ========================================================================== #
#                      ** TRANSPORT FUNCTIONALITY **                           #
# ========================================================================== #
# Esta clase heredará dos métodos de la interfaz 'RAInterface'
#   1) rcvDataFromAsset
#   2) sendDataToAsset
class TransportFunctionality(RAInterface):
    #   [BOOTING BEHAVIOUR]
    async def init(self, myAgent):
        # Método de inicialización del agente TRANSPORTE
        print("[" + myAgent.id + "] booting")

        # Inicializar variables:
        #   1) Flag WIP (WorkInProgress)
        self.WIP = False
        #   2) Estado inicial / predefinido
        self.state = "ACTIVE"

        # Guardar JID + password de GWAgentROS
        gw_jid = "gwagentros_" + myAgent.id.split('_')[1]
        myAgent.gw_jid = gw_jid
        passwd = "upv123"

        # Instanciar el GWAgentROS para comunicarse con al Asset Físico (AGV).
        ga = GWAgentROS(gw_jid, passwd)
        await ga.start()

        print("[" + myAgent.id + "] booting finished")

# ==========================================================================
#   [RUNNING BEHAVIOUR]
    async def execute(self, behav, myAgent):
        # Método de ejecución de las funcionalidades del agente trasnporte. Aquí, el agente se
        # quedará a la escucha de mensajes, y tras recibir una petición, la añadirá al plan de transporte
        print("[" + myAgent.id + "] running")

        if not myAgent.ready:
            myAgent.ready = True

        # A espera de recibir mensajes
        receivedMsg = await behav.receive(timeout=360)

        # Si recibe un mensaje de solicitud de servicio, lo añade al plan de transporte
        if receivedMsg:
            print("\n[" + myAgent.id + "] message from " + str(receivedMsg.sender) + ": {}".format(receivedMsg.body))

            # Añadir petición al plan de transporte
            myAgent.transportPlan.append(receivedMsg.body)
            print("[" + myAgent.id + "] request added to TransportPlan: " + str(myAgent.transportPlan))
        else:
            # No ha recibido mensaje en un intervalo de 360 segundos
            print("[" + myAgent.id + "] No message received in a while\n")

# ============================================================================================================
#   [NEGOTIATION BEHAVIOUR]
    async def negotiation(self, behav, myAgent):
    # El algoritmo de negociación, tiene 4 fases[0-3]:

    # Variables de control:
        # 1) Paso de la negociación
        step = 0
        # 2) Número de respuestas recibidas
        replyNum = 0

        # Queda a la espera del mensaje CFP (Call For Proposals)
        CFPmsg = await behav.receive(timeout=360)
        print("[" + myAgent.id + "] CFP message from " + str(CFPmsg.sender))

        # Extracción de datos del mensaje:
        data = CFPmsg.body.split("#")
        # Lista de recursos transporte disponibles = CANDIDATOS
        contractors = (data[0].split("=")[1])
        targets = contractors.strip('][').split(', ')
        # Negotiation criteria = BATERÍA MÁX.
        criteria = data[1].split("=")[1]

        # Este criterio puede ser diferente según el sistema que se quiera implementar,
        # por tanto, es mejor parametrizarlo
        if (criteria == "battery"):
            myValue = myAgent.battery

        # Si hay más de un transporte disponible (más de 1 candidato)
        if (len(targets)>1):

            # [PASO 0] ________________________________________________________________________
            #   | Se envían mensajes ACL al resto de agentes con los que desea negociar.
            #   | Dichos mensajes incluyen el valor del criterio con el que se desea negociar.

            if (step == 0):
                # Para cada uno de los candidatos
                for jid in targets:
                    # Quitar caracter "'"
                    jid = jid.replace("'", "")

                    # Si no es el JID propio, enviar mensaje
                    if (jid != myAgent.id):
                        msg2send = Message(to=str(jid).replace("'", ""),
                                           sender=str(myAgent.id),
                                           body=str(str(myAgent.id) + "," + str(myValue)))

                        # Settea thread como 'MY_VALUE'
                        msg2send.thread = "MY_VALUE"

                        # Envía al mensaje al otro transport agent
                        print("[" + myAgent.id + "] proposal message to " + str(jid))
                        await behav.send(msg2send)
                # Pasar a la siguiente etapa
                step = 1

            # [PASO 1] _____________________________________________________________________________
            #   | Se compara el valor propio con los valores recibidos por parte de otros agentes.
            #   | Mientras no se reciban los mensajes de todos los agentes y el valor propio sea mejor
            #   | que los valores recibidos hasta el momento, se permanece a la espera de recibir los
            #   | mensajes co2n los valores restantes. Si, en algún momento, se detecta que el valor
            #   | propio es peor, se salta al paso 3 y se sale de la negociación. Si, una vez recibidos
            #   | todos los mensajes, el valor propio sigue siendo el mejor, se salta al paso 2.

            if (step == 1):
                # Queda a la espera de mensaje
                replyMsg = await behav.receive(timeout=360)

                if replyMsg:
                    sender_jid = str(replyMsg.body.split(",")[0])
                    sender_value = str(replyMsg.body.split(",")[1])
                    print("[" + myAgent.id + "] proposal message from " + str(sender_jid) + ": battery " + str(sender_value))

                    # Si se detecta que el valor propio es peor, se salta al paso 3
                    if (int(sender_value) > myValue):
                        # Sale de la negociación
                        print("[" + myAgent.id + "] negotiation lost")
                        step = 3
                    replyNum = replyNum + 1

                    if (replyNum >= len(targets)-1):
                        if (step == 3):
                            pass
                        else:
                            # Si, una vez recibidos todos los mensajes, el valor propio sigue siendo el mejor,
                            # se salta al paso 2. Se declara el transport agent como ganador
                            step = 2
            # [PASO 2] _____________________________________________________________________________
            #   | Se informa al agente que solicitó la negociación de que este agente es el ganador
            #   | de la negociación.
            if (step == 2):
                print("[" + myAgent.id + "] negotiation win")
                # Se notifica que hay ganador mediante el thread 'WINNER'
                msg2send = Message(to='machineagent_1@ubuntu.min.vm', sender=myAgent.id, body=str(myAgent.id))

                # Settea el thread
                msg2send.thread = "WINNER"

                # Se envía el mensaje
                await behav.send(msg2send)

                # Se marca el propio agente como ganador
                myAgent.winner = True

            # [PASO 3] _____________________________________________________________________________
            #   | Salir de la negociación cuando se ha perdido.
            if (step == 3):
                myAgent.winner = False
                step = 4
            # [DEFAULT]
            if (step == 4):
                pass

        else:
            # Sólo hay un transporte disponible (por lo tanto, es el único y es el winner)
            msg2send = Message(to='machineagent_1@ubuntu.min.vm', sender=myAgent.id, body=str(myAgent.id))

            # Settea la clave "performative" como "inform"
            msg2send.thread = "WINNER"

            # Envía al mensaje al resto de candidatos
            await behav.send(msg2send)
            myAgent.winner = True

# ============================================================================================================
#   [ASSET MANAGEMENT BEHAVIOUR]
    async def rcvDataFromAsset(self, behav, myAgent):
        # Evalúa el valor de un flag de “trabajo en proceso” (WIP) para determinar
        # si un recurso físico está disponible.
        if self.WIP:
            print("[" + myAgent.id + "] wait message from " + myAgent.gw_jid)
            receivedMsg = await behav.receive(timeout=500)
            if receivedMsg.thread == "READY":

                # Obtener la tarea finalizada
                task = myAgent.transportPlan[0]
                print("[" + myAgent.id + "] task " + str(task) + " finished")

                # Quitar tarea del plan del transporte, puesto que ya se ha realizado con éxito
                myAgent.transportPlan.pop(0)
                print("[" + myAgent.id + "] request removed from TransportPlan: " + str(myAgent.transportPlan))

                # Marcar el recurso como DISPONIBLE
                self.WIP = False

                # Obtener tipo de servicio
                taskType = task.split(":")[0]
                # Si la tarea realizada ha sido de tipo 'DELIVERY'
                if (taskType == "DELIVERY"):
                    # Enviar una solicitud de servicio a MACHINE AGENT
                    print("[" + myAgent.id + "] service request to machineagent_1@ubuntu.min.vm")
                    # Generar el mensaje para enviar
                    msg2send = Message(to="machineagent_1@ubuntu.min.vm", sender=myAgent.id, body=str(task))
                    # Settear el thread como 'READY'
                    msg2send.thread = "READY"
                    # Envía al mensaje
                    await behav.send(msg2send)

# ----------------------------------------------------------------------------------------------------
    async def sendDataToAsset(self, behav, myAgent):
        # Evalúa el valor de un flag de “trabajo en proceso”(WIP) para determinar
        # si un recurso físico está disponible. Si es así, también comprueba las peticiones de
        # servicio pendientes relacionadas con el recurso (plan de transporte).
        # Si se dan esas condiciones, la información relativa a la siguiente petición de servicio
        # se envía al gateway (pasarela). Una vez se haya envíado la información, el flag “trabajo
        # en proceso” se activa para bloquear el envío de nueva información, hasta que el servicio actual
        # se haya completado (WIP=True).

        # Procesar las tareas del plan de transporte
        if (not self.WIP and len(myAgent.transportPlan) > 0):

            # Marcar el transporte como OCUPADO
            self.WIP = True

            # Obtener tarea
            task = myAgent.transportPlan[0]
            # Obtener tipo de servicio a realizar
            taskType = task.split(":")[0]

            # Instancia el mensaje a enviar:
            msg2send = Message(to=myAgent.gw_jid, sender=myAgent.id, body=str(taskType))
            msg2send.thread = str(taskType)

            # Envía al mensaje al GWAgentROS
            await behav.send(msg2send)
            print("[" + myAgent.id + "] message to " + myAgent.gw_jid)

# ============================================================================================================
#   [STOPPING BEHAVIOUR]
    def stop(self):
        print("Stopping TransportAgent...")
        print("            + OK!\n")

# ============================================================================================================
#   [IDLE BEHAVIOUR]
    def idle(self):
        print("Transport status: IDLE")
