# DVC y remoto GCS — plan y estado

**Estado (2026-09-08):** DVC inicializado localmente, **remoto GCS real creado y conectado** (`gcs` → `gs://hematovision-ml-dvc/dvc-store`), probado end-to-end con un archivo pequeño descartable. **Los datasets originales (~24-25 GiB) todavía NO están versionados ni subidos** — nada de eso se ejecutó en esta ronda. Este documento separa lo ya hecho (verificado) de lo propuesto (requiere autorización separada antes de ejecutarse), siguiendo la misma disciplina de [Plan de Fase 2](phase2-plan.md) y [Manifiesto de originales](dataset-manifest.md).

## 1. Qué ya existe (verificado)

- DVC 3.67.1 (`dvc[gs]` en `ml/pyproject.toml`, resuelto por `uv`), inicializado en la raíz del repositorio (`D:\Proyectos\hematovision\.dvc\`).
- **Proyecto GCP dedicado:** `hematovision-ml` (número `806949743302`), creado explícitamente para este proyecto — no se reutilizó ningún proyecto personal existente de Miguel. Billing vinculado a su cuenta de facturación abierta (`0110F9-9DA6AB-628D75`).
- **Bucket GCS creado:** `gs://hematovision-ml-dvc`, región `SOUTHAMERICA-WEST1`, clase `STANDARD`, `public_access_prevention: enforced`, `uniform_bucket_level_access: true`. Verificado con `gcloud storage buckets describe` tras crearlo.
- **Remoto DVC conectado:** `gcs` → `gs://hematovision-ml-dvc/dvc-store`, configurado como remoto por defecto. Solo la URL quedó en `.dvc/config` (versionado en Git); ninguna credencial.
- **Autenticación:** Application Default Credentials (`gcloud auth application-default login`), con la cuenta personal de Miguel (`m.angel9106@gmail.com`, deliberadamente distinta de su cuenta de trabajo de Cero). Sin ninguna clave JSON de service account creada. Las credenciales viven en `%APPDATA%\gcloud\application_default_credentials.json`, fuera del repositorio.
- **Prueba end-to-end real, exitosa:** archivo descartable de 55 bytes → `dvc add` → `dvc push` (confirmado en el bucket vía `gcloud storage ls`) → borrado local → `dvc pull` → contenido restaurado con **SHA-256 idéntico**. El archivo, su `.dvc`, la entrada de `.gitignore` y el objeto en el bucket se eliminaron después — el bucket quedó vacío (`gcloud storage ls -r` no devuelve objetos).
- El split congelado (`ml/data/manifest_v2.csv`, DEC-003, SHA-256 `010a820d…acf31e1`) permaneció intacto durante todo el proceso.

## 2. Estrategia de datos (qué se versionará con DVC y cómo)

Tres categorías de datos, con estrategias distintas porque su relación con el repositorio es distinta:

### 2.1 Manifiestos (`ml/data/manifest_v1.csv`, `manifest_v2.csv`)

**Estado:** ya viven dentro del árbol del repositorio (`ml/data/`), ~4 MiB cada uno, ya excluidos de Git vía `.gitignore`. Son el caso más simple: `dvc add ml/data/manifest_v1.csv` y `dvc add ml/data/manifest_v2.csv` los traería bajo control de DVC sin mover ni copiar nada fuera de su ubicación actual — y ahora ya existe un remoto real para poder hacerles `dvc push`.

**Limitación encontrada (verificada, no solo teórica):** DVC **rechaza** crear un puntero `.dvc` dentro de una carpeta que ya está completamente ignorada por Git — lo comprobamos directamente al intentar la primera prueba de humo en `ml/data/`. Para trackear los manifiestos con DVC, `.gitignore` tiene que dejar de ignorar `ml/data/` como bloque entero; en su lugar, cada archivo real queda ignorado individualmente por el `.gitignore` que el propio DVC genera al lado de cada `.dvc`. Es un cambio mecánico y de bajo riesgo, pero no se aplicó en esta ronda (no estaba pedido) — queda propuesto para cuando se autorice trackear los manifiestos.

**Plan (no ejecutado):**
```
# quitar la línea "ml/data/" del .gitignore raíz
dvc add ml/data/manifest_v1.csv
dvc add ml/data/manifest_v2.csv
git add ml/data/manifest_v1.csv.dvc ml/data/manifest_v2.csv.dvc ml/data/.gitignore .gitignore
dvc push
```

### 2.2 Datasets originales (Bodzas `Labelled`, ~24 GiB; PBC `Labelled_2`, ~268 MiB)

**Este es el punto que requiere una decisión explícita antes de tocarse — no se ejecutó nada aquí, y sigue sin autorizarse.**

**El problema de fondo:** hoy viven fuera del repositorio, en `D:\Datasets\dataset_hematologia\`. DVC necesita que el archivo o carpeta que se trackea esté **dentro** del árbol del repositorio para que el flujo estándar `git clone` + `dvc pull` funcione en otra máquina.

**Alternativas evaluadas** (sin cambios respecto a la ronda anterior):

1. **Mover los datasets dentro del repo** (ej. `ml/data/raw/Labelled`, `ml/data/raw/Labelled_2`), después `dvc add` + `dvc push` al remoto ya existente. Es el camino recomendado: mismo volumen NTFS (`D:`), el movimiento no duplica espacio; el costo real es que `dvc add` tiene que leer y hashear las ~30.224 imágenes una vez.
2. **Symlink** hacia la ubicación externa: descartado, no resuelve portabilidad.
3. **DVC "external outputs"**: descartado, mismo problema de portabilidad, no es el camino recomendado por DVC para este caso.

**Recomendación sin cambios:** opción 1, **pendiente de autorización separada**. Antes de ejecutarla: decidir la carpeta destino exacta y actualizar las rutas que hoy dependen de `D:\Datasets\dataset_hematologia\` en `ml/scripts/` y `ml/src/`.

### 2.3 Artefactos de experimentos futuros (`artifacts/experiments/`)

Todavía no existe (no hay ningún `EXP-NNN` ejecutado). Cuando exista, cada carpeta de experimento se trackeará con DVC igual que los manifiestos, con `dvc push` al remoto `gcs` ya conectado.

## 3. Configuración GCS aplicada

| Parámetro | Valor aplicado | Razón |
| --- | --- | --- |
| **Proyecto GCP** | `hematovision-ml` | Dedicado, creado desde cero — no reutiliza ningún proyecto personal de Miguel (`desafio1`, `desafio2`, `fir-init-f898f`, `inmunovida-v4`, `prueba1` quedaron sin tocar). |
| **Región del bucket** | `southamerica-west1` (Santiago, Chile) | Miguel opera desde Chile; es la única región de GCS físicamente en el país — menor latencia para `dvc push`/`dvc pull` interactivos. |
| **Clase de almacenamiento** | `STANDARD` | Se anticipa acceso frecuente durante desarrollo activo. |
| **Nombre del bucket** | `hematovision-ml-dvc` | Único globalmente (confirmado al crearlo), asociado claramente al proyecto. |
| **Acceso** | `public_access_prevention: enforced`, `uniform_bucket_level_access: true` | Sin acceso público bajo ninguna circunstancia, IAM uniforme en vez de ACLs por objeto (recomendación vigente de GCS). |
| **Remote name en DVC** | `gcs` | `gs://hematovision-ml-dvc/dvc-store`, configurado como remoto por defecto (`dvc remote add -d`). |

## 4. Autenticación aplicada

**Desarrollo local (esta máquina):** Application Default Credentials, vía `gcloud auth application-default login` con la cuenta personal `m.angel9106@gmail.com`. Sin clave JSON de service account. Las credenciales quedan en el perfil de usuario de Windows (`%APPDATA%\gcloud\`), nunca en el repositorio — verificado explícitamente.

**Futuras VMs de entrenamiento o CI/CD** (sin cambios, todavía no aplica):
- **VM de Compute Engine:** cuenta de servicio *adjunta* a la VM (metadata server), sin clave descargada.
- **CI/CD (ej. GitHub Actions):** Workload Identity Federation, sin clave de larga duración.

**Qué quedó versionado en Git y qué no:**
- **En `.dvc/config` (versionado):** solo `remote = gcs` y `url = gs://hematovision-ml-dvc/dvc-store` — topología, no un secreto.
- **Nunca en Git:** ninguna clave JSON (no se generó ninguna), `.dvc/config.local` (no existe), la caché ADC de `gcloud` (fuera del repo), ninguna variable `GOOGLE_APPLICATION_CREDENTIALS`.

## 5. Prueba pequeña — resultado

| Paso | Resultado |
| --- | --- |
| `dvc add` de un archivo descartable (55 bytes) | Puntero `.dvc` generado correctamente (md5 `f7145c1c…`) |
| `dvc push` | `1 file pushed`; confirmado en `gs://hematovision-ml-dvc/dvc-store/files/md5/f7/…` vía `gcloud storage ls` |
| Borrado de la copia local | Confirmado ausente |
| `dvc pull` | `1 file added`; contenido restaurado |
| Verificación de integridad | SHA-256 idéntico antes y después (`6a9d2db7…`) |
| Limpieza | Archivo local, `.dvc`, entrada de `.gitignore`, objeto en el bucket y entrada de caché local — todos eliminados. Bucket confirmado vacío tras la limpieza. |

## 6. Estimación de costo (Standard, ~24-25 GiB) — supuestos explícitos, no un compromiso de precio

**No se afirma un costo exacto** — los precios de GCP cambian y deben confirmarse en la [calculadora oficial](https://cloud.google.com/products/calculator) antes de comprometerse. Estimación aproximada basada en tarifas históricas típicas de almacenamiento Standard en regiones sudamericanas (del orden de US$0,023–0,026 por GiB/mes):

- **Almacenamiento:** ~25 GiB × ~US$0,025/GiB/mes ≈ **US$0,60–0,65/mes** — un costo bajo dado el tamaño actual del dataset.
- **Operaciones:** `dvc push`/`dvc pull` de ~30.000 archivos implica del orden de 3-4 lotes de 10.000 operaciones — de órdenes de centavos de dólar por corrida completa (las tarifas de operaciones Clase A/B son mucho más bajas que el almacenamiento).
- **Egress (salida de red):** el costo más variable. Si un futuro entrenamiento corre en una VM de GCP en la misma región, el tráfico puede ser gratuito o muy barato (dentro de la nube de Google). Si se hace `dvc pull` hacia esta máquina de desarrollo (fuera de GCP, por internet), aplica la tarifa estándar de egress a internet — más cara que el almacenamiento, típicamente varios centavos de dólar por GiB, por lo que una descarga completa del dataset podría costar el equivalente a varios meses de almacenamiento en una sola corrida. Pulls repetidos desde múltiples máquinas de desarrollo suman.
- **No se activó ningún servicio adicional** más allá de Cloud Storage (Storage API) — las demás APIs que GCP habilita por defecto en un proyecto nuevo (BigQuery, Datastore, etc.) no generan costo por sí solas mientras no se usen.

**Recomendación:** antes de subir el dataset completo, confirmar el precio vigente exacto en la calculadora oficial y decidir con Miguel si el patrón de uso esperado (cuántas veces se espera hacer `pull` completo, desde dónde) cambia la estimación de egress.

## 7. Seguridad — verificado en esta ronda

- Bucket sin acceso público (`public_access_prevention: enforced`), confirmado con `gcloud storage buckets describe`.
- Ninguna credencial en Git — búsqueda activa de patrones (`private_key`, `client_email`, `service_account`, variables `GOOGLE_APPLICATION_CREDENTIALS`) sobre todo el repositorio, sin resultados.
- Ninguna clave JSON de service account generada en ningún momento.
- `.dvc/config` solo contiene la URL del remoto, sin secretos.
- `.dvc/config.local` no existe (no hizo falta).
- `.gitignore` volvió a su estado original tras la limpieza de la prueba — sin residuos.

## 8. Qué sigue sin autorizar

Mover o copiar los datasets originales (Bodzas/PBC), trackear o subir los ~24-25 GiB completos, ejecutar el primer `dvc push` de datos reales, entrenar, ejecutar EXP-REPRO, y modificar el modelo publicado — cada uno sigue requiriendo su propia autorización explícita y separada.
