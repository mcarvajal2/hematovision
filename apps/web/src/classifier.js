import*as tf from'@tensorflow/tfjs';import{CELL_TYPES,MODEL_SIZE}from'./constants.js';
// El modelo legado serializa capas Conv2D con kernel_regularizer: L2 (ver
// apps/web/public/model/model.json). TF.js Layers comparte el registro de
// deserialización entre "layers" y "regularizers", así que sin esta clase
// registrada bajo el nombre "L2" tf.loadLayersModel() falla al reconstruir
// esas capas. Un regularizer no participa en la inferencia (solo afecta la
// pérdida durante el entrenamiento), así que un pass-through es correcto acá;
// esta clase NO debe usarse como una capa real. Ver docs/model-card.md y
// tests/classifier.test.js (carga el artefacto real para detectar si este
// shim deja de ser suficiente).
class L2 extends tf.layers.Layer{static className='L2';call(inputs){return inputs}}tf.serialization.registerClass(L2);
export class CellClassifier{model=null;async load(source=`${import.meta.env.BASE_URL}model/model.json`){await tf.ready();this.model=await tf.loadLayersModel(source);const size=this.model.outputs[0].shape.at(-1);if(size!==CELL_TYPES.length)throw new Error(`El modelo devuelve ${size} clases; se esperaban ${CELL_TYPES.length}.`)}predict(source){if(!this.model)throw new Error('El modelo todavía no está disponible.');return tf.tidy(()=>{const input=tf.browser.fromPixels(source).resizeBilinear([MODEL_SIZE,MODEL_SIZE]).toFloat().div(255).expandDims(0);const probabilities=Array.from(this.model.predict(input).dataSync());const index=probabilities.indexOf(Math.max(...probabilities));return{label:CELL_TYPES[index],confidence:probabilities[index]}})}}
