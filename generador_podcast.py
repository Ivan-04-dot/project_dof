import os
import asyncio
import edge_tts
from datetime import datetime
async def generar_audio():
    """
    Lee el archivo de texto (guion) más reciente de la carpeta Summaries/ 
    y genera un archivo de audio .mp3 usando la voz neuronal de Microsoft Edge TTS.
    """
    print("Iniciando el Generador de Podcast TTS...")
    
    # 1. Configuración de Rutas y Directorios
    project_root = os.path.dirname(os.path.abspath(__file__))
    summaries_dir = os.path.join(project_root, "Summaries")
    podcasts_dir = os.path.join(project_root, "Podcasts")
    
    # Verificar si la carpeta Summaries existe
    if not os.path.exists(summaries_dir):
        print(f"Error: La carpeta {summaries_dir} no existe. Ejecuta el analista primero.")
        return None
        
    # Crear la carpeta Podcasts si no existe
    if not os.path.exists(podcasts_dir):
        os.makedirs(podcasts_dir)
        print(f"Carpeta creada: {podcasts_dir}")
        
    # 2. Buscar el guion más reciente en la carpeta Summaries/
    archivos_txt = [os.path.join(summaries_dir, f) for f in os.listdir(summaries_dir) if f.endswith('.txt')]
    
    if not archivos_txt:
        print(f"Error: La carpeta {summaries_dir} está vacía. No hay guiones para convertir.")
        return None
        
    ultimo_txt_path = max(archivos_txt, key=os.path.getmtime)
    print(f"Guion seleccionado para el audio: {os.path.basename(ultimo_txt_path)}")
    
    # 3. Leer el contenido del guion
    try:
        with open(ultimo_txt_path, "r", encoding="utf-8") as f:
            texto_guion = f.read()
    except Exception as e:
        print(f"Error al intentar leer el archivo de texto: {e}")
        return None
        
    # Si el texto está vacío
    if not texto_guion.strip():
        print("El archivo de texto está vacío. No se generará audio.")
        return None
        
    # 4. Configuración del sintetizador de voz (Edge TTS)
    # Seleccionamos una voz neuronal en Español de México (Jorge para voz masculina, Dalia para femenina)
    voz_seleccionada = "es-MX-JorgeNeural"
    
    # Construcción dinámica del nombre del archivo de salida
    fecha_str = datetime.now().strftime("%Y%m%d")
    nombre_archivo_mp3 = f"podcast_dof_{fecha_str}.mp3"
    ruta_mp3 = os.path.join(podcasts_dir, nombre_archivo_mp3)
    
    print(f"Generando el audio con la voz de {voz_seleccionada}...")
    print("Por favor espera, este proceso puede tomar un momento dependiendo de la longitud del texto...")
    
    # 5. Generación del Audio (Proceso Asíncrono)
    try:
        # Se crea el objeto Communicate con el texto y la voz deseada
        comunicador = edge_tts.Communicate(text=texto_guion, voice=voz_seleccionada)
        
        # Ejecutamos la función de guardado de forma asíncrona
        await comunicador.save(ruta_mp3)
        
        print(f"¡Éxito! El podcast se ha guardado correctamente en: {ruta_mp3}")
        return ruta_mp3
        
    except Exception as e:
        print(f"Ocurrió un error inesperado al generar el audio: {e}")
        return None

# 6. Bloque de prueba independiente
if __name__ == "__main__":
    print("--- INICIANDO PRUEBA INDEPENDIENTE: GENERADOR DE PODCAST ---")
    resultado_audio = asyncio.run(generar_audio())
    
    if resultado_audio:
        print("\n==================================================")
        print(f"🎙️ PODCAST GENERADO: {resultado_audio}")
        print("Puedes reproducirlo en tu reproductor multimedia favorito.")
        print("==================================================\n")
