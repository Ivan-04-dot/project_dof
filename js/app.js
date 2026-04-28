document.addEventListener("DOMContentLoaded", () => {
    // Referencias a los botones
    const btnDescargar = document.getElementById("btn-descargar");
    const btnAnalisis = document.getElementById("btn-analisis");
    const btnAudio = document.getElementById("btn-audio");

    // Referencia al contenedor de resultados
    const resultsContainer = document.getElementById("results-container");

    // URL base del backend FastAPI
    const API_BASE_URL = "http://127.0.0.1:8000/api";

    // Función auxiliar para mostrar un mensaje de error
    const showError = (message) => {
        resultsContainer.innerHTML = `
            <div class="status-message" style="color: #dc2626;">
                <span>❌ Error: ${message}</span>
            </div>
        `;
    };

    // Lógica Botón 1: Descargar archivos DOF
    btnDescargar.addEventListener("click", async () => {
        resultsContainer.innerHTML = `
            <div class="status-message">
                <div class="spinner"></div>
                <span>Estado: Descargando PDFs usando Selenium...</span>
            </div>
            <p style="color: var(--text-muted); margin-top: 1rem;">Navegando a la página del DOF, buscando las ediciones del día. Esto puede tomar varios segundos...</p>
        `;

        try {
            const response = await fetch(`${API_BASE_URL}/descargar`);
            const data = await response.json();
            
            if (response.ok) {
                resultsContainer.innerHTML = `
                    <div class="status-message" style="color: #16a34a;">
                        <span>✅ ¡Descarga completada! Los archivos PDF se encuentran listos.</span>
                    </div>
                `;
                // Habilitamos el botón de análisis
                btnAnalisis.removeAttribute('disabled');
            } else {
                showError(data.detail || "Hubo un error en el servidor al descargar.");
            }
        } catch (error) {
            showError("No se pudo conectar con el servidor FastAPI. Verifica que uvicorn esté corriendo.");
        }
    });

    // Lógica Botón 2: Realizar análisis
    btnAnalisis.addEventListener("click", async () => {
        resultsContainer.innerHTML = `
            <div class="status-message">
                <div class="spinner"></div>
                <span>Estado: Analizando documentos con Gemini IA...</span>
            </div>
            <p style="color: var(--text-muted); margin-top: 1rem;">La Inteligencia Artificial está leyendo los documentos y generando el guion estructurado...</p>
        `;

        try {
            const response = await fetch(`${API_BASE_URL}/analizar`);
            const data = await response.json();

            if (response.ok) {
                resultsContainer.innerHTML = `
                    <div class="analysis-content">
                        <h2 class="analysis-title">📄 Resumen del Análisis (Gemini AI)</h2>
                        <div class="analysis-text">${data.data.replace(/\n/g, '<br>')}</div>
                    </div>
                `;
                // Habilitamos el botón de generar audio
                btnAudio.removeAttribute('disabled');
            } else {
                showError(data.detail || "Hubo un error en el servidor al analizar.");
            }
        } catch (error) {
            showError("No se pudo conectar con el servidor FastAPI.");
        }
    });

    // Lógica Botón 3: Generar audio
    btnAudio.addEventListener("click", async () => {
        const hasAnalysis = resultsContainer.querySelector('.analysis-content');
        
        if (!hasAnalysis) {
            showError("Primero debes realizar el análisis para poder generar el audio.");
            return;
        }

        // Agregamos el indicador de carga para el audio
        const audioSection = document.createElement('div');
        audioSection.className = 'audio-section';
        audioSection.innerHTML = `
            <div class="status-message">
                <div class="spinner"></div>
                <span>Estado: Sintetizando voz con Microsoft Edge TTS...</span>
            </div>
        `;
        resultsContainer.appendChild(audioSection);

        try {
            // El endpoint devuelve un archivo directamente (FileResponse)
            const response = await fetch(`${API_BASE_URL}/audio`);
            
            if (!response.ok) {
                const errData = await response.json();
                audioSection.innerHTML = `
                    <span style="color: #dc2626;">❌ Error al generar audio: ${errData.detail}</span>
                `;
                return;
            }

            // Convertimos la respuesta en un blob binario para reproducirlo en el navegador
            const audioBlob = await response.blob();
            const audioUrl = URL.createObjectURL(audioBlob);

            audioSection.innerHTML = `
                <p class="status-message" style="color: #16a34a; font-size: 1rem;">
                    <span class="icon">✅</span> ¡Podcast generado con éxito!
                </p>
                <audio controls>
                    <source src="${audioUrl}" type="audio/mpeg">
                    Tu navegador no soporta el elemento de audio.
                </audio>
                <a href="${audioUrl}" download="podcast_dof.mp3" class="download-link">Descargar MP3</a>
            `;
        } catch (error) {
            audioSection.innerHTML = `
                <span style="color: #dc2626;">❌ No se pudo conectar con el servidor para descargar el audio.</span>
            `;
        }
    });
});
