import os
import asyncio
from dotenv import load_dotenv
import google.generativeai as genai
from datetime import datetime
import PyPDF2

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("No se encontro la variable GEMINI_API_KEY en el archivo .env")

genai.configure(api_key=API_KEY)

def extraer_texto_local(ruta_pdf):
    texto_completo = ""
    try:
        with open(ruta_pdf, 'rb') as archivo:
            lector = PyPDF2.PdfReader(archivo)
            for pagina in lector.pages:
                texto_pagina = pagina.extract_text()
                if texto_pagina:
                    texto_completo += texto_pagina + "\n"
    except Exception as e:
        print(f"Error extrayendo texto de {ruta_pdf}: {e}")
    return texto_completo

async def generar_guion_dof():
    print("Iniciando el Analista IA de Gemini (Modo de lectura local sin subida a la nube)...")
    
    project_root = os.path.dirname(os.path.abspath(__file__))
    download_dir = os.path.join(project_root, "pdfs_dof")
    
    if not os.path.exists(download_dir):
        print(f"Error: La carpeta {download_dir} no existe.")
        return None
        
    archivos_pdf = [os.path.join(download_dir, f) for f in os.listdir(download_dir) if f.endswith('.pdf')]
    
    if not archivos_pdf:
        print("Error: No se encontraron archivos PDF.")
        return None
        
    print(f"Se encontraron {len(archivos_pdf)} archivo(s) PDF para analizar.")
    
    try:
        texto_dof_combinado = ""
        for pdf_path in archivos_pdf:
            print(f"Leyendo texto localmente de: {os.path.basename(pdf_path)}...")
            texto_extraido = await asyncio.to_thread(extraer_texto_local, pdf_path)
            texto_dof_combinado += f"\n\n--- DOCUMENTO: {os.path.basename(pdf_path)} ---\n" + texto_extraido
        
        modelo = genai.GenerativeModel(model_name="gemini-2.5-flash")
        
        prompt_maestro = f"""
Actúa como un Analista Financiero Senior y un Locutor de Podcast experto en la industria manufacturera de México.

Tu tarea es analizar el siguiente texto extraído de la edición de hoy del Diario Oficial de la Federación (DOF) y generar el guion directo para un noticiero de audio (cápsula de 2 a 3 minutos).

TEXTO DEL DOF:
{texto_dof_combinado[:50000]}

Instrucciones de Extracción (Filtro Estricto):
Ignora nombramientos políticos, expropiaciones menores o temas agrarios. Céntrate EXCLUSIVAMENTE en la información que impacte la estructura de costos, operaciones, logística o planeación fiscal de una planta de manufactura, buscando específicamente:

Tipo de Cambio (Prioridad 1): Localiza la publicación del Banco de México (Banxico) con el tipo de cambio FIX del dólar de los EE.UU. (USD/MXN) para solventar obligaciones pagaderas en la República Mexicana.

Comercio Exterior: Modificaciones a la TIGIE, aranceles, cuotas compensatorias (antidumping), permisos previos de importación/exportación o avisos de la Secretaría de Economía.

Materia Fiscal: Estímulos fiscales, cambios en IEPS (combustibles), resoluciones de la Miscelánea Fiscal (SAT) o cuotas obrero-patronales (IMSS/Infonavit).

Normativas y Energía: Nuevas Normas Oficiales Mexicanas (NOM) que afecten maquinaria o procesos, o acuerdos de la CRE/CFE sobre tarifas industriales.

Estructura del Guion (Formato para Audio):
Redacta la respuesta como un guion fluido, diseñado para ser leído por una voz robótica (TTS), sin viñetas con símbolos especiales, sin tablas y usando puntuación clara para forzar pausas (comas y puntos).

Intro: Un saludo enérgico, corporativo y directo. Ejemplo: "Hola, qué tal. Este es el reporte financiero y regulatorio del Diario Oficial de la Federación para el sector manufacturero..."

El Dólar: Menciona de inmediato el tipo de cambio reportado por Banxico.

Impactos Clave: Resume máximo los 3 puntos más críticos del día. Para cada uno explica brevemente: ¿De qué trata la publicación? y, lo más importante, ¿Cómo afecta a la tesorería o a la operación de la fábrica?

Aviso de Calma (Solo si aplica): Si hoy no hay nada relevante para la manufactura más allá del dólar, indícalo claramente: "Fuera del tipo de cambio, la edición de hoy no presenta nuevas regulaciones o impactos fiscales directos para la industria."

Cierre: Una despedida breve y profesional.
"""

        print("Solicitando analisis a la IA (enviando texto directo)...")
        respuesta = await asyncio.to_thread(modelo.generate_content, prompt_maestro)
        
        texto_resultado = respuesta.text
        
        fecha_str = datetime.now().strftime("%Y%m%d")
        
        # Crear la carpeta de resúmenes si no existe
        resumenes_dir = os.path.join(project_root, "Summaries")
        if not os.path.exists(resumenes_dir):
            os.makedirs(resumenes_dir)
            
        ruta_txt = os.path.join(resumenes_dir, f"guion_dof_{fecha_str}.txt")
        
        with open(ruta_txt, "w", encoding="utf-8") as f:
            f.write(texto_resultado)
            
        print(f"El guion se ha guardado exitosamente en: {ruta_txt}")
        return texto_resultado
        
    except Exception as e:
        print(f"Ocurrio un error al comunicarse con Gemini: {e}")
        return None

if __name__ == "__main__":
    print("--- INICIANDO PRUEBA INDEPENDIENTE: ANALISTA GEMINI (LOCAL) ---")
    resultado = asyncio.run(generar_guion_dof())
    if resultado:
        print("\n==================================================")
        print("CONTENIDO DEL ARCHIVO .TXT GENERADO:")
        print("==================================================\n")
        print(resultado)
