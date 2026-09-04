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

  // Smoke test pendiente: cargar el modelo real con CellClassifier.load() y
  // correr una predicción de humo. Requiere servir public/model por HTTP
  // (p. ej. `vite preview` + Playwright) o instalar @tensorflow/tfjs-node
  // (bindings nativos) para resolver tf.loadLayersModel contra el filesystem.
  // Ninguno está configurado en este repo todavía; no fabricar un fetch/mock
  // que oculte si la carga real del modelo (incluido el shim de L2) sigue
  // funcionando.
  it.skip('CellClassifier.load() carga el modelo real y predice sin errores', () => {});
});
