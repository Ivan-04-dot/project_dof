from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

# Importamos las funciones asíncronas de nuestros módulos
from scraper_dof import extraer_dof
from analista_gemini import generar_guion_dof
from generador_podcast import generar_audio

app = FastAPI(title="Backend DOF Podcast", version="1.0")

# Configuración estricta de CORS para permitir al frontend (HTML local) hacer peticiones
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite peticiones de cualquier origen (útil para desarrollo local)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/descargar")
async def api_descargar():
    """Endpoint para iniciar el web scraping del DOF."""
    try:
        await extraer_dof()
        return {"status": "success", "message": "Archivos PDF descargados correctamente en la carpeta pdfs_dof."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante la descarga: {str(e)}")

@app.get("/api/analizar")
async def api_analizar():
    """Endpoint para procesar los PDFs descargados y generar el guion con Gemini."""
    try:
        # Nota: La función original de tu prompt era analizar_ultimo_pdf(), pero en la 
        # Fase 2 la renombramos a generar_guion_dof() para que procesara TODOS los PDFs
        resultado = await generar_guion_dof()
        
        if not resultado:
            raise HTTPException(status_code=500, detail="No se pudo generar el guion. Revisa la consola para más detalles.")
            
        return {
            "status": "success", 
            "message": "Análisis completado.",
            "data": resultado
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante el análisis de Gemini: {str(e)}")

@app.get("/api/audio")
async def api_audio():
    """Endpoint para generar el audio usando Edge-TTS y servir el archivo MP3 resultante."""
    try:
        ruta_mp3 = await generar_audio()
        
        if not ruta_mp3 or not os.path.exists(ruta_mp3):
            raise HTTPException(status_code=500, detail="El archivo de audio no se generó correctamente.")
            
        # Usamos FileResponse para enviar el archivo binario MP3 al frontend directamente
        # Esto permite que el reproductor de <audio> del frontend lo lea y reproduzca
        return FileResponse(
            path=ruta_mp3, 
            media_type="audio/mpeg", 
            filename=os.path.basename(ruta_mp3)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante la generación de audio: {str(e)}")

# ==============================================================================
# RUTAS DEL FRONTEND
# ==============================================================================
# Servimos las carpetas css, js e iconos de manera estática
app.mount("/css", StaticFiles(directory="css"), name="css")
app.mount("/js", StaticFiles(directory="js"), name="js")
app.mount("/iconos", StaticFiles(directory="iconos"), name="iconos")

# La ruta principal ("/") devolverá nuestro index.html
@app.get("/")
async def serve_frontend():
    return FileResponse("index.html")

# ==============================================================================
# INSTRUCCIONES DE EJECUCIÓN:
# Para levantar este servidor web, abre tu terminal, asegúrate de tener tu 
# entorno virtual (venv) activado, y ejecuta el siguiente comando:
#
# uvicorn main:app --reload
#
# El servidor estará disponible en: http://127.0.0.1:8000
# Puedes ver la documentación interactiva en: http://127.0.0.1:8000/docs
# ==============================================================================
