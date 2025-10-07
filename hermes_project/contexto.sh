#!/bin/bash

# Este script genera el contenido de los archivos críticos del módulo 'reportes'
# en formato Markdown para ser enviado al Asistente de IA.

# Define los archivos clave a incluir
ARCHIVOS_REPORTE=(
    "reportes/urls.py"
    "reportes/views.py"
    "reportes/serializers.py"
    "reportes/models.py" # Incluimos este por si tiene alguna tabla de parámetros
)

# Nombre del archivo de salida
OUTPUT_FILE="contexto_reportes_hermes.md"

# 1. Limpiar o crear el archivo de salida
echo "# CONTEXTO DEL MÓDULO REPORTES (GENERADO AUTOMÁTICAMENTE)" > "$OUTPUT_FILE"
echo "Generado: $(date)" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# 2. Iterar sobre cada archivo y añadir su contenido con formato
for FILE_PATH in "${ARCHIVOS_REPORTE[@]}"; do
    if [ -f "$FILE_PATH" ]; then
        echo "## 📄 Archivo: $FILE_PATH" >> "$OUTPUT_FILE"
        echo '```python' >> "$OUTPUT_FILE"
        cat "$FILE_PATH" >> "$OUTPUT_FILE"
        echo '```' >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
    else
        echo "## 📄 Archivo: $FILE_PATH" >> "$OUTPUT_FILE"
        echo '```python' >> "$OUTPUT_FILE"
        echo "# El archivo existe en el sistema, pero está vacío o no fue encontrado en la ruta." >> "$OUTPUT_FILE"
        echo '```' >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
    fi
done

echo "✅ Contexto generado con éxito en el archivo: $OUTPUT_FILE"