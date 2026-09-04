import { describe, expect, it } from 'vitest';
import { centerSquareCrop } from '../src/camera.js';

describe('centerSquareCrop', () => {
  it('no recorta un video ya cuadrado', () => {
    expect(centerSquareCrop(400, 400)).toEqual({ side: 400, sx: 0, sy: 0 });
  });

  it('recorta los bordes horizontales de un video apaisado', () => {
    expect(centerSquareCrop(800, 600)).toEqual({ side: 600, sx: 100, sy: 0 });
  });

  it('recorta los bordes verticales de un video en retrato', () => {
    expect(centerSquareCrop(600, 800)).toEqual({ side: 600, sx: 0, sy: 100 });
  });
});
