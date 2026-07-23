import os
import glob
import pandas as pd

# Rutas relativas dentro de la carpeta backend/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATOS_DIR = os.path.join(BASE_DIR, "datos")

# Nuevo archivo específico solo para el Excel
CORPUS_EXCEL_PATH = os.path.join(DATOS_DIR, "corpus_excel.txt")

def buscar_archivo_excel():
    """Busca automáticamente el primer archivo .xlsx dentro de backend/datos/"""
    patron = os.path.join(DATOS_DIR, "*.xlsx")
    archivos = glob.glob(patron)
    
    if not archivos:
        raise FileNotFoundError(f"No se encontró ningún archivo .xlsx en la carpeta: {DATOS_DIR}")
    
    archivo_encontrado = archivos[0]
    print(f"📄 Archivo Excel detectado: {os.path.basename(archivo_encontrado)}")
    return archivo_encontrado

def procesar_excel_a_corpus():
    try:
        excel_path = buscar_archivo_excel()
        df = pd.read_excel(excel_path)

        records = []
        current_tutor = None
        i = 0

        # Procesamiento del Excel de tutorías
        while i < len(df):
            val_col0 = str(df.iloc[i, 0]).strip() if pd.notna(df.iloc[i, 0]) else ""
            val_col1 = str(df.iloc[i, 1]).strip() if pd.notna(df.iloc[i, 1]) else ""

            if val_col0 == "Docente":
                i += 1
                if i < len(df) and pd.notna(df.iloc[i, 0]):
                    current_tutor = str(df.iloc[i, 0]).strip()
            elif val_col0 != "" and val_col0 != "nan" and current_tutor is None and not val_col0.isdigit():
                current_tutor = val_col0
            elif val_col0.isdigit() and current_tutor:
                records.append({
                    'codigo': val_col0,
                    'estudiante': val_col1,
                    'tutor': current_tutor
                })
            i += 1

        # Generación de la estructura del corpus
        # Opción limpia B: Solo un párrafo descriptivo fluido
        corpus_text = ""
        for item in records:
            header = f"TUTORIA_ESTUDIANTE_{item['codigo']}"
            corpus_text += f"### {header}\n\n"
            corpus_text += (
                f"El estudiante {item['estudiante']} con código universitario {item['codigo']} "
                f"tiene asignado(a) como tutor(a) académico(a) a {item['tutor']} para el periodo 2026-I.\n\n"
            )
            corpus_text += "---\n\n"

        # Guardar en corpus_excel.txt (nuevo archivo independiente)
        with open(CORPUS_EXCEL_PATH, 'w', encoding='utf-8') as f:
            f.write(corpus_text)

        print(f"✅ ¡Éxito! Se procesaron {len(records)} registros y se creó/actualizó '{CORPUS_EXCEL_PATH}'.")

    except Exception as e:
        print(f"❌ Error al procesar el archivo Excel: {e}")

if __name__ == "__main__":
    procesar_excel_a_corpus()