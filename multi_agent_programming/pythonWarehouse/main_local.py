""" Authors: Ane López Mena & Maite López Mena """
import asyncio
import time
from random import randint

import spade
from Agents.MachineAgent import MachineAgent
from Agents.TransportAgent import TransportAgent
from Agents.SenderAgent import SenderAgent

async def main():

    print("+------------------------------------------------------------+")
    print("|            MULTIAGENT SYSTEM COMMUNICATION -               |")
    print("|             ** Maite López y Ane López **                  |")
    print("|             =============================                  |")
    print("|                - Trabajo Fin de Grado -                    |")
    print("|                     - 2023-2024 -                          |")
    print("+------------------------------------------------------------+\n")

    # Guardar JID + PASSWORD de los agentes creados
    machine_jid = "machineagent_1@ubuntu.min.vm"
    transport1_jid = "transportagent_1@ubuntu.min.vm"
    transport2_jid = "transportagent_2@ubuntu.min.vm"
    sender_jid = "senderagent_1@ubuntu.min.vm"

    # passwd = getpass.getpass()
    passwd = "upv123"

#=====================================================================================

# El objetivo del presente programa es demostrar la comunicación de las diferentes máquinas
# de un entorno de producción, empleando para ello la plataforma pythonWarehouse.
# pythonWarehouse está dirigida al desarrollo de agentes en el lenguaje de programación Python.

# Los recursos involucrados son los listados a continuación:
#  1) Recurso máquina: Automated Warehouse
#  2) Recurso transporte: Robot AGV - Turtlebot3 (Modelo 'Burger')
#
# El sistema implementado consiste en un almacén automático, en el que los usuarios
# podrán solicitar 2 servicios diferentes:2
#   |
#   |----> INTRODUCIR (Servicio 1) - El usuario indicará una posición (targetPosition)
#   |                                donde almacenar el material. Ese material será suministrado
#   |                                por un robot de navegación autónoma (AGV).
#   |
#   |----> EXTRAER    (Servicio 2) - El usuario indicará una posición (targetPosition) del
#                                    almacén para extraer material. Una vez extraído, la máquina,
#                                    se comunicará con los transportes para realizar el reparto del material.

# ===========================================================================================

    # Pedir por consola el servicio a realizar
    nServ = int(input("|----> Choose SERVICE TYPE: * DELIVERY (1) * COLLECTION (2) : "))

    # Pedir la posición del almacén para almacenar/extraer material
    targetPos = int(input("|----> Choose TARGET POSITION (1-54): " ))

#===========================================================================================

    print('\n·::::::::::::::::::[ INITIALIZATING ENVIRONMENT AND ASSETS ]:::::::::::::::::::·')

    if (nServ == 1):

        # Si se solicita el servicio 'DELIVERY', se instancian:
        #   * 1 MAQUINA
        #   * 1 TRANSPORTE

        # Inicialización de agente transporte 01
        ta = TransportAgent(transport1_jid, passwd)
        await ta.start()
        while not ta.ready:
            await asyncio.sleep(1)
        print()

        # Inicialización de agente máquina
        ma = MachineAgent(machine_jid, passwd)
        await ma.start()
        while not ma.ready:
            await asyncio.sleep(1)
        print()

        # Inicialización de agente Sender, para notificar al transporte de la petición de servicio
        sa = SenderAgent(sender_jid, passwd, nServ, targetPos)
        await sa.start()

        # Dejar código a la espera hasta finalización de agentes
        await spade.wait_until_finished(ma)
        await spade.wait_until_finished(ta)

    else:

        # Si se solicita el servicio 'COLLECTION', se instancian:
        #   * 1 MAQUINA
        #   * 2 TRANSPORTES

        # Inicialización de agente máquina
        ma = MachineAgent(machine_jid, passwd)
        await ma.start()
        while not ma.ready:
            await asyncio.sleep(1)
        print()

        # Inicialización de agente transporte 01
        ta1 = TransportAgent(transport1_jid, passwd, int(randint(1, 100)))
        await ta1.start()
        while not ta1.ready:
            await asyncio.sleep(1)
        print()

        # Inicialización de agente transporte 02
        ta2 = TransportAgent(transport2_jid, passwd, int(randint(1, 100)))
        await ta2.start()
        while not ta2.ready:
            await asyncio.sleep(1)
        print()

        # Inicialización de agente Sender, para notificar a la máquina de la petición de servicio
        sa = SenderAgent(sender_jid, passwd, nServ, targetPos)
        await sa.start()

        # Dejar código a la espera hasta finalización de agentes
        await spade.wait_until_finished(ma)
        await spade.wait_until_finished(ta1)
        await spade.wait_until_finished(ta2)

    print(" -- Agents finished --")

# ====================================================================
# Programa principal 'MAIN', desde el que se iniciará el entorno
if __name__ == "__main__":
    spade.run(main())
    start = time.time()
