# DVC y remoto GCS — plan y estado

**Estado:** DVC inicializado localmente (2026-09-08). **Google Cloud Storage (GCS) es el remoto objetivo elegido por Miguel**, pero **todavía no existe ningún bucket, proyecto, service account ni credencial** — nada de eso está autorizado en esta ronda. Este documento separa lo ya hecho (local, sin red) de lo propuesto (requiere autorización separada antes de ejecutarse), siguiendo la misma disciplina de [Plan de Fase 2](phase2-plan.md) y [Manifiesto de originales](dataset-manifest.md).

## 1. Qué ya existe (local, verificado)

- DVC instalado como dependencia de desarrollo de `ml/` (`dvc[gs]` en `ml/pyproject.toml`, resuelto por `uv`), con soporte de Google Cloud Storage disponible (`gcsfs`), sin necesitar instalar nada aparte cuando llegue el momento de conectar el remoto real.
- `dvc init` ejecutado en la raíz del repositorio Git (`D:\Proyectos\hematovision\.dvc\`, **no** dentro de `ml/`) — es la ubicación correcta porque DVC versiona datos a nivel de todo el repositorio, no por subproyecto.
- `core.analytics = false` en `.dvc/config`: se deshabilitó la telemetría anónima de DVC para no enviar nada fuera de esta máquina mientras el proyecto siga siendo local.
- **Ningún remoto configurado.** `dvc remote list` está vacío a propósito.
- Probado con un archivo descartable (`dvc add` / `dvc status` / `dvc checkout`) para confirmar que el mecanismo de cacheo y restauración funciona antes de aplicarlo a datos reales; el archivo de prueba y todo rastro suyo se eliminaron al terminar.
- El split congelado (`ml/data/manifest_v2.csv`, DEC-003, SHA-256 `010a820d…acf31e1`) permaneció intacto durante todo el proceso.

Detalle técnico completo (versión exacta de DVC, salida de `dvc doctor`, verificación independiente) en el commit correspondiente y en el reporte de revisión de este trabajo.

## 2. Estrategia de datos (qué se versionará con DVC y cómo)

Tres categorías de datos, con estrategias distintas porque su relación con el repositorio es distinta:

### 2.1 Manifiestos (`ml/data/manifest_v1.csv`, `manifest_v2.csv`)

**Estado:** ya viven dentro del árbol del repositorio (`ml/data/`), ~4 MiB cada uno, ya excluidos de Git vía `.gitignore`. Son el caso más simple: `dvc add ml/data/manifest_v1.csv` y `dvc add ml/data/manifest_v2.csv` los traería bajo control de DVC sin mover ni copiar nada fuera de su ubicación actual.

**Limitación encontrada (verificada en esta ronda, no solo teórica):** DVC **rechaza** crear un puntero `.dvc` dentro de una carpeta que ya está completamente ignorada por Git — lo comprobamos directamente al intentar una prueba de humo en `ml/data/`. Para trackear los manifiestos con DVC, `.gitignore` tiene que dejar de ignorar `ml/data/` como bloque entero; en su lugar, cada archivo real (`manifest_v1.csv`, `manifest_v2.csv`) queda ignorado individualmente por el `.gitignore` que el propio DVC genera al lado de cada `.dvc`, mientras los punteros `.dvc` sí se versionan en Git. Es un cambio mecánico y de bajo riesgo, pero es un cambio real de `.gitignore` que no se aplicó en esta ronda (no estaba pedido) — queda propuesto para cuando se autorice trackear los manifiestos.

**Plan (no ejecutado):**
```
# quitar la línea "ml/data/" del .gitignore raíz
dvc add ml/data/manifest_v1.csv
dvc add ml/data/manifest_v2.csv
git add ml/data/manifest_v1.csv.dvc ml/data/manifest_v2.csv.dvc ml/data/.gitignore .gitignore
```
Esto no mueve ni duplica nada: los archivos ya están donde tienen que estar.

### 2.2 Datasets originales (Bodzas `Labelled`, ~24 GiB; PBC `Labelled_2`, ~268 MiB)

**Este es el punto que requiere una decisión explícita antes de tocarse — no se ejecutó nada aquí.**

**El problema de fondo:** hoy viven fuera del repositorio, en `D:\Datasets\dataset_hematologia\`. DVC necesita que el archivo o carpeta que se trackea esté **dentro** del árbol del repositorio para que el flujo estándar `git clone` + `dvc pull` funcione en otra máquina — el puntero `.dvc` que se commitea a Git describe una ruta relativa al repo, y `dvc pull` reconstruye el contenido exactamente en esa ruta relativa. Un dataset fuera del repo, referenciado por una ruta absoluta de esta máquina (`D:\Datasets\...`), no es portable: esa ruta no existe en otra computadora, y DVC no tiene forma de "recrearla" ahí.

**Alternativas evaluadas:**

1. **Mover los datasets dentro del repo** (ej. `ml/data/raw/Labelled`, `ml/data/raw/Labelled_2`), después `dvc add`. Es el camino estándar y el único que garantiza portabilidad total (`git clone` + `uv sync` + `dvc pull` reproduce todo en una máquina nueva). Como el repo (`D:\Proyectos\`) y los datasets (`D:\Datasets\`) están en el **mismo volumen NTFS (`D:`)**, mover ~24 GiB es una operación de sistema de archivos casi instantánea (rename a nivel de volumen, no una copia física de bytes) — no duplica el espacio en disco. El costo real no es el movimiento en sí, sino que `dvc add` tiene que **leer y hashear las ~30.224 imágenes una vez** para construir el cache de DVC (I/O de lectura, no de red) — comparable en magnitud al trabajo que ya hizo `build_manifest.py` al construir el manifiesto original.
2. **Symlink/junction desde dentro del repo hacia la ubicación externa**, sin mover nada. Se descarta como estrategia principal: no resuelve el problema de portabilidad (en una máquina nueva no existiría `D:\Datasets\...` para apuntar), y la integración de DVC con symlinks como "add target" es más frágil/menos probada que el flujo estándar.
3. **DVC "external outputs"** (trackear una ruta fuera del repo directamente). Existe como función de DVC, pero está pensada para casos donde los datos *tienen* que quedarse fuera del árbol del proyecto (ej. un dataset compartido entre varios repos); complica el `dvc pull`/`dvc checkout` en otra máquina de la misma forma que el symlink, y no es el camino recomendado hoy por la documentación de DVC para este caso de uso.

**Recomendación:** opción 1 (mover dentro del repo, mismo volumen, sin duplicar espacio), **pero no se ejecuta en esta ronda** porque el usuario pidió explícitamente no mover ni copiar los datasets originales todavía. Antes de hacerlo, hay que decidir junto con Miguel: la carpeta destino exacta (`ml/data/raw/` es la propuesta), y confirmar que ningún otro proceso/notebook depende de la ruta actual `D:\Datasets\dataset_hematologia\` (los scripts nuevos de `ml/scripts/` y `ml/src/` sí dependen de ella hoy — habría que actualizarlos como parte del mismo cambio, no por separado).

### 2.3 Artefactos de experimentos futuros (`artifacts/experiments/`)

Todavía no existe (no hay ningún `EXP-NNN` ejecutado). Cuando exista, cada carpeta de experimento (checkpoints, `history.json`, configuración) se trackeará con DVC igual que los manifiestos — vive naturalmente dentro del repo, sin el problema de portabilidad de los datasets externos.

## 3. Diseño de configuración GCS (propuesto, nada de esto está aplicado)

| Parámetro | Propuesta | Razón |
| --- | --- | --- |
| **Región del bucket** | `southamerica-west1` (Santiago, Chile) | Miguel opera desde Chile; es la única región de GCS físicamente en el país — menor latencia para `dvc push`/`dvc pull` interactivos desde su máquina de desarrollo. Alternativa si `southamerica-west1` tuviera alguna limitación de servicio/precio relevante: `southamerica-east1` (São Paulo) como segunda opción regional. |
| **Clase de almacenamiento inicial** | `Standard` | Se anticipa acceso frecuente durante desarrollo activo (`dvc pull` en cada máquina nueva, iteración de experimentos). Nearline/Coldline penalizan con costos de recuperación y duración mínima de almacenamiento — no convienen todavía. Podría reevaluarse a futuro *solo* para los datasets originales una vez que se consideren estables/inmutables. |
| **Nombre lógico del bucket** | algo como `hematovision-dvc` o `<identificador-de-miguel>-hematovision-dvc` | Los nombres de bucket de GCS son **únicos globalmente** (no solo dentro del proyecto de GCP) — el nombre final depende de disponibilidad al momento de crearlo; esto es solo una propuesta de convención, a confirmar cuando se autorice la creación. |
| **Remote name en DVC** | `gcs` | Alias simple y explícito (`dvc remote add gcs gs://<bucket>/dvc-store`, comando exacto en la Sección 5 — no ejecutado). |

## 4. Autenticación (recomendada, no configurada)

**Desarrollo local (Miguel, esta máquina y futuras máquinas de desarrollo):** [Application Default Credentials (ADC)](https://cloud.google.com/docs/authentication/application-default-credentials) vía `gcloud auth application-default login`. Es el mecanismo que Google y DVC recomiendan hoy para desarrollo interactivo — autentica con la identidad de Google del propio Miguel, sin generar ningún archivo de clave JSON de larga duración. Las credenciales quedan cacheadas fuera del repositorio (en el perfil del usuario del sistema operativo, no en `D:\Proyectos\hematovision`), así que nunca llegan a Git aunque se cometiera un error de `.gitignore`.

**Futuras VMs de entrenamiento o CI/CD:** evitar también ahí una clave JSON estática:
- **VM de Compute Engine:** usar la cuenta de servicio *adjunta* a la VM (autenticación vía metadata server) — no requiere ninguna clave descargada.
- **CI/CD (ej. GitHub Actions):** **Workload Identity Federation (WIF)**, que intercambia un token OIDC de GitHub Actions por credenciales temporales de GCP, sin ninguna clave de larga duración almacenada como secreto.

**Qué se versiona en Git y qué no:**
- **En `.dvc/config` (versionado):** el nombre del remoto y su URL `gs://bucket/ruta` una vez creado — es solo topología, no un secreto.
- **Nunca en Git:** cualquier archivo de clave JSON (evitado por diseño con ADC/WIF), `.dvc/config.local` (DVC ya lo ignora automáticamente por defecto), la caché de credenciales de `gcloud` (vive en el perfil del usuario, fuera del repo), y cualquier variable de entorno `GOOGLE_APPLICATION_CREDENTIALS`.

## 5. Comandos que Miguel deberá ejecutar cuando autorice el siguiente paso (ninguno ejecutado todavía)

```powershell
# 1. Crear el proyecto de GCP (si no existe uno ya elegido) y habilitar billing — decisión de Miguel, fuera de DVC
gcloud projects create <project-id>

# 2. Crear el bucket en la región y clase elegidas
gcloud storage buckets create gs://<nombre-bucket-elegido> `
  --project=<project-id> `
  --location=southamerica-west1 `
  --default-storage-class=STANDARD `
  --uniform-bucket-level-access

# 3. Autenticación local recomendada (sin clave JSON)
gcloud auth application-default login

# 4. Conectar el remoto en DVC (recién acá se toca .dvc/config)
cd D:\Proyectos\hematovision
ml\.venv\Scripts\uv.exe run --project ml dvc remote add -d gcs gs://<nombre-bucket-elegido>/dvc-store
git add .dvc/config
git commit -m "chore(dvc): conectar remoto GCS"

# 5. Recién ahí, subir lo que ya esté trackeado con DVC (manifiestos, y más adelante datasets)
ml\.venv\Scripts\uv.exe run --project ml dvc push
```

## 6. Seguridad — verificado en esta ronda

- Ninguna credencial de ningún tipo existe en el repositorio ni en `.dvc/`.
- Ningún remoto real configurado (`dvc remote list` vacío).
- `.gitignore` sigue coherente: `.dvc/cache/` ya estaba anticipado antes de inicializar DVC; el propio `.dvc/.gitignore` que DVC generó ignora además `config.local` y `tmp` — configuración local y compartida quedan separadas por diseño de DVC, no por convención manual.
- No hubo ninguna transferencia de red: sin remoto, `dvc push`/`dvc pull` no tienen a dónde apuntar.

## 7. Qué NO autoriza este documento

Crear el proyecto/bucket de GCP, configurar billing, generar cualquier credencial, ejecutar `dvc remote add` con una URL real, ejecutar `dvc push`, mover o copiar los datasets originales, y entrenar o ejecutar EXP-REPRO — cada uno sigue requiriendo su propia autorización explícita y separada, igual que en las rondas anteriores de Fase 2.
