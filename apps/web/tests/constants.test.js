import { describe, expect, it } from 'vitest';
import { MIN_CONFIDENCE, isConclusive } from '../src/constants.js';

describe('isConclusive', () => {
  it('rechaza una confianza por debajo del umbral', () => {
    expect(isConclusive(MIN_CONFIDENCE - 0.01)).toBe(false);
  });

  it('acepta una confianza igual al umbral', () => {
    expect(isConclusive(MIN_CONFIDENCE)).toBe(true);
  });

  it('acepta una confianza alta', () => {
    expect(isConclusive(0.99)).toBe(true);
  });
});
