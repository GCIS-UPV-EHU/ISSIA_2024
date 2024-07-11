""" Authors: Ane López Mena & Maite López Mena """
#!/usr/bin/env python
import re # regex
import time
import rospy
import smach # máquina de estados
import rosbag
import rosnode
import actionlib # SimpleActionClient
from turtlesim.msg import Pose
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import PoseStamped
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal

# Variables auxiliares para coordenadas
new_x = 0
new_y = 0

# ============================= [ MOVE ] =============================== #
# Este método gestionará el movimiento de nuestro robot turtlebot mediante
# el cálculo de la distancia y velocidad.
def move(lx,ly, lz, ax, ay, angle, distance, rotation_speed, clockwise):
    # Crear un nodo PUBLISHER que publique por el tópico /cmd_vel
    velocity_publisher = rospy.Publisher('/cmd_vel', Twist, queue_size=10)

    # Definir el valor de PI para los giros
    PI = 3.1415926535897

    # Crear un tipo de datos Twist para enviar por el tópico /cmd_vel
    vel_msg = Twist()

    speed = lx
    angular_speed = rotation_speed * 2 * PI / 360
    relative_angle = angle * 2 * PI / 360

    vel_msg.linear.x = lx
    # Solo se moverá por el eje x
    vel_msg.linear.y = ly
    vel_msg.linear.z = lz
    vel_msg.angular.x = ax
    vel_msg.angular.y = ay

    # Comprobar si el movimiento del robot es en sentido HORARIO o ANTIHORARIO
    # Horario
    if clockwise:
        vel_msg.angular.z = -abs(angular_speed)
    else:
    # Antihorario
        vel_msg.angular.z = abs(angular_speed)

    if not rospy.is_shutdown():
        # Obtener el tiempo actual para el cálculo de la DISTANCIA
        t0 = rospy.Time.now().to_sec()
        current_distance = 0
        current_angle = 0

        # ROTATION
        while (current_angle < relative_angle):
            velocity_publisher.publish(vel_msg)
            t1 = rospy.Time.now().to_sec()
            current_angle = angular_speed * (t1 - t0)

        # MOVE
        while (int(current_distance) < int(distance)):
            velocity_publisher.publish(vel_msg)
            # Obtener el tiempo actual para el cálculo de la VELOCIDAD
            t1 = rospy.Time.now().to_sec()
            # Calcula la distancia
            current_distance = speed * (t1 - t0)
            
        # Después del bucle, detiene el robot
        vel_msg.linear.x = 0
        velocity_publisher.publish(vel_msg)
        vel_msg.angular.z = 0
        velocity_publisher.publish(vel_msg)

# ================================================================
# STATE_1: IDLE
# Definimos el estado IDLE del turtlebot3
class Idle(smach.State):

    def __init__(self):
        
        # Definimos los atributos de la clase, que para el caso, serán:
        #   1) Una variable donde almacenar los mensajes
        self.msg = ""
        #   2) Un nodo PUBLISHER, que será el que publique el estado del robot por e tópico '/status'
        self.pub = rospy.Publisher('/status', String, queue_size=10) #.publish("IDLE")
        #   3) Un nodo SUBSCRIBER, que se quedará a la escucha en el tópico '/coordinateIdle' para
        #      recibir la señal de inicio
        rospy.Subscriber("/coordinateIDLE", String, self.callback)

        # Establecer las transiciones entre estados
        smach.State.__init__(self, outcomes=['TO_LOCALIZATION', 'TO_ERROR'])

    # El método callback se ejecutará cuando el nodo suscriptor reciba un mensaje por
    # el tópico '/coordinateIdle'
    def callback(self, data):
        self.msg = data.data
        
    def execute(self, userdata):
        rospy.loginfo('Executing state IDLE')
        self.pub.publish("IDLE")
        print("")

        # Mientras esté activo, comprobará los mensajes recibidos
        while not rospy.is_shutdown():
            # Si ha recibido un mensaje de valor 'GO'
            if (self.msg == "GO") :
                # Pasa al siguiente estado -> LOCALIZATION
                return "TO_LOCALIZATION"
            else:
                # En cambio, si recibe un mensaje de valor 'STOP'
                if (self.msg == "STOP"):
                    # Pasa al estado 'ERROR'
                    return "TO_ERROR"

# ================================================================
# STATE_2: LOCALIZATION
# Definimos el estado LOCALIZATION

