# DVC y remoto GCS — plan y estado

**Estado (2026-09-08):** DVC inicializado localmente, **remoto GCS real creado y conectado** (`gcs` → `gs://hematovision-ml-dvc/dvc-store`), probado end-to-end con un archivo pequeño descartable. Además, se validó empíricamente (en un proyecto DVC temporal, fuera del repo real) el mecanismo `dvc add --to-remote`, que permite subir los datasets originales al remoto **sin moverlos ni copiarlos localmente primero**. **Los datasets originales (~24-25 GiB) todavía NO están versionados ni subidos** — nada de eso se ejecutó sobre datos reales en esta ronda. Este documento separa lo ya hecho (verificado) de lo propuesto (requiere autorización separada antes de ejecutarse), siguiendo la misma disciplina de [Plan de Fase 2](phase2-plan.md) y [Manifiesto de originales](dataset-manifest.md).

## 1. Qué ya existe (verificado)

- DVC 3.67.1 (`dvc[gs]` en `ml/pyproject.toml`, resuelto por `uv`), inicializado en la raíz del repositorio (`D:\Proyectos\hematovision\.dvc\`).
- **Proyecto GCP dedicado:** `hematovision-ml` (número `806949743302`), creado explícitamente para este proyecto — no se reutilizó ningún proyecto personal existente de Miguel. Billing vinculado a su cuenta de facturación abierta (`0110F9-9DA6AB-628D75`).
- **Bucket GCS creado:** `gs://hematovision-ml-dvc`, región `SOUTHAMERICA-WEST1`, clase `STANDARD`, `public_access_prevention: enforced`, `uniform_bucket_level_access: true`.
- **Remoto DVC conectado:** `gcs` → `gs://hematovision-ml-dvc/dvc-store`, configurado como remoto por defecto. Solo la URL quedó en `.dvc/config` (versionado en Git); ninguna credencial.
- **Autenticación:** Application Default Credentials, con la cuenta personal de Miguel (`m.angel9106@gmail.com`, deliberadamente distinta de su cuenta de trabajo de Cero). Sin ninguna clave JSON de service account. Las credenciales viven en `%APPDATA%\gcloud\application_default_credentials.json`, fuera del repositorio.
- **Dos pruebas end-to-end reales, exitosas** (ver Sección 6): un archivo simple vía `dvc add`/`dvc push`/`dvc pull`, y un directorio sintético vía `dvc add --to-remote` simulando una máquina nueva. Ambas limpiadas por completo del bucket y del disco después.
- **Cache type efectivo en esta máquina:** `hardlink` sobre NTFS (`D:`) — ver Sección 9.
- El split congelado (`ml/data/manifest_v2.csv`, DEC-003, SHA-256 `010a820d…acf31e1`) permaneció intacto durante todo el proceso.

## 2. Estrategia de datos (qué se versionará con DVC y cómo)

Tres categorías de datos, con estrategias distintas porque su relación con el repositorio es distinta:

### 2.1 Manifiestos (`ml/data/manifest_v1.csv`, `manifest_v2.csv`)

**Estado:** ya viven dentro del árbol del repositorio (`ml/data/`), ~4 MiB cada uno, ya excluidos de Git vía `.gitignore`. Al ser archivos ya locales y pequeños, `--to-remote` no aporta nada (ese mecanismo existe para evitar un round-trip local de datos *externos* grandes) — la estrategia sigue siendo `dvc add` normal (por cache local) + `dvc push`.

**Limitación encontrada (verificada):** DVC **rechaza** crear un puntero `.dvc` dentro de una carpeta que ya está completamente ignorada por Git. Para trackear los manifiestos (o, más adelante, los datasets) con DVC, `.gitignore` tiene que dejar de ignorar `ml/data/` como bloque entero; cada archivo real queda ignorado individualmente por el `.gitignore` que el propio DVC genera al lado de cada `.dvc`. Cambio mecánico y de bajo riesgo, no aplicado en esta ronda.

**Plan (no ejecutado, queda para cuando se autorice mezclar esto con datos reales):**
```
# quitar la línea "ml/data/" del .gitignore raíz
dvc add ml/data/manifest_v1.csv
dvc add ml/data/manifest_v2.csv
git add ml/data/manifest_v1.csv.dvc ml/data/manifest_v2.csv.dvc ml/data/.gitignore .gitignore
dvc push
```

### 2.2 Datasets originales (Bodzas `Labelled`, ~24 GiB; PBC `Labelled_2`, ~268 MiB) — estrategia revisada

**Todavía no se ejecutó nada aquí — sigue sin autorizarse.** Pero la estrategia recomendada **cambió** respecto a la ronda anterior, gracias al hallazgo validado en la Sección 7.

**Estrategia anterior (descartada como plan principal):** mover `Labelled`/`Labelled_2` físicamente dentro del repo y luego `dvc add` normal. Funcionaría, pero exige reorganizar ~24 GiB de originales en esta máquina.

**Estrategia recomendada ahora:** `dvc add --to-remote`, validado empíricamente en la Sección 7. Sube el contenido **directo desde `D:\Datasets\dataset_hematologia\` al bucket**, sin pasar por el cache local y **sin mover ni copiar nada en esta máquina**:

```powershell
# NO EJECUTADO — requiere autorización separada y aplica a los datos reales
cd D:\Proyectos\hematovision
ml\.venv\Scripts\uv.exe run --project ml dvc add --to-remote -r gcs `
  -o ml/data/raw/bodzas D:\Datasets\dataset_hematologia\Labelled
ml\.venv\Scripts\uv.exe run --project ml dvc add --to-remote -r gcs `
  -o ml/data/raw/pbc D:\Datasets\dataset_hematologia\Labelled_2
git add ml/data/raw/bodzas.dvc ml/data/raw/pbc.dvc ml/data/.gitignore .gitignore
```

Esto genera `ml/data/raw/bodzas.dvc` y `ml/data/raw/pbc.dvc` (versionables en Git) apuntando a datos que **ya están en GCS**, mientras `D:\Datasets\dataset_hematologia\` sigue exactamente como está hoy, sin tocarse. En una máquina nueva, `git clone` + `dvc pull` materializa el contenido en `ml/data/raw/bodzas/` y `ml/data/raw/pbc/` — sin que esa máquina necesite conocer `D:\Datasets\...` en absoluto.

**Costo real de esta operación (no ejecutada, para dimensionar antes de autorizar):** DVC igual necesita **leer y hashear las ~30.224 imágenes una vez** (para calcular el hash de contenido) y **subir ~24-25 GiB por red** a GCS — el ahorro de `--to-remote` es no duplicar esos GiB en el disco local, no evitar la lectura/hash ni la subida.

**Alternativas descartadas (sin cambios):** symlink hacia la ubicación externa (no resuelve portabilidad), DVC "external outputs" (mismo problema, no es el camino recomendado por DVC hoy).

### 2.3 Artefactos de experimentos futuros (`artifacts/experiments/`)

Todavía no existe (no hay ningún `EXP-NNN` ejecutado). Cuando exista, cada carpeta de experimento se trackeará con `dvc add` normal (ya nace dentro del repo) + `dvc push` al remoto `gcs` ya conectado.

### 2.4 Resolución portable de `path_original` — sin tocar DEC-003

**El problema:** `manifest_v2.csv` está congelado byte a byte (DEC-003, SHA-256 `010a820d…acf31e1`) y **no puede modificarse** para cambiar rutas. Sus valores de `path_original` (verificado en el CSV real y en `ml/scripts/build_manifest.py`, que los generó con `os.path.relpath(full, DATASET_ROOT)`) son rutas **relativas** con **separador Windows literal** dentro del string, por ejemplo `Labelled\Basophile\0.png` o `Labelled_2\eosinophil\EO_225902.jpg` — nunca una ruta absoluta de `D:\Datasets\...`. Eso ya es una buena noticia: el manifiesto no tiene hardcodeado `D:\Datasets`.

**El problema real y no obvio:** ese separador `\` es un **carácter literal dentro del string del CSV**, no una decisión del sistema operativo que lo lea. En Windows, `pathlib.Path("Labelled\\Basophile\\0.png")` lo interpreta correctamente como 3 componentes. **En Linux/GCP, `pathlib.PurePosixPath` trata la barra invertida como un carácter normal del nombre de archivo, no como separador** — un `Path(row["path_original"])` ingenuo se rompe silenciosamente fuera de Windows. Esto hay que resolverlo explícitamente, no asumir que "usar `pathlib`" alcanza.

**Diseño propuesto (no implementado — cambio de código pendiente, ver Sección 8), estructural y no basado en reemplazo de strings frágil:**

```python
# ml/src/hematovision_ml/paths.py (propuesto, no aplicado)
"""Resuelve path_original del manifiesto congelado contra una raíz configurable.

manifest_v2.csv nunca cambia (DEC-003). Este módulo traduce sus rutas
históricas (relativas a D:\\Datasets\\dataset_hematologia, con "\\" literal
grabado en el CSV) hacia la raíz de datos vigente en la máquina actual.
"""
import os
from pathlib import Path

DATASET_ROOT_ENV_VAR = "HEMATOVISION_DATASET_ROOT"
DEFAULT_DATASET_ROOT = Path(r"D:\Datasets\dataset_hematologia")  # default histórico, esta máquina

# Clave estructural: la columna "fuente" del manifiesto (ya verificada, no inferida)
# determina el prefijo histórico exacto y el nombre de carpeta portable nuevo.
_FUENTE_LAYOUT = {
    "Bodzas": {"historic_prefix": "Labelled", "portable_dir": "bodzas"},
    "PBC": {"historic_prefix": "Labelled_2", "portable_dir": "pbc"},
}

def dataset_root() -> Path:
    override = os.environ.get(DATASET_ROOT_ENV_VAR)
    return Path(override) if override else DEFAULT_DATASET_ROOT

def resolve_image_path(row: dict, root: Path | None = None) -> Path:
    layout = _FUENTE_LAYOUT[row["fuente"]]
    # split explícito por "\" literal: NO usar Path(path_original) directo,
    # porque en Linux "\" no separa componentes.
    parts = row["path_original"].split("\\")
    if parts[0] != layout["historic_prefix"]:
        raise ValueError(f"path_original inesperado para fuente={row['fuente']!r}: {row['path_original']!r}")
    return (root or dataset_root()).joinpath(layout["portable_dir"], *parts[1:])
```

**Por qué esta forma y no un reemplazo de strings:** el mapeo `fuente → prefijo histórico/carpeta portable` es una tabla fija de 2 entradas derivada de cómo `build_manifest.py` construyó el CSV (verificado, no adivinado) — no una heurística que intente adivinar patrones. `fuente` ya es una columna auditada y congelada; usarla como llave es más robusto que inferir el origen desde el propio `path_original`.

**Qué logra esta capa:**
- `manifest_v2.csv` no se toca nunca — DEC-003 intacto.
- En esta máquina (donde `HEMATOVISION_DATASET_ROOT` no se setea), el default apunta a `D:\Datasets\dataset_hematologia` — comportamiento idéntico al actual, cero disrupción.
- En una máquina nueva, tras `git clone` + `dvc pull` de `ml/data/raw/bodzas.dvc`/`pbc.dvc`, alcanza con `HEMATOVISION_DATASET_ROOT=<repo>/ml/data/raw` para que las mismas filas del manifiesto abran los archivos correctos, sin ningún cambio al CSV.
- Funciona igual en Windows y Linux/GCP porque el split es sobre el string, no sobre semántica de `pathlib` dependiente del SO.

## 3. Configuración GCS aplicada

| Parámetro | Valor aplicado | Razón |
| --- | --- | --- |
| **Proyecto GCP** | `hematovision-ml` | Dedicado, creado desde cero — no reutiliza ningún proyecto personal de Miguel (`desafio1`, `desafio2`, `fir-init-f898f`, `inmunovida-v4`, `prueba1` quedaron sin tocar). |
| **Región del bucket** | `southamerica-west1` (Santiago, Chile) | Miguel opera desde Chile; es la única región de GCS físicamente en el país. |
| **Clase de almacenamiento** | `STANDARD` | Se anticipa acceso frecuente durante desarrollo activo. |
| **Nombre del bucket** | `hematovision-ml-dvc` | Único globalmente, asociado claramente al proyecto. |
| **Acceso** | `public_access_prevention: enforced`, `uniform_bucket_level_access: true` | Sin acceso público, IAM uniforme. |
| **Remote name en DVC** | `gcs` | `gs://hematovision-ml-dvc/dvc-store`, remoto por defecto. |

## 4. Autenticación aplicada

**Desarrollo local:** Application Default Credentials, cuenta personal `m.angel9106@gmail.com`. Sin clave JSON. Credenciales en `%APPDATA%\gcloud\`, fuera del repositorio.

**Futuras VMs/CI/CD** (sin cambios, no aplica todavía): cuenta de servicio adjunta a la VM (Compute Engine) o Workload Identity Federation (CI/CD) — nunca una clave de larga duración.

**Qué quedó versionado en Git y qué no:** en `.dvc/config`, solo `remote = gcs` y su URL. Nunca en Git: claves JSON (ninguna generada), `.dvc/config.local` (no existe), caché ADC (fuera del repo), variables `GOOGLE_APPLICATION_CREDENTIALS`.

## 5. Otros proyectos GCP de Miguel (verificado, sin tocar)

Al crear `hematovision-ml` se confirmó que ninguno de estos proyectos personales preexistentes fue reutilizado ni modificado: `desafio1-5e6ca`, `desafio2-4c868`, `fir-init-f898f`, `inmunovida-v4`, `prueba1-bd5fe`.

## 6. Prueba pequeña (remoto real, archivo único) — resultado

| Paso | Resultado |
| --- | --- |
| `dvc add` de un archivo descartable (55 bytes) | Puntero `.dvc` generado (md5 `f7145c1c…`) |
| `dvc push` | `1 file pushed`; confirmado en el bucket vía `gcloud storage ls` |
| Borrado local + `dvc pull` | Contenido restaurado, **SHA-256 idéntico** |
| Limpieza | Archivo, `.dvc`, `.gitignore`, objeto remoto y cache local — todos eliminados; bucket confirmado vacío |

Repetida independientemente por Luna con un archivo distinto: mismo resultado.

## 7. Prueba de portabilidad `dvc add --to-remote` (simulación de máquina nueva) — resultado

Realizada en un **proyecto DVC temporal fuera del repo real** (`dvc init` aislado, remoto de prueba en un subpath separado del bucket, `gs://hematovision-ml-dvc/portability-test/`), con un dataset sintético (`external_test/class_a/a.txt`, `class_b/b.txt`, unas pocas palabras cada uno) — nunca datos reales.

1. **Mecanismo confirmado empíricamente** (leyendo `dvc add --help`/`dvc import-url --help` de la versión real instalada, no de memoria): `dvc add --to-remote -r <remote> [-o <nombre>] <ruta externa absoluta>` existe y acepta una carpeta externa fuera del proyecto DVC.
2. **Comando ejecutado:** `dvc add --to-remote -r gcstest C:\...\hematovision_portability_A\external_test` → generó `external_test.dvc` con el hash del directorio, `path: external_test` (relativo al proyecto, nunca la ruta absoluta de origen).
3. **Cache local de la "máquina A": vacío.** Ni siquiera se creó el directorio `.dvc/cache` — confirma que `--to-remote` sube directo al remoto sin materializar una copia local. Este es el hallazgo más importante y **quedó confirmado, no refutado**.
4. **"Máquina B" (simulación de clon limpio):** un directorio totalmente separado, con **solo** `external_test.dvc` + `.dvc/config` + `.dvcignore` copiados (nunca el contenido ni el cache de la máquina A). `dvc pull` recuperó `external_test/` completo; **SHA-256 idéntico** en ambos archivos respecto al origen.
5. **Limpieza verificada:** ambos directorios temporales eliminados, objetos bajo `gs://hematovision-ml-dvc/portability-test/` eliminados (incluidos objetos `.tmp` intermedios que generó la subida), `gcloud storage ls -r` confirma el bucket sin residuos.
6. **Limitación menor observada:** `dvc get` no soporta `--to-remote` (no es el mecanismo relevante); `dvc add`/`dvc import-url` sí. Para directorios, la subida genera objetos temporales `.tmp` en el remoto durante la transferencia — se limpian solos al terminar o se eliminan manualmente si la prueba se corta.

## 8. Estimación de costo (Standard, ~24-25 GiB) — supuestos explícitos, no un compromiso de precio

**No se afirma un costo exacto** — confirmar en la [calculadora oficial](https://cloud.google.com/products/calculator) antes de comprometerse. Estimación basada en tarifas históricas típicas de Standard en Sudamérica (~US$0,023–0,026/GiB/mes):

- **Almacenamiento:** ~25 GiB × ~US$0,025/GiB/mes ≈ **US$0,60–0,65/mes**.
- **Operaciones:** `push`/`pull` de ~30.000 archivos, del orden de centavos de dólar por corrida completa.
- **Egress:** la variable más grande — gratis/barato si un futuro entrenamiento corre en GCP misma región; una descarga completa hacia esta máquina por internet podría costar el equivalente a varios meses de almacenamiento en una sola corrida. `--to-remote` para la subida inicial no tiene costo de egress (es tráfico de entrada), pero cada `dvc pull` completo posterior sí.
- **Sin servicios adicionales activados** más allá de Cloud Storage.

## 9. Cache local — qué soporta esta máquina

`dvc doctor` confirma: **`Cache types: hardlink`**, sobre NTFS en `D:`. DVC 3.67.1 soporta `reflink`, `hardlink`, `symlink` y `copy` como valores de `cache.type`; NTFS no soporta `reflink` (requiere Btrfs/APFS/ReFS con bloques compartidos), por eso DVC elige `hardlink` como mejor opción disponible aquí — confirmado también con una prueba aislada (`fsutil hardlink list` mostró el archivo de trabajo y el objeto de cache compartiendo el mismo enlace físico).

**Implicación de mutabilidad:** con `hardlink`, el archivo de trabajo y la entrada de cache son el **mismo inodo** — escribir sobre el archivo de trabajo corrompería silenciosamente la cache (por eso DVC marca los archivos trackeados como solo lectura por defecto; no burlar esa protección manualmente). No se cambió `cache.type` en el repo real — sigue en su default (`hardlink` ya es lo que DVC elegiría automáticamente aquí, confirmado, no forzado).

## 10. Seguridad — verificado en esta ronda (dos veces, incluida revisión independiente)

- Bucket sin acceso público (`public_access_prevention: enforced`), sin bindings de `allUsers`/`allAuthenticatedUsers` en su política IAM.
- Ninguna credencial en Git — búsqueda activa de patrones sin resultados.
- Ninguna clave JSON de service account generada.
- `.dvc/config` solo contiene la URL del remoto.
- `.dvc/config.local` no existe.
- `.gitignore` sin residuos de las pruebas.

## 11. Qué sigue sin autorizar

Mover o copiar los datasets originales, subir los ~24-25 GiB reales (con `--to-remote` o cualquier otro mecanismo), trackear los manifiestos reales, implementar `ml/src/hematovision_ml/paths.py` (Sección 2.4, diseñado pero no aplicado), entrenar, ejecutar EXP-REPRO, y modificar el modelo publicado — cada uno sigue requiriendo su propia autorización explícita y separada.
