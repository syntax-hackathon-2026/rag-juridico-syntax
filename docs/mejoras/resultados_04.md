# Resultados analisis abstencion - e02_v0

Comando ejecutado: python src/evaluacion/analisis_abstencion.py --experimento e02_v0

Archivos leidos:
 - C:\Users\sofim\OneDrive\Desktop\VisualStudios\hackathon\rag-juridico-syntax.worktrees\trabaja-u-nicamente-en-la-rama-sofi-comprueba\salidas\trazas\e02_v0.jsonl
 - C:\Users\sofim\OneDrive\Desktop\VisualStudios\hackathon\rag-juridico-syntax.worktrees\trabaja-u-nicamente-en-la-rama-sofi-comprueba\evaluation\generacion\e02_v0\errores.csv

Total ids union: 50
Aciertos (correcta==1 && trace): 11
Errores (correcta==0 && trace): 4
Exclusiones (diagnostico in SCHEMA/ABSTENCION/CORPUS): 1
Faltantes traza: 0, faltantes error: 0

Se generaron 99 filas de candidatos de umbrales en C:\Users\sofim\OneDrive\Desktop\VisualStudios\hackathon\rag-juridico-syntax.worktrees\trabaja-u-nicamente-en-la-rama-sofi-comprueba\evaluation\abstencion\e02_v0_umbral_candidatos.csv
Se genero el CSV por-item en C:\Users\sofim\OneDrive\Desktop\VisualStudios\hackathon\rag-juridico-syntax.worktrees\trabaja-u-nicamente-en-la-rama-sofi-comprueba\evaluation\abstencion\e02_v0_senales.csv

Pendientes:
 - Revisar definicion exacta de 'exclusiones' con el equipo (aqui se usaron SCHEMA/ABSTENCION/CORPUS).
 - Elegir a lo sumo 2-3 señales por formato para la Fase B.
 - Ejecutar A/B sobre sample_50 con las reglas propuestas.
