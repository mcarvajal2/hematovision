import { readFile } from 'node:fs/promises';
import { describe, expect, it } from 'vitest';

const modelUrl = new URL('../public/model/model.json', import.meta.url);

describe('modelo web publicado', () => {
  it('incluye cada fragmento de pesos declarado en el manifiesto', async () => {
    const model = JSON.parse(await readFile(modelUrl, 'utf8'));
    const paths = model.weightsManifest.flatMap((group) => group.paths);

    expect(paths.length).toBeGreaterThan(0);

    await Promise.all(
      paths.map((path) => expect(readFile(new URL(`../public/model/${path}`, import.meta.url))).resolves.toBeDefined()),
    );
  });

  // La carga real del modelo (tf.loadLayersModel, incluido el shim de L2) se
  // prueba en tests/classifier.test.js.
});
