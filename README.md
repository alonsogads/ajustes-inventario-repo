# AjustesInventario

Programa en Python para convertir `ajustes.txt` en una tabla con las columnas:

`Sucursal | Turno | Cantidad | Clave | Comentario`

El programa conserva el orden original de los ajustes, omite sucursales/turnos sin movimientos y conserva las claves como texto en Excel (por ejemplo, `0001` permanece como `0001`).

## Estructura del proyecto

```text
ajustes_inventario/
├── ajustes_inventario/
│   ├── __init__.py
│   ├── cli.py          # Argumentos y flujo principal
│   ├── exporter.py     # Exportación a Excel y CSV
│   ├── models.py       # Modelo Adjustment y errores de formato
│   └── parser.py       # Lectura y análisis de ajustes.txt
├── ejemplos/
│   └── ajustes_ejemplo.txt
├── tests/
│   └── test_parser.py
├── main.py             # Punto de entrada
└── requirements.txt
```

## Requisitos

- Python 3.10 o posterior.
- Para generar archivos Excel `.xlsx`, instalar las dependencias del proyecto.

### Windows (PowerShell)

Desde este directorio:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### Linux

Desde este directorio:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Uso normal

1. Coloca el archivo real `ajustes.txt` junto a `main.py`.
2. Ejecuta:

   ```bash
   python main.py
   ```

3. Si encuentra ajustes, genera `ajustes_procesados.xlsx` en el mismo directorio que `ajustes.txt`. El libro incluye una tabla de Excel con filtros, encabezado fijo y la columna `Clave` almacenada como texto.

También puedes indicar las rutas de entrada y salida:

```bash
python main.py "C:/ruta/ajustes.txt" --salida "C:/ruta/resultado.xlsx"
```

En Linux, por ejemplo:

```bash
python main.py "$HOME/documentos/ajustes.txt" -o "$HOME/documentos/resultado.csv"
```

La extensión selecciona el formato de salida:

- `.xlsx`: libro de Excel (recomendado).
- `.csv`: CSV UTF-8 con BOM, separado por punto y coma (`;`). Si abres este CSV directamente en Excel, la aplicación puede interpretar claves como `0001` como números; utiliza el `.xlsx` recomendado si necesitas conservar los ceros iniciales de forma automática.

Si no existe ningún ajuste, el programa no crea ni modifica el archivo de salida. Si ya había un resultado de una ejecución anterior, lo deja intacto. Si encuentra una línea no vacía con formato incorrecto, detiene el proceso y muestra el número de línea para evitar crear una tabla incompleta.

## Formato esperado

Cada sección empieza con cuatro caracteres, por ejemplo `SPT1`, `C1T2` o `PAT1`. Los dos primeros identifican la sucursal y los dos últimos, el turno (`T1` o `T2`). Después aparecen los ajustes con este formato:

```text
CLAVE+CANTIDAD COMENTARIO
```

No se escribe un espacio entre la clave, el signo y la cantidad. Ejemplos válidos:

```text
SPT1
0001-10 CONSUMO PERSONAL
0127+5 UNO POR OTRO
1-1 CONSUMO
```

Se aceptan archivos UTF-8 y archivos de texto con codificación Windows-1252. Las líneas vacías se ignoran.

## Crear un ejecutable

Instala PyInstaller dentro del entorno virtual:

```bash
python -m pip install pyinstaller
```

Después, desde la raíz del proyecto:

### Windows

```powershell
pyinstaller --clean --noconfirm --onefile --name AjustesInventario main.py
```

El ejecutable se crea en `dist\AjustesInventario.exe`.

### Linux

```bash
pyinstaller --clean --noconfirm --onefile --name AjustesInventario main.py
```

El ejecutable se crea en `dist/AjustesInventario`.

**Construye el ejecutable en cada sistema operativo:** el `.exe` se genera en Windows y el ejecutable para Linux, en Linux. Copia `ajustes.txt` al directorio donde esté el ejecutable y ejecútalo desde allí. También puedes pasar una ruta explícita al archivo.

## Pruebas

```bash
python -m unittest discover -s tests -v
```
