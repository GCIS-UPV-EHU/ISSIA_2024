# Kode honek XML osagai-eredua edukita, Node-RED tresnarako prest dagoen nodo pertsonalizatua lortzeko beharrezko fitxategiak sortzen ditu
from io import BytesIO
import os

# Fitxategiak aukeratzeko liburutegia
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# XML, XSLT eta XSD fitxategiekin lan egiteko liburutegiak
from saxonche import *
from lxml import etree

'''
----------------------------------
Methods related to Component Model
----------------------------------
'''


def getAppModel():
    print("To enter the XML application model, select one of the following options:")
    print("\t\t -> 1: Enter the application model as a file.")
    print("\t\t -> 2: Enter the application model as text.")
    print("\t\t -> 3: Exit the program.")
    while True:
        selectedOption = int(input("Enter the option number: "))
        if 1 <= selectedOption <= 3:
            break
        else:
            print("The option selected is incorrect, please enter it again.")
    print(selectedOption)
    if (selectedOption == 1):
        window = Tk()
        window.lift()
        window.attributes("-topmost", True)  # Leihoa pantailan erakusteko
        window.after_idle(window.attributes, '-topmost', False)
        Tk().withdraw()
        archivo_xml = askopenfilename(filetypes=[("Archivos XML", "*.xml")], title="Choose the XML file")
        with open(archivo_xml,
                  "r") as archivo:
            # Lee el contenido del archivo y almacénalo en una cadena
            content = archivo.read()
        window.destroy()
        return content
    elif (selectedOption == 2):
        print("Copy the component model and paste it here (end by pressing Enter on a blank line):")
        stringAppModel = ''
        while True:

            line = input('''''')
            if line == '':
                break
            else:
                stringAppModel += line + '\n'
        print(stringAppModel)
        return stringAppModel
    elif (selectedOption == 3):
        exit()
    else:
        print("Option not available.")


'''
---------------------------------------------
Saxonche liburutegiarekin erlazionatutako metodoak
---------------------------------------------
'''


def checkApplicationMetaModel(appXML):
    result = False
    while not result:
        xmlschema_doc = etree.parse("/home/issia/NodeRED/Application.xsd")
        xmlschema = etree.XMLSchema(xmlschema_doc)

        some_file_or_file_like_object = BytesIO(appXML.encode('utf-8'))
        xml_doc = etree.parse(some_file_or_file_like_object)
        result = xmlschema.validate(xml_doc)
        if not result:
            print("The XML file you entered is incorrect, please re-enter it.")
            appXML = getAppModel()
    return appXML


def getAppName(originXML):
    with PySaxonProcessor(license=False) as proc:
        xp = proc.new_xpath_processor()
        node = proc.parse_xml(xml_text=originXML)
        xp.set_context(xdm_item=node)
        result = xp.evaluate_single('/application/@name')
        return str.lower(result.string_value)



def getXSLT_transformation(originXML, stylesheetXSLT):
    with PySaxonProcessor(license=False) as proc:
        xsltproc = proc.new_xslt30_processor()
        document = proc.parse_xml(xml_text=originXML)
        executable = xsltproc.compile_stylesheet(stylesheet_file=stylesheetXSLT)
        output = executable.transform_to_string(xdm_node=document)
        return output


'''
---------------------------------------------
Bestelako metodoak
---------------------------------------------
'''


def createFile(content, fileName):
    f = open(fileName, 'w')
    f.write(content)
    f.close()


def main():
    appModelXML = getAppModel()

    print("Before starting the process, the entered application model will be checked with the application meta-model.")
    appModelXML = checkApplicationMetaModel(appModelXML)
    appName = getAppName(appModelXML)

    print("After verifying the validity of the model, the Application Delivery Model will be obtained, in the form of a Custom Resource in a YAML file.")
    customResourceContent = getXSLT_transformation(appModelXML, '/home/issia/NodeRED/appModelToAppDeliveryModel.xslt')
    createFile(customResourceContent, './' + appName + '.yaml')
    print("Application Delivery Model correctly created! The new file is in the following path: " + os.getcwd() + '/' + appName + '.yaml')


main()
