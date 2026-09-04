import{CELL_TYPES,MAX_NON_PLATELET_COUNT}from'./constants.js';
export function createCounter(){return Object.fromEntries(CELL_TYPES.map(name=>[name,0]))}
export function totalWithoutPlatelets(counter){return CELL_TYPES.filter(name=>name!=='Plaquetas').reduce((sum,name)=>sum+counter[name],0)}
export function increment(counter,cellType){if(!CELL_TYPES.includes(cellType))throw new Error(`Clase desconocida: ${cellType}`);if(totalWithoutPlatelets(counter)>=MAX_NON_PLATELET_COUNT&&cellType!=='Plaquetas')return{...counter};return{...counter,[cellType]:counter[cellType]+1}}
