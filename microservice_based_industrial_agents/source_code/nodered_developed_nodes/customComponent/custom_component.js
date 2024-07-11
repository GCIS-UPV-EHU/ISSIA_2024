const fs = require('fs');

// Aplikazio-eredua osatzeko elementu erabilgarrien liburutegia inportatu
const {FunctionInfo, createNewMicroservice, addMicroServiceToModel} = require('../appModel_utils.js');

// Osagaiaren aldagaiak
const componentName = "CustomComponent";
const imgBase = "ekhurtado/gcis-issia-24:custom-comp";

module.exports = function(RED) {
    function CustomComponent(config) {
        RED.nodes.createNode(this,config);

        this.componentname = config.componentname;
        this.dockerimage = config.dockerimage;
        this.service = config.service;
        var node = this;
        
        node.on('input', function(msg) {

            if (node.function === "") {
                node.error(`No functionality has been selected for a node. To find out which one it is, click on this error message.`);
            } else {

                // Hautatutako funtzionalitatearen informazioa lortzen dugu
                // --------------------
                selectedFunctionInfo = new FunctionInfo(node.service, "HTTP", "HTTP", "TNumber", "TNumber", null);


                // Mikrozerbitzu berriaren informazioa eraikitzen dugu
                // --------------------
                const newMicroservice = createNewMicroservice(node.componentname, node.dockerimage, selectedFunctionInfo, 7000);


                // Aurreko osagaiak bidalitako aplikazio-eredua lortzen dugu
                // --------------------
                let appModelXML = addMicroServiceToModel(msg, newMicroservice, false);

                // XML aplikazio-eredua hurrengo nodoari bidali
                node.send(appModelXML);
            }


        });
    }

    RED.nodes.registerType("CustomComponent",CustomComponent);
}
