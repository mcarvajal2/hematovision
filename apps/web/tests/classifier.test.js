import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { describe, expect, it } from 'vitest';
import { CellClassifier } from '../src/classifier.js';
import { CELL_TYPES } from '../src/constants.js';

const modelDir = fileURLToPath(new URL('../public/model/', import.meta.url));

// tf.loadLayersModel() sabe pedir un modelo por URL (fetch) o por un
// IOHandler propio. En Node, sin @tensorflow/tfjs-node ni un servidor HTTP,
// se arma un IOHandler que lee el manifiesto y los shards directo del
// filesystem, para poder probar la carga real del artefacto (y con eso, que
// el shim de L2 en classifier.js siga siendo suficiente) sin red.
async function loadFromFilesystem() {
  const modelJson = JSON.parse(await readFile(path.join(modelDir, 'model.json'), 'utf8'));
  const weightSpecs = modelJson.weightsManifest.flatMap((group) => group.weights);

  const shardBuffers = [];
  for (const group of modelJson.weightsManifest) {
    for (const shardPath of group.paths) {
      shardBuffers.push(await readFile(path.join(modelDir, shardPath)));
    }
  }
  const concatenated = Buffer.concat(shardBuffers);
  const weightData = concatenated.buffer.slice(
    concatenated.byteOffset,
    concatenated.byteOffset + concatenated.byteLength,
  );

  return {
    load: async () => ({
      modelTopology: modelJson.modelTopology,
      weightSpecs,
      weightData,
      format: modelJson.format,
      generatedBy: modelJson.generatedBy,
      convertedBy: modelJson.convertedBy,
    }),
  };
}

describe('CellClassifier con el artefacto publicado', () => {
  it('carga el modelo real (shim de L2 incluido) y expone las 9 clases esperadas', async () => {
    const classifier = new CellClassifier();
    const handler = await loadFromFilesystem();

    await classifier.load(handler);

    expect(classifier.model).toBeTruthy();
    expect(classifier.model.outputs[0].shape.at(-1)).toBe(CELL_TYPES.length);
  });
});
