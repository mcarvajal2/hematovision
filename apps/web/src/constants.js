export const CELL_TYPES=['Basófilos','Eosinófilos','Eritroblastos','Linfoblastos','Linfocitos','Mieloblastos','Monocitos','Neutrófilos','Plaquetas'];
export const MAX_NON_PLATELET_COUNT=100;
export const MODEL_SIZE=150;
// Umbral provisional: el modelo siempre reparte 100% de probabilidad entre las
// 9 clases, así que una confianza alta no garantiza que la imagen sea una
// célula válida (una cara u otro objeto puede dar >90%). Este valor solo
// filtra predicciones obviamente ambiguas; no está calibrado contra un set de
// validación negativo (fondos, piel, caras, otras tinciones). Ver docs/model-card.md.
export const MIN_CONFIDENCE=0.6;
export function isConclusive(confidence){return confidence>=MIN_CONFIDENCE}
