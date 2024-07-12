
// Aplikazio-eredua osatzeko elementu erabilgarrien liburutegia inportatu
const {FunctionInfo, createLastMicroservice, addMicroServiceToModel, checkApplicationMetaModel, appModelToAppDeliveryModel} = require('../appModel_utils.js');

// Osagaiaren aldagaiak
const componentName = "NumberDisplay";
const imgBase = "ekhurtado/gcis-issia-24:number-display";

module.exports = function(RED) {
    function NumberDisplay(config) {
        RED.nodes.createNode(this,config);
        
        this.function = config.function;
        this.selectedPortNumber = config.portnumber;
        this.selectedFileName = config.filename;
        var node = this;
        
        node.on('input', function(msg) {

            if (node.function === "") {
                node.error(`No functionality has been selected for a node. To find out which one it is, click on this error message.`);
            } else {

                // Funtzionalitate guztien informazioa betetzen dugu
                // --------------------
                const allFunctionsInfo= [
                    consoleDisplay = new FunctionInfo("ConsoleDisplay", "HTTP", null, "TNumber", null, null),
                    saveTXT = new FunctionInfo("SaveTXT", "HTTP", null, "TNumber", null, "custom_filename"),
                    saveCSV = new FunctionInfo("SaveCSV", "HTTP", null, "TNumber", null, "custom_filename"),
                ]

                // Hautatutako funtzionalitatearen informazioa lortzen dugu
                // --------------------
                let selectedFunctionInfo;
                let selectedCustomizationValue = "";
                for (const funcObj in allFunctionsInfo) {
                    if (node.function === allFunctionsInfo[funcObj].name) {
                        selectedFunctionInfo = allFunctionsInfo[funcObj];
                        if (node.function === "SaveTXT" || node.function === "SaveCSV") {
                            if (node.selectedFileName === "") {
                                node.error("You have not specified a file name. Please specify.");
                                return;
                            } else
                                selectedCustomizationValue = node.selectedFileName;
                        }
                    }
                }

                // Mikrozerbitzu berriaren informazioa eraikitzen dugu
                // --------------------
                const newMicroservice = createLastMicroservice(componentName, imgBase, selectedFunctionInfo, node.selectedPortNumber);
                // Osagai honen pertsonalizazioa gehitzen diogu (osagai honen bereizgarria dena)
                if (selectedCustomizationValue !== "")
                    newMicroservice.$.customization = `{'${selectedFunctionInfo.customizationName}': '${selectedCustomizationValue}'}`;


                // Aurreko osagaiak bidalitako aplikazio-ereduari osagaiaren informazioa gehitzen diogu
                // --------------------
                let appModelXML = addMicroServiceToModel(msg, newMicroservice, true);

                // Azkenengo osagaia denez, aplikazio-eredua zuzena dela konprobatuko du
                let result = checkApplicationMetaModel(appModelXML);
                if (!result || result.length === 0) {
                    // XML aplikazio-eredua zuzena da, erabiltzaileari emaitza erakustiko diogu
                    node.warn(appModelXML);

                    // let appDeliveryModelYAML = appModelToAppDeliveryModel(appModelXML);
                    // let appModels= {"application model": appModelXML,
                    //                                         "application delivery model": appDeliveryModelYAML};
                    // node.warn(appModels);

                } else
                    node.error(`The generated application model does not match the Fog Application meta-model. The reason: ${result}`);

            }


        });
    }

    RED.nodes.registerType("NumberDisplay",NumberDisplay);
}
