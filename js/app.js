document.addEventListener("DOMContentLoaded", () => {
    // Referencias a los botones
    const btnDescargar = document.getElementById("btn-descargar");
    const btnAnalisis = document.getElementById("btn-analisis");
    const btnAudio = document.getElementById("btn-audio");

    // Referencia al contenedor de resultados
    const resultsContainer = document.getElementById("results-container");

    // Lógica Botón 1: Descargar archivos DOF
    btnDescargar.addEventListener("click", () => {
        resultsContainer.innerHTML = `
            <div class="status-message">
                <div class="spinner"></div>
                <span>Estado: Descargando PDFs usando Selenium...</span>
            </div>
            <p style="color: var(--text-muted); margin-top: 1rem;">Navegando a la página del DOF, buscando la edición matutina y vespertina...</p>
        `;
    });

    // Lógica Botón 2: Realizar análisis
    btnAnalisis.addEventListener("click", () => {
        // Simulamos un tiempo de carga antes de mostrar el análisis
        resultsContainer.innerHTML = `
            <div class="status-message">
                <div class="spinner"></div>
                <span>Estado: Analizando documentos con Gemini IA...</span>
            </div>
        `;

        setTimeout(() => {
            const loremText = `¡Hola, qué tal! Este es el reporte financiero y regulatorio del Diario Oficial de la Federación para el sector manufacturero.

**El Dólar:** 
El Banco de México ha publicado el tipo de cambio FIX del dólar de los Estados Unidos de América en $18.50 MXN para solventar obligaciones pagaderas en la República Mexicana.

**Comercio Exterior:** 
La Secretaría de Economía ha actualizado las cuotas compensatorias para la importación de productos de acero, lo cual podría incrementar en un 5% los costos logísticos si tu cadena de suministro depende de estas importaciones.

**Materia Fiscal:** 
El SAT emitió una resolución de la Miscelánea Fiscal que ajusta los tiempos de declaración del IEPS aplicable a combustibles industriales. Impacto: La tesorería deberá adelantar el flujo de caja 5 días hábiles.

Fuera de esto, la edición de hoy no presenta nuevas regulaciones críticas. Recuerden, una gestión proactiva es su mejor ventaja competitiva. Soy su analista, ¡hasta pronto!`;

            resultsContainer.innerHTML = `
                <div class="analysis-content">
                    <h2 class="analysis-title">📄 Resumen del Análisis (Gemini AI)</h2>
                    <div class="analysis-text">${loremText.replace(/\n/g, '<br>')}</div>
                </div>
            `;
        }, 1500); // Simulamos 1.5 segundos de procesamiento
    });

    // Lógica Botón 3: Generar audio
    btnAudio.addEventListener("click", () => {
        // Solo inyectar el audio si ya hay un análisis en pantalla, de lo contrario mostrar aviso
        const hasAnalysis = resultsContainer.querySelector('.analysis-content');
        
        if (!hasAnalysis) {
            resultsContainer.innerHTML = `
                <div class="status-message" style="color: #dc2626;">
                    <span>⚠️ Primero debes realizar el análisis para poder generar el audio.</span>
                </div>
            `;
            return;
        }

        // Si ya hay análisis, agregamos la sección de audio en la parte inferior
        const audioSection = document.createElement('div');
        audioSection.className = 'audio-section';
        audioSection.innerHTML = `
            <p class="status-message" style="color: var(--text-main); font-size: 1rem;">
                <span class="icon">🎙️</span> Generando podcast...
            </p>
            <audio controls>
                <!-- Usamos un audio de muestra simulado -->
                <source src="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3" type="audio/mpeg">
                Tu navegador no soporta el elemento de audio.
            </audio>
            <a href="#" class="download-link">Descargar MP3</a>
        `;

        resultsContainer.appendChild(audioSection);
        
        // Simular el cambio de estado de "Generando podcast..." a "Podcast Listo"
        setTimeout(() => {
            const statusText = audioSection.querySelector('.status-message span:last-child');
            if(statusText) statusText.innerText = "¡Podcast generado con éxito!";
        }, 2000);
    });
});
