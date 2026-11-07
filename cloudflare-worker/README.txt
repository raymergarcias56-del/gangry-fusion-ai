GANGRY FUSION AI — MOTOR DE IMÁGENES

Este Worker conecta la interfaz publicada en GitHub Pages con FLUX.1 Schnell de Cloudflare Workers AI.

INSTALACIÓN (desde el panel web de Cloudflare; no requiere instalar programas):
1. Inicia sesión en https://dash.cloudflare.com/
2. Entra en Workers & Pages y crea un Worker nuevo.
3. Ponle el nombre gangry-fusion-image-api.
4. Abre Edit code y reemplaza todo el código de ejemplo por el contenido de worker.js.
5. Guarda y despliega (Deploy).
6. En el Worker, abre Settings > Bindings > Add binding > Workers AI.
7. En Variable name escribe exactamente AI. Guarda el binding y vuelve a desplegar si el panel lo solicita.
8. Copia la URL pública del Worker (termina en workers.dev).
9. En GANGRY FUSION AI > Image Studio, pega esa URL en “Conexión del motor de imágenes” y cambia de campo para guardarla.
10. Escribe una descripción, pulsa “Construir prompt” y luego “Generar imagen real”.

SEGURIDAD:
- No se necesita pegar API token ni contraseña en la web.
- El Worker solo acepta solicitudes desde https://raymergarcias56-del.github.io.
- No compartas el código de acceso de tu cuenta Cloudflare.

COSTO Y LÍMITES:
- Workers AI anuncia una asignación gratuita de 10,000 Neurons por día; el consumo depende del modelo y parámetros. Al agotarla, la generación puede fallar hasta el reinicio diario.
- Mantén la cuenta en el plan gratuito. No agregues método de pago ni actualices a un plan de pago.
