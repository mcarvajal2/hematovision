// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

// app.js tiene efectos al importarse (busca elementos del DOM, engancha
// listeners, arranca la carga del modelo), así que se mockean sus
// dependencias y se reimporta con módulos frescos en cada test.

const classifierMocks = vi.hoisted(() => ({
  predict: vi.fn(),
  load: vi.fn().mockResolvedValue(undefined),
}));
vi.mock('../src/classifier.js', () => ({
  CellClassifier: vi.fn().mockImplementation(() => ({
    predict: classifierMocks.predict,
    load: classifierMocks.load,
  })),
}));

const cameraMocks = vi.hoisted(() => ({
  start: vi.fn().mockResolvedValue(undefined),
  stop: vi.fn(),
  switch: vi.fn().mockResolvedValue(undefined),
}));
vi.mock('../src/camera.js', () => ({
  CameraController: vi.fn().mockImplementation(() => ({
    start: cameraMocks.start,
    stop: cameraMocks.stop,
    switch: cameraMocks.switch,
  })),
}));

function mountFixture() {
  document.body.innerHTML = `
    <video id="video"></video>
    <canvas id="canvas"></canvas>
    <div id="camera-placeholder"></div>
    <span id="camera-status"></span>
    <span id="model-status"></span>
    <button id="enable-camera"></button>
    <button id="switch-camera" disabled></button>
    <button id="capture"></button>
    <button id="start" hidden></button>
    <button id="pause" hidden></button>
    <button id="reset"></button>
    <p id="automatic-note" hidden></p>
    <div id="prediction"></div>
    <strong id="total"></strong>
    <div id="counter-list"></div>
    <div id="toast"></div>
    <input type="radio" name="mode" value="manual" checked>
    <input type="radio" name="mode" value="automatic">
  `;
}

async function loadApp() {
  vi.resetModules();
  mountFixture();
  await import('../src/app.js');
  // Deja correr el microtask de classifier.load().then(...) y camera activada.
  await Promise.resolve();
  await Promise.resolve();
}

async function enableCamera() {
  document.getElementById('enable-camera').click();
  await Promise.resolve();
  await Promise.resolve();
}

beforeEach(() => {
  classifierMocks.predict.mockReset();
  cameraMocks.start.mockClear();
});

afterEach(() => {
  document.body.innerHTML = '';
});

describe('flujo de análisis en app.js', () => {
  it('una predicción aceptada incrementa el contador', async () => {
    await loadApp();
    await enableCamera();
    classifierMocks.predict.mockReturnValue({ label: 'Linfocitos', confidence: 0.9 });

    document.getElementById('capture').click();

    expect(document.getElementById('total').textContent).toBe('1');
    expect(document.getElementById('prediction').textContent).toBe('Linfocitos · 90.0%');
  });

  it('una predicción rechazada no incrementa y muestra el aviso', async () => {
    await loadApp();
    await enableCamera();
    classifierMocks.predict.mockReturnValue({ label: 'Linfocitos', confidence: 0.3 });

    document.getElementById('capture').click();

    expect(document.getElementById('total').textContent).toBe('0');
    expect(document.getElementById('prediction').textContent).toBe(
      'Imagen no concluyente · enfoca una célula aislada',
    );
  });

  it('el modo automático (demo) muestra el aviso y no se disfraza de conteo manual', async () => {
    await loadApp();
    const automaticRadio = document.querySelector('input[name=mode][value=automatic]');
    const manualRadio = document.querySelector('input[name=mode][value=manual]');

    automaticRadio.checked = true;
    automaticRadio.dispatchEvent(new Event('change', { bubbles: true }));

    expect(document.getElementById('automatic-note').hidden).toBe(false);
    expect(document.getElementById('capture').hidden).toBe(true);
    expect(document.getElementById('start').hidden).toBe(false);

    manualRadio.checked = true;
    manualRadio.dispatchEvent(new Event('change', { bubbles: true }));

    expect(document.getElementById('automatic-note').hidden).toBe(true);
  });

  it('al alcanzar el límite de 100, una captura posterior no acumula y avisa', async () => {
    await loadApp();
    await enableCamera();
    classifierMocks.predict.mockReturnValue({ label: 'Linfocitos', confidence: 0.9 });
    const captureButton = document.getElementById('capture');

    for (let i = 0; i < 100; i += 1) {
      captureButton.click();
    }
    expect(document.getElementById('total').textContent).toBe('100');

    captureButton.click();

    expect(document.getElementById('total').textContent).toBe('100');
    expect(document.getElementById('prediction').textContent).toBe(
      'Límite de 100 células alcanzado · no se contabiliza',
    );
  });
});
