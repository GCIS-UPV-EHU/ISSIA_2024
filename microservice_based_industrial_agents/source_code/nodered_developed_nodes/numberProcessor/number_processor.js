const fs = require('fs');
const xml2js = require('xml2js');

// Aplikazio-eredua osatzeko elementu erabilgarrien liburutegia inportatu
const {FunctionInfo, createNewMicroservice, addMicroServiceToModel} = require('../appModel_utils.js');

// Osagaiaren aldagaiak
let componentName = "NumberProcessor";
const imgBase = "ekhurtado/gcis-issia-24:number-processor";

module.exports = function(RED) {
    function NumberProcessor(config) {
        RED.nodes.createNode(this,config);
        
        this.function = config.function;
        this.selectedPortNumber = config.portnumber;
        this.selectedStepSize = config.stepsize;
        this.selectedMultiplier = config.multiplier;
        var node = this;
        
        node.on('input', function(msg) {

            if (node.function === "") {
                node.error(`No functionality has been selected for a node. To find out which one it is, click on this error message.`);
            } else {

                if (node.function === "BalioaHanditu") {
                    node.function = "IncreaseValue"
                }

                // Funtzionalitate guztien informazioa betetzen dugu
                // --------------------
                const allFunctionsInfo= [
                    increaseValueInfo = new FunctionInfo("IncreaseValue", "HTTP", "HTTP", "TNumber", "TNumber", "custom_step"),
                    decreaseValueInfo = new FunctionInfo("DecreaseValue", "HTTP", "HTTP", "TNumber", "TNumber", "custom_step"),
                    multiplyValueInfo = new FunctionInfo("MultiplyValue", "HTTP", "HTTP", "TNumber", "TNumber", "custom_multiplier"),
                ]

                // Hautatutako funtzionalitatearen informazioa lortzen dugu
                // --------------------
                let selectedFunctionInfo;
                let selectedCustomizationValue;
                for (const funcObj in allFunctionsInfo) {
                    if (node.function === allFunctionsInfo[funcObj].name) {
                        selectedFunctionInfo = allFunctionsInfo[funcObj];
                        if (node.function === "IncreaseValue" || node.function === "DecreaseValue") {
                            if (node.selectedStepSize === -1) {
                                node.error("No step size has been selected. Please enter a valid number.");
                                return;
                            } else
                                selectedCustomizationValue = node.selectedStepSize;
                        } else {
                            if (node.selectedMultiplier === -1) {
                                node.error("No multiplier has been selected. Please enter a valid number.");
                                return;
                            } else
                                selectedCustomizationValue = node.selectedMultiplier;

                        }
                    }
                }

                let compName = "NumberProcessor";
                xml2js.parseString(msg, function (err, result) {
                    let microserviceList = result.application.microservice;
                    let lastMicroSvc = microserviceList.pop();
                    let repeatedComp = lastMicroSvc.$.name.toString().split("-");
                    if (repeatedComp[0].includes("NumberProcessor")) {
                        let newNumber = parseInt(repeatedComp[1]) + 1
                        compName = repeatedComp[0] + '-' + newNumber.toString();
                    } else {
                        compName = componentName + '-1'
                    }
                });

                // Mikrozerbitzu berriaren informazioa eraikitzen dugu
                // --------------------
                const newMicroservice = createNewMicroservice(compName, imgBase, selectedFunctionInfo, node.selectedPortNumber);
                // Osagai honen pertsonalizazioa gehitzen diogu (osagai honen bereizgarria dena)
                newMicroservice.$.customization = `{'${selectedFunctionInfo.customizationName}': ${selectedCustomizationValue}}`;


                // Aurreko osagaiak bidalitako aplikazio-eredua lortzen dugu
                // --------------------
                let appModelXML = addMicroServiceToModel(msg, newMicroservice, false);

                // XML aplikazio-eredua hurrengo nodoari bidali
                node.send(appModelXML);
            }


        });
    }

    RED.nodes.registerType("NumberProcessor",NumberProcessor);
}
