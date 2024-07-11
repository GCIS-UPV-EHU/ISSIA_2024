const xml2js = require('xml2js');
const builder = new xml2js.Builder();
const fs = require('fs');


// Aplikazio-eredua osatzeko elementu erabilgarrien liburutegia inportatu
const {FunctionInfo, createFirstMicroservice} = require('../appModel_utils.js');

// Osagaiaren aldagaiak
const componentName = "NumberGeneratorButton";
const imgBase = "ekhurtado/gcis-issia-24:number-generator";

module.exports = function(RED) {
    function NumberGeneratorButton(config) {
        RED.nodes.createNode(this,config);
        
        this.function = config.function;
        this.valuetype = config.valuetype;
        this.firstvalue = config.firstvalue;
        var node = this;

        node.on('input', function(msg) {
            // Cuando recibe un mensaje es que se ha hecho click en el nodo

            var RED2 = require.main.require('node-red');
            var miflow = RED2.nodes.getFlow(this.z);    // this.z -> nodoa dagoen fluxuaren IDa
            var appName = miflow.label;
            if (appName.includes(' '))
                appName = appName.replace(/ /g, '_');

            if (node.function === "") {
                node.error(`Ez da funtzionalitaterik aukeratu nodo batean. Jakiteko zein den, klikatu errore mezu honetan.`);
            } else {

                // Funtzionalitate guztien informazioa betetzen dugu
                // --------------------
                const allFunctionsInfo= [
                    naturalValueInfo = new FunctionInfo("NaturalNumbers", null, "HTTP", null, "TNumber", "custom_type,custom_initialvalue"),
                    integerValue = new FunctionInfo("IntegerNumbers", null, "HTTP", null, "TNumber", "custom_type,custom_initialvalue"),
                    floatValue = new FunctionInfo("DecimalNumbers", null, "HTTP", null, "TNumber", "custom_type,custom_initialvalue")
                ]

                // Hautatutako funtzionalitatearen informazioa lortzen dugu
                // --------------------

                let selectedFunctionInfo;
                for (const funcObj in allFunctionsInfo) {
                    if (node.function === allFunctionsInfo[funcObj].name)
                        selectedFunctionInfo = allFunctionsInfo[funcObj];
                }

                // Customization datuak sartu badira konprobatuko da
                if (node.valuetype === "" || node.firstvalue === -999) {
                    node.error("Customization data is not included. Enter it, please.");
                    return;
                }

                // Mikrozerbitzu berriaren informazioa eraikitzen dugu
                // --------------------
                const microservice = createFirstMicroservice(componentName, imgBase, selectedFunctionInfo);
                // Osagai honen pertsonalizazioa gehitzen diogu (osagai honen bereizgarria dena)
                microservice.$.customization = `{` +
                    `'${selectedFunctionInfo.customizationName.split(',')[0]}': '${node.valuetype}', ` +
                    `'${selectedFunctionInfo.customizationName.split(',')[1]}': ${node.firstvalue}`+
                    `}`;

                const channel = {
                    $: {
                        from: microservice.outPort.$.name
                    }
                }

                // Lehenengo osagaia izanik, aplikazio-eredua eraikiko dugu
                // --------------------
                let appModelXML = {
                    application: {
                        $: {
                            name: appName, // recogerlo del nombre del flow
                        },
                        microservice,
                        channel
                    }
                }

                // XML fitxategia sortu
                appModelXMLObject = builder.buildObject(appModelXML);

                // XML aplikazio-eredua hurrengo nodoari bidali
                node.send(appModelXMLObject);
            }
        });
    }

    RED.nodes.registerType("NumberGeneratorButton",NumberGeneratorButton);

    // Creamos un listener para obtener mensajes http tipo POST
    RED.httpAdmin.post("/buttonnode/:id", RED.auth.needsPermission("buttonnode.write"), function(req,res) {
        var node = RED.nodes.getNode(req.params.id);
        if (node != null) {
            try {
                node.receive();
                res.sendStatus(200);
            } catch(err) {
                res.sendStatus(500);
                node.error(RED._("buttonnode.failed",{error:err.toString()}));
            }
        } else {
            res.sendStatus(404);
        }
    });
}
