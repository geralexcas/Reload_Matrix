# Plan: Soporte para PDFs Escaneados en Carga Inteligente de Facturas

## Fecha: 2026-05-30

## Diagnóstico

El problema está en `backend/app/services/purchase_service.py:739`:

```python
if not text.strip():
    raise ValueError("No se pudo extraer texto del PDF o está vacío.")
```

### Tipos de PDFs identificados

| Archivo | Tipo | `page.get_text()` | Imágenes |
|---------|------|--------------------|----------|
| `ledacon-01.pdf` | PDF nativo (generado digitalmente) | 3129 chars | 2 |
| `ledacom.pdf` | PDF escaneado (imagen escaneada) | 0 chars | 1 |
| `dysion3.pdf` | PDF escaneado (imagen escaneada) | 0 chars | 1 |

Los PDFs escaneados son **imágenes dentro de un PDF** (1728x2379 PNG). PyMuPDF (`fitz`) solo extrae texto embebido, no hace OCR. Por eso `get_text()` devuelve vacío y se lanza el error **antes** de llamar a Gemini.

**Lo irónico**: Gemini 2.5 Flash **sí puede leer PDFs escaneados** nativamente (se envía el PDF binario en `types.Part.from_bytes`), pero el código nunca llega a llamarlo porque la validación de texto lo bloquea antes.

---

## Alternativas Evaluadas

### Alternativa 1: Eliminar la validación de texto y confiar solo en Gemini (RECOMENDADA - SELECCIONADA)

La más simple y que aprovecha lo que ya existe. Gemini 2.5 Flash soporta lectura nativa de PDFs (incluyendo escaneados/imágenes).

**Cambios:**
1. Quitar el bloqueo en `purchase_service.py:739` — no lanzar error si `text.strip()` está vacío
2. Ajustar el prompt — si hay texto extraído, incluirlo como respaldo; si no, indicar que es un PDF escaneado
3. El PDF binario ya se envía a Gemini vía `types.Part.from_bytes`, así que Gemini puede leer la imagen

**Pros**: Cambio mínimo, sin nuevas dependencias, usa la infraestructura existente.
**Contras**: Depende 100% de Gemini para PDFs escaneados (si la API falla, no hay fallback). Latencia un poco mayor para escaneados.

---

### Alternativa 2: Agregar OCR local con PyMuPDF + Tesseract (pytesseract)

Agregar OCR en el backend antes de llamar a Gemini:
1. Instalar `pytesseract` + Tesseract OCR en el contenedor Docker
2. Cuando `get_text()` devuelva vacío, convertir cada página a imagen con PyMuPDF (`page.get_pixmap()`) y correr OCR con pytesseract
3. Usar el texto OCR como respaldo para Gemini

**Pros**: No dependes exclusivamente de Gemini para la extracción. Texto OCR disponible localmente.
**Contras**: Requiere instalar Tesseract en el Dockerfile (+150MB), nueva dependencia `pytesseract`, calidad OCR puede ser inferior a Gemini, mantenimiento adicional.

---

### Alternativa 3: Usar PyMuPDF para convertir páginas a imágenes y enviarlas a Gemini como imagen

En lugar de enviar el PDF binario, convertir las páginas a imágenes PNG y enviarlas como `inline_data` a Gemini Vision:
1. Si `get_text()` está vacío, usar `page.get_pixmap()` para convertir cada página a imagen
2. Enviar las imágenes a Gemini como `types.Part.from_bytes(data=img_bytes, mime_type='image/png')`
3. Si hay texto, incluirlo como contexto adicional

**Pros**: Mayor control sobre la resolución de imagen enviada a Gemini, compatible con modelos vision.
**Contras**: Más código, mayor tamaño del payload si el PDF tiene muchas páginas.

---

### Alternativa 4: OCR con EasyOCR (sin Tesseract)

Biblioteca Python pura basada en deep learning:
1. Agregar `easyocr` a requirements.txt
2. Cuando no hay texto, extraer imágenes del PDF y pasarlas por EasyOCR
3. Usar el texto como respaldo para Gemini

**Pros**: Sin instalación de sistema (no requiere Tesseract), soporta español, buena calidad.
**Contras**: Pesado (~500MB modelo), lento en CPU, primera ejecución descarga modelo, complejidad adicional.

---

## Decisión

Se implementa la **Alternativa 1** por mejor relación costo/beneficio:
- Gemini ya está integrado y ya recibe el PDF binario
- Gemini 2.5 Flash lee PDFs escaneados nativamente
- El cambio es mínimo (~10 líneas)
- No agrega dependencias ni peso al contenedor
- Si en el futuro se necesita más robustez, se puede combinar con la Alternativa 2

## Archivos a Modificar

- `backend/app/services/purchase_service.py` — Método `extract_from_pdf` (líneas 730-832)