class Localization(smach.State):

    def callbackScan(self, msg):
        # Desde terminal:
        # ~/catkin_ws$ rosmsg show sensor_msgs/LaserScan
        """
         _________________________________________________________________________
        | Para más información de las coordenadas enviadas por el tópico '/scan', |
        | pueden descomentarse las siguientes líneas:                             |
        +-------------------------------------------------------------------------+
        print("Data received from /scan: "+str(msg))
        print(' * Front: {}'.format(msg.ranges[0])) # Datos del lidar de la parte DELANTERA
        print(' * Left:  {}'.format(msg.ranges[90])) # Datos del lidar de la parte IZQUIERDA
        print(' * Right: {}'.format(msg.ranges[270])) # Datos del lidar de la parte DERECHA
        print(' * Back: {}'.format(msg.ranges[180])) # Datos del lidar de la parte TRASERA
        """
        # Guardar el mensaje obtenido
        self.msg = msg

    def __init__(self):
        # Establecer las transiciones entre estados
        smach.State.__init__(self, outcomes=['TO_RECOVERY', 'TO_ACTIVE','TO_ERROR'])

        # Definimos los atributos de la clase, que para el caso, serán:
        #   1) Una variable donde almacenar los mensajes
        self.msg = None
        #   2) Crear un suscriptor para el tópico '/scan'
        #         |__Type: sensor_msgs/LaserScan
        sub_scan = rospy.Subscriber("/scan", LaserScan, self.callbackScan)
        #   3) Crear un publicista para el tópico '/status'
        self.pub = rospy.Publisher('/status', String, queue_size=10)

    def execute(self, userdata):
        rospy.loginfo('Executing state LOCALIZATION')
        # Publica el estado por '/status'
        self.pub.publish("LOCALIZATION")

        if self.msg:
            # Distancia para esquivar obstáculos (Distancia de seguridad)
            self.avoidance_distance = 0.3
            # Velocidad
            self.speed = 20

            # Definir un ángulo de 60 grados para comprobación de obstáculos
            if self.msg.ranges[0] > self.avoidance_distance and self.msg.ranges[30] > self.avoidance_distance and self.msg.ranges[330] > self.avoidance_distance:

                # Calibración: Gira sobre sí mismo 360º
                print(" -- Calibrating turtlebot3... -- ")
                # Sentido HORARIO
                move(lx=0, ly=0, lz=0, ax=0, ay=0, angle=360, distance=0, rotation_speed=200, clockwise=True)
                # Sentido ANTIHORARIO
                move(lx=0, ly=0, lz=0, ax=0, ay=0, angle=360, distance=0, rotation_speed=200, clockwise=False)

                # Una vez calibrado el turtlebot, pasa a estado ACTIVE
                return  'TO_ACTIVE'

            else:
                # Si detecta un obstáculo, pasa a RECOVERY
                rospy.loginfo(" -- Oh! Obstacle on the way! -- ")

                return  'TO_RECOVERY'

# ================================================================
# STATE_3: ACTIVE
# Definimos el estado ACTIVE. El turtlebot queda a espera de servicio.
class Active(smach.State):

    def __init__(self):
        # Establecer las transiciones entre estados
        smach.State.__init__(self, outcomes=['TO_OPERATIVE','TO_ERROR'])

        # Definimos los atributos de la clase, que para el caso, serán:
        #   1) Una variable donde almacenar los mensajes
        self.msg = None
        rospy.Subscriber("/coordinate", String, self.callback)

        #   2) Crear un publicista para el tópico '/status'
        self.pub = rospy.Publisher('/status', String, queue_size=10)

        print("Waiting for a new goal...")

    # El método callback se ejecutará cuando el nodo suscriptor reciba un mensaje por
    # el tópico '/coordinate'
    def callback(self, data):
        self.msg = data.data
        #print("RECIBE MENSAJE NUEVO EN ACTIVE: " + str(self.msg))

    def execute(self, userdata):
        rospy.loginfo('Executing state ACTIVE')
        self.pub.publish("ACTIVE")
        print("*")
        data_ok = False

        # Comprobar mensaje recibido
        while not data_ok:
            # Si no ha recibido mensaje, paso
            if self.msg == None:
               pass
            # Si ha recibido mensaje, comprobar el contenido
            else:
                # Si el mensaje es 'STOP'
                if (self.msg == "STOP"):
                    # Pasa al estado ERROR
                    return "TO_ERROR"
                else:
                    # Ha recibido una coordenada: Comprobar que la coordenada sea apta
                    #   Para ello, se hace uso de expresiones regex
                    if re.search("(-*[0-9])+,(-*[0-9])+", str(self.msg)):
                        # Coordenada X
                        new_x = float(str(self.msg).split(",")[0])
                        # Coordenada Y
                        new_y = float(str(self.msg).split(",")[1])

                        # Marcar como data ok
                        data_ok = True

                        # Guardar coordenadas del goal en un bagfile de ROS
                        bag = rosbag.Bag(f='goal.bag', mode='w')
                        try:
                            # Crear una estructura Pose para escribir las coordenadas
                            # y guardarlas en el rosbag
                            p = Pose()
                            p.x = new_x
                            p.y = new_y
                            # Escribir en rosbag
                            bag.write('coordinate', p)
                        finally:
                            bag.close()
                            self.msg = None
                            
                        # Pasar al estado operative
                        return 'TO_OPERATIVE'

                    # Si el formato del mensaje no es válido -> Ignorarlo

        # Si sale hasta aquí, ir a estado ERROR
        return 'TO_ERROR'

