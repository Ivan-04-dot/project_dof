import os
import asyncio

# Desactivar la verificación SSL para webdriver_manager (Soluciona el error CERTIFICATE_VERIFY_FAILED)
os.environ['WDM_SSL_VERIFY'] = '0'
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

async def extraer_dof():
    """
    Función asíncrona para extraer los archivos PDF del Diario Oficial de la Federación (DOF).
    """
    print("Iniciando el proceso de extracción del DOF...")
    
    # 1. Configuración del directorio de descargas
    # Obtiene la ruta del directorio donde se encuentra este script
    project_root = os.path.dirname(os.path.abspath(__file__))
    download_dir = os.path.join(project_root, "pdfs_dof")
    
    # Crea la carpeta pdfs_dof si no existe
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
        print(f"Directorio de descargas creado en: {download_dir}")
    else:
        print(f"Utilizando directorio de descargas: {download_dir}")
        # Limpiar PDFs anteriores para evitar duplicidad y evitar que Gemini lea datos pasados
        archivos_antiguos = [os.path.join(download_dir, f) for f in os.listdir(download_dir) if f.endswith('.pdf')]
        if archivos_antiguos:
            print(f"Limpiando {len(archivos_antiguos)} archivo(s) PDF antiguo(s)...")
            for archivo in archivos_antiguos:
                try:
                    os.remove(archivo)
                except Exception as e:
                    print(f"Error al borrar {archivo}: {e}")

    # 2. Configuración de ChromeOptions
    chrome_options = Options()
    # Preferencias para la descarga automática
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,  # Desactiva el prompt de confirmación
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True  # Fuerza la descarga en lugar de abrir en el visor web
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    # Opciones adicionales recomendadas para estabilidad (especialmente útil en servidores)
    # chrome_options.add_argument("--headless=new") # Descomentar para ejecutar sin interfaz gráfica
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--start-maximized")

    # 3. Inicialización del Driver
    print("Configurando ChromeDriver...")
    # webdriver_manager se encarga de descargar y linkear la versión correcta del driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # 4. Navegación
        url_dof = "https://www.dof.gob.mx/"
        print(f"Navegando a la página principal del DOF: {url_dof}")
        driver.get(url_dof)
        
        # Espera explícita para asegurar que la página cargue correctamente
        wait = WebDriverWait(driver, 15)

        async def descargar_edicion_actual(nombre_contexto="página actual"):
            print(f"Buscando el botón de descarga en {nombre_contexto}...")
            xpath_selector = "//a[contains(@onclick, 'nota_to_pdf.php') or .//img[@title='Ver ejemplar completo en PDF']]"
            
            try:
                enlaces_pdf = wait.until(EC.presence_of_all_elements_located((By.XPATH, xpath_selector)))
                if enlaces_pdf:
                    print(f"Se encontraron {len(enlaces_pdf)} enlace(s) en {nombre_contexto}. Iniciando descarga...")
                    for idx, enlace in enumerate(enlaces_pdf, start=1):
                        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", enlace)
                        await asyncio.sleep(1) 
                        enlace.click()
                        print(f"Descarga iniciada ({nombre_contexto} - elemento {idx})")
                        await asyncio.sleep(2)
            except Exception as e:
                print(f"No se encontró el botón de descarga en {nombre_contexto} o ocurrió un error: {e}")

        # Descargamos la edición que aparece por defecto en la página principal
        await descargar_edicion_actual("la página principal")

        # 5. Buscar otras ediciones del día (Matutina / Vespertina)
        print("Buscando si hay otras ediciones disponibles el día de hoy...")
        # Buscamos por los parámetros 'edicion=MAT' y 'edicion=VES' en los enlaces (más seguro que por texto)
        xpath_otras_ediciones = "//a[contains(@href, 'edicion=MAT') or contains(@href, 'edicion=VES')]"
        
        try:
            # Buscamos los elementos sin esperar mucho porque podrían no existir (ej. si solo hay una edición)
            otras_ediciones = driver.find_elements(By.XPATH, xpath_otras_ediciones)
            urls_otras = [el.get_attribute("href") for el in otras_ediciones if el.get_attribute("href")]
            
            # Usamos un Set para no visitar la misma URL dos veces en caso de botones duplicados
            for url in set(urls_otras):
                print(f"Navegando a otra edición del día encontrada: {url}")
                driver.get(url)
                await asyncio.sleep(2) # Espera para que cargue la nueva página
                await descargar_edicion_actual("otra edición")
                
        except Exception as e:
            print(f"Error al buscar o navegar por otras ediciones: {e}")

        # 6. Esperar a que todas las descargas finalicen
        print("Esperando a que finalicen todas las descargas...")
        tiempo_espera = 0
        tiempo_max_espera = 60  # Segundos máximos para esperar las descargas
        
        while tiempo_espera < tiempo_max_espera:
            archivos_actuales = os.listdir(download_dir)
            descargando = any(archivo.endswith(".crdownload") for archivo in archivos_actuales)
            
            if not descargando:
                break
                
            await asyncio.sleep(2)  # Pausa de 2 segundos antes de volver a comprobar
            tiempo_espera += 2
            
        print("Proceso de descargas concluido.")

    except Exception as e:
        # Manejo básico de excepciones en caso de que la página no cargue o cambie la estructura
        print(f"Ocurrió un error general durante la ejecución de Selenium: {e}")
        
    finally:
        # Siempre asegurar que el navegador se cierre para no dejar procesos "zombies"
        print("Cerrando el navegador...")
        driver.quit()

# 6. Bloque de prueba independiente
if __name__ == "__main__":
    print("Iniciando prueba independiente del script scraper_dof.py")
    # Ejecutamos la función asíncrona usando el event loop de asyncio
    asyncio.run(extraer_dof())
    print("Prueba finalizada.")
