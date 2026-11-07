// GANGRY FUSION AI — Image generation API
// Deploy as a Cloudflare Worker and add an AI binding named AI.
const ALLOWED_ORIGIN = 'https://raymergarcias56-del.github.io';
const MODEL = '@cf/black-forest-labs/flux-1-schnell';

function corsHeaders(origin) {
  return {
    'Access-Control-Allow-Origin': origin === ALLOWED_ORIGIN ? ALLOWED_ORIGIN : 'null',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Vary': 'Origin',
  };
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin') || '';
    const headers = corsHeaders(origin);
    if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers });
    if (origin !== ALLOWED_ORIGIN) return Response.json({ error: 'Origen no autorizado.' }, { status: 403, headers });
    if (request.method !== 'POST') return Response.json({ error: 'Usa POST para generar imágenes.' }, { status: 405, headers });
    if (!env.AI) return Response.json({ error: 'Falta configurar el AI binding llamado AI en Cloudflare.' }, { status: 503, headers });

    try {
      const body = await request.json();
      const prompt = typeof body.prompt === 'string' ? body.prompt.trim() : '';
      if (!prompt) return Response.json({ error: 'Escribe una descripción para la imagen.' }, { status: 400, headers });
      if (prompt.length > 2048) return Response.json({ error: 'La descripción supera el máximo de 2048 caracteres.' }, { status: 400, headers });

      const result = await env.AI.run(MODEL, { prompt, steps: 4 });
      if (!result || !result.image) throw new Error('El modelo no devolvió una imagen.');
      return Response.json({ image: result.image, model: MODEL }, { headers });
    } catch (error) {
      const message = String(error?.message || error);
      const status = /limit|quota|neuron/i.test(message) ? 429 : 502;
      return Response.json({ error: status === 429 ? 'Se alcanzó el límite gratuito diario de IA. Inténtalo después del reinicio.' : `Error al generar: ${message.slice(0, 220)}` }, { status, headers });
    }
  },
};