# ================================================================
# STATE_4: OPERATIVE
# Definimos el estado OPERATIVE
class Operative(smach.State):

    def __init__(self):
        # Establecer las transiciones entre estados
        smach.State.__init__(self, outcomes=['TO_RECOVERY', 'TO_ACTIVE','TO_ERROR', 'TO_STOP'])
        rospy.loginfo('Executing state OPERATIVE')
        # Publicista para publicar el estado de la máquina por el tópico '/status'
        self.pub = rospy.Publisher('/status', String, queue_size=10)
        #time.sleep(1)
        # Publicista para publicar las coordenadas a alcanzar por el tópico '/move_base_simple/goal'
        self.move_base_pub = rospy.Publisher('/move_base_simple/goal', PoseStamped, queue_size=5)

    def movebase_client(self, goal_x, goal_y):
        # Crear un nodo "action client" llamado 'move_base' con el action definition file (ADF) "MoveBaseAction"
        client = actionlib.SimpleActionClient('move_base', MoveBaseAction)

        # Queda a la espera de que el action server se haya iniciado y esté a la escucha de goals (objetivos)
        client.wait_for_server()

        # Crea un nuevo goal con el constructor de MoveBaseGoal
        goal = MoveBaseGoal()
        goal.target_pose.header.frame_id = "map"
        goal.target_pose.header.stamp = rospy.Time.now()

        # Indicar las coordenadas (X,Y)
        goal.target_pose.pose.position.x = float(goal_x)
        goal.target_pose.pose.position.y = float(goal_y)

        # Rotación, para que el robot mire de frente al almacen
        goal.target_pose.pose.orientation.w = 1.0

        #time.sleep(1)
        # Envía el goal al action server
        client.send_goal(goal)
        # QUeda a la espera de que el servidor termine de procesar la solicitud
        wait = client.wait_for_result()

        # Si no hay respuesta, se asume que el servidor no está disponible o hay algún error
        if not wait:
            rospy.logerr("Action server not available!")
            rospy.signal_shutdown("Action server not available!")
        else:
            # Devuelve el resultado de la operación
            return client.get_result()

    def execute(self, userdata):
        # Publica el estadp actual del recurso transporte
        self.pub.publish("OPERATIVE")

        # Extrae los datos del rosbag anterior
        bag = rosbag.Bag('goal.bag')
        goal_x = ""
        goal_y = ""
        for topic, msg, t in bag.read_messages(topics=['coordinate']):
            messageSplit = str(msg).split(":")
            goal_x = str(messageSplit[1]).replace("\ny", "")
            goal_y = str(messageSplit[2]).replace("\ntheta", "")

        # Limpiar y cerrar el rosbag
        bag.flush()
        bag.close()

        try:
            print("MOVING TO COORDINATE: " + str(goal_x) + str(goal_y))

            #time.sleep(1)
            # Se inicia nuevamente un nodo rospy para que publique el SImpleActionClient
            result = self.movebase_client(goal_x, goal_y)

            # Si ha habido resultado
            if result:
                rospy.loginfo("Goal execution done!")
                return 'TO_ACTIVE'
        except rospy.ROSInterruptException:
            # Si ha habido algún error
            rospy.loginfo("Navigation test finished.")
            return 'TO_ERROR'

