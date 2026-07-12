# Sistema IA de Notas de Crédito Tributarias - FastAPI

Este proyecto mejora el sistema anterior agregando un agente IA simulado inspirado en el ejemplo proporcionado.

## Qué incluye

- Backend con FastAPI.
- Frontend servido desde FastAPI.
- Login con roles: ADMIN, OPERADOR y CLIENTE.
- Registro de notas con documento simulado.
- Búsqueda inteligente de antecedentes por RUC y número de título.
- RAG simulado con base de conocimiento.
- Análisis IA de riesgo, pendientes, evidencia y precio sugerido.
- Decisión IA como recomendación, nunca como acción automática final.
- Aprobación humana.
- Ficha IA de negociación.
- Mercado y negociación simulada.
- Chat con agente IA.
- Dashboard.
- Historial del expediente.

## Usuarios de prueba

- admin / 123
- operador / 123
- cliente / 123

## Cómo ejecutar

1. Entrar a la carpeta backend:

```bash
cd backend
```

2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

3. Ejecutar el servidor:

```bash
python main.py
```

4. Abrir en el navegador:

```text
http://127.0.0.1:8000
```

## Flujo recomendado de demo

1. Login como admin u operador.
2. Registrar una nota.
3. Copiar el ID de la nota.
4. Buscar antecedentes IA.
5. Analizar con IA.
6. Preguntar al chat: ¿Qué falta corregir? / ¿Cuál es el riesgo? / ¿Puede negociarse?
7. Aprobar recomendación IA.
8. Generar ficha IA.
9. Publicar en mercado.
10. Solicitar compra.
11. Avanzar negociación hasta solicitud de endoso.
12. Cerrar simulación.

## Nota importante

Este sistema es educativo y simulado. No ejecuta liquidación, transferencia ni endoso real. Las acciones sensibles quedan como propuestas o solicitudes de aprobación humana.
