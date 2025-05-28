
import {app} from "/scripts/app.js"

class AudioNodeBase {
    onConnectionsChange(node, side, slot /*, connect, link_info, output */) {
        // console.log("Someone changed my connection!", node, side, slot);
        this.checkInputs(node);
    }

    getWidgetNames(node) {
        const widgetNames = {};
        if(node.widgets) {
            for(const widget of node.widgets) {
                widgetNames[widget.name] = true;
            }
        }
        return widgetNames;
    }

    getAudioNames(node) {
        const audioNames = {};
        if(node.inputs) {
            for(const input of node.inputs) {
                if(input.type !== 'AUDIO') {
                    continue;
                }
                audioNames[input.name] = input;
            }
        }
        return audioNames;
    }

    getHasSpareAudios(audioNames) {
        return Object.values(audioNames).
            reduce((c, input) => (input.link ? 0 : 1), 0);
    }

    init() {
        const t = this;
        app.registerExtension({
            name: this.getNodeName(),
            async beforeRegisterNodeDef(nodeType /*, nodeData, app */) {
                if (nodeType.comfyClass === t.getNodeClass()) {
                    const onConnectionsChange = nodeType.prototype.onConnectionsChange;
                    nodeType.prototype.onConnectionsChange = function (side, slot, connect, link_info, output) {
                        // biome-ignore lint: Using arguments with apply()
                        const r = onConnectionsChange?.apply(this, arguments);
                        t.onConnectionsChange(this, side, slot, connect, link_info, output);
                        return r;
                    }
                }
            },
            async nodeCreated(node) {
                if (node && node.comfyClass === t.getNodeClass()) {
                    try {
                        t.checkInputs(node);
                    } catch(e) {
                        console.error('nodeCreated error', e);
                    }
                }
            }
        });
    }
}

class AudioMix extends AudioNodeBase {
    addVolumeWidget(node, volumeName) {
        node.addWidget('number', volumeName, 1,
            {},
            { "default": 1, "step":0.05 },
        );
    }

    addStartSecsWidget(node, startSecsName) {
        node.addWidget('number', startSecsName, 0,
            {},
            { "default": 0, "step":1, "min": 0 },
        );
    }

    checkInputs(node) {
        const widgetNames = this.getWidgetNames(node);
        const audioNames = this.getAudioNames(node);

        // let maxAudioNum = 0;
        const hasSpareAudios = this.getHasSpareAudios(audioNames);
        let upto = 1;
        for(; ; upto++) {
            const audioName = `audio${upto}`;
            const volumeName = `volume${upto}`;
            const start_secsName = `start_secs${upto}`;
            if(audioNames[audioName]) {
                if(!widgetNames[volumeName]) {
                    this.addVolumeWidget(node, volumeName);
                }
                if(!widgetNames[start_secsName]) {
                    this.addStartSecsWidget(node, start_secsName);
                }
            } else {
                break;
            }
        }

        if(!hasSpareAudios) {
            const audioNum = upto;

            node.addInput(`audio${audioNum}` , 'AUDIO', {});
            this.addVolumeWidget(node, `volume${audioNum}`);
            this.addStartSecsWidget(node, `start_secs${audioNum}`);
        }
    }

    getNodeClass() {
        return 'AudioMix';
    }

    getNodeName() {
        return 'AudioGeneral.AudioMix';
    }
}

class AudioConcatenate extends AudioNodeBase {
    getNodeClass() {
        return 'AudioConcat';
    }

    getNodeName() {
        return 'AudioGeneral.AudioConcat';
    }

    checkInputs(node) {
        const audioNames = this.getAudioNames(node);

        const hasSpareAudios = this.getHasSpareAudios(audioNames);
        let upto = 1;
        for(; ; upto++) {
            const audioName = `audio${upto}`;
            if(!audioNames[audioName]) {
                break;
            }
        }

        if(!hasSpareAudios) {
            const audioNum = upto;

            node.addInput(`audio${audioNum}` , 'AUDIO', {});
        }
    }
}

new AudioConcatenate().init();
new AudioMix().init();