# ================================================================
# STATE_5: STOP
class Stop(smach.State):

    def __init__(self):
        # Establecer las transiciones entre estados
        smach.State.__init__(self, outcomes=[])

        # Crear un publisher para devolver el estado del recurso transporte por el tópico '/status'
        self.pub = rospy.Publisher('/status', String, queue_size=10)

    def execute(self, userdata):
        # Detiene la unidad de transporte y termina la ejecución de todos los
        # nodos implicados en el sistema de navegación
        self.pub.publish("STOP")

        # Obtener lista de nodos
        nodelist = rosnode.get_node_names()

        # Por cada nodo, terminarlo
        for node in nodelist:
            rosnode.kill_nodes(node)

# ================================================================
# STATE_6: RECOVERY
# Definir el estado RECOVERY
class Recovery(smach.State):

    def __init__(self):
        # Establecer las transiciones entre estados
        smach.State.__init__(self, outcomes=['TO_LOCALIZATION','TO_OPERATIVE'])

        # Crear un publisher para devolver el estado del recurso transporte por el tópico '/status'
        self.pub = rospy.Publisher('/status', String, queue_size=10)

    def execute(self, userdata):
        # Publicar el estado del recurso como "RECOVERY"
        self.pub.publish("RECOVERY")
        #time.sleep(1)
        return 'TO_OPERATIVE'
        
# ================================================================
# STATE_7: ERROR
class Error(smach.State):

    def __init__(self):
        # Establecer las transiciones entre estados
        smach.State.__init__(self, outcomes=[])

        # Crear un publisher para devolver el estado del recurso transporte por el tópico '/status'
        self.pub = rospy.Publisher('/status', String, queue_size=10)
        # Publicar el estado del recurso como "ERROR"
        self.pub.publish("ERROR")

    def execute(self, userdata):
        self.pub.publish("ERROR")
        # Detiene la unidad de transporte y termina la ejecución de todos los
        # nodos implicados en el sistema de navegación

        # Obtener lista de nodos
        nodelist = rosnode.get_node_names()

        # Por cada nodo, terminarlo
        for node in nodelist:
            rosnode.kill_nodes(node)
        #time.sleep(1)

        return 'TO_OPERATIVE'

# ==============================================================================

def main():
    # El método main contiene la declaración de la máquina de estados del transporte.

    # Definir los estados de la máquina de estados (SMACH)
    STATE_1 = "IDLE"
    STATE_2 = "LOCALIZATION"
    STATE_3 = "ACTIVE"
    STATE_4 = "OPERATIVE"
    STATE_5 = "STOP"
    STATE_6 = "RECOVERY"
    STATE_7 = "ERROR"

    # Crear el nodo 'main', llamado 'TRANSPORT_NODE', fque ejecuta y coordina la máquina de estados
    rospy.init_node('TRANSPORT_NODE')

    # Crear la máquina de estados, definiendo los estados "finales":
    # STATE_5 --> STOP
    # STATE_7 --> ERROR
    sm = smach.StateMachine(outcomes=[STATE_5, STATE_7])

    # Open the container
    with sm:
        # Declarar los estados y transiciones
        smach.StateMachine.add(STATE_1, Idle(),
                               transitions={'TO_LOCALIZATION': STATE_2,
                                            'TO_ERROR': STATE_7})
                                            
        smach.StateMachine.add(STATE_2, Localization(),
                               transitions={'TO_RECOVERY': STATE_6,
                                            'TO_ACTIVE': STATE_3,
                                            'TO_ERROR': STATE_7})
                                            
        smach.StateMachine.add(STATE_3, Active(),
                               transitions={'TO_OPERATIVE': STATE_4,
                                            'TO_ERROR': STATE_7})
                                            
        smach.StateMachine.add(STATE_4, Operative(),
                               transitions={'TO_RECOVERY': STATE_6,
                                            'TO_ACTIVE': STATE_3,
                                            'TO_STOP': STATE_5,
                                            'TO_ERROR': STATE_7})

        smach.StateMachine.add(STATE_5, Stop(),transitions={})

        smach.StateMachine.add(STATE_6, Recovery(),
                               transitions={'TO_OPERATIVE': STATE_4,
                                            'TO_LOCALIZATION': STATE_2})

        '''smach.StateMachine.add(STATE_7, Error(),transitions={})'''

    # Ejecutar plan SMACH (State MACHine)
    outcome = sm.execute()

# ======= [MAIN] ======= #
if __name__ == '__main__':
    main()
    
