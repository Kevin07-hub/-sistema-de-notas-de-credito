import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any

from agente_ia import (
    analizar_nota_ia,
    buscar_antecedentes_ia,
    responder_chat_ia,
    generar_ficha_ia,
    generar_dashboard
)

app = FastAPI(title="Sistema IA de Notas de Crédito Tributarias", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# MEMORIA SIMULADA
# =========================
usuarios = [
    {"id": 1, "usuario": "admin", "clave": "123", "rol": "ADMIN"},
    {"id": 2, "usuario": "operador", "clave": "123", "rol": "OPERADOR"},
    {"id": 3, "usuario": "cliente", "clave": "123", "rol": "CLIENTE"},
]

notas: List[Dict[str, Any]] = []
historial: List[Dict[str, Any]] = []
mercado: List[Dict[str, Any]] = []

# =========================
# MODELOS
# =========================
class LoginData(BaseModel):
    usuario: str
    clave: str

class NotaCreate(BaseModel):
    usuario: str
    rol: str
    titular: str
    ruc: str
    numeroTitulo: str
    tipoNota: str
    valorNominal: float
    saldoDisponible: float
    deudaCliente: float
    documentoCargado: bool = False
    nombreDocumento: str = "Sin documento"
    tipoDocumento: str = "No aplica"
    observacion: str = ""

class DecisionData(BaseModel):
    usuario: str
    decision: str
    observacion: Optional[str] = ""

class MercadoPublicar(BaseModel):
    usuario: str
    idNota: int
    precioVenta: float

class UsuarioRol(BaseModel):
    usuario: str
    rol: str

class SolicitudCompra(BaseModel):
    usuario: str

class ChatData(BaseModel):
    pregunta: str

# =========================
# UTILIDADES
# =========================
def ahora():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def agregar_historial(id_nota: int, accion: str, usuario: str, comentario: str):
    historial.append({
        "id": len(historial) + 1,
        "idNota": id_nota,
        "fecha": ahora(),
        "usuario": usuario,
        "accion": accion,
        "comentario": comentario
    })

def buscar_nota(id_nota: int):
    return next((n for n in notas if n["id"] == id_nota), None)

def buscar_item_mercado(id_mercado: int):
    return next((m for m in mercado if m["idMercado"] == id_mercado), None)

# =========================
# FRONTEND EN FASTAPI
# =========================
frontend_path = os.path.join(os.path.dirname(__file__), "frontend")

@app.get("/", response_class=HTMLResponse)
def home():
    html_path = os.path.join(frontend_path, "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()

app.mount("/static", StaticFiles(directory=frontend_path), name="static")

# =========================
# API
# =========================
@app.post("/login")
def login(data: LoginData):
    for u in usuarios:
        if u["usuario"] == data.usuario and u["clave"] == data.clave:
            return {"acceso": True, "usuario": u["usuario"], "rol": u["rol"], "id": u["id"]}
    raise HTTPException(status_code=401, detail="Usuario o clave incorrectos")

@app.post("/notas")
def registrar_nota(data: NotaCreate):
    if data.rol not in ["ADMIN", "OPERADOR"]:
        raise HTTPException(status_code=403, detail="Solo ADMIN u OPERADOR pueden registrar notas")

    nota = {
        "id": len(notas) + 1,
        "titular": data.titular,
        "ruc": data.ruc,
        "numeroTitulo": data.numeroTitulo,
        "tipoNota": data.tipoNota,
        "valorNominal": data.valorNominal,
        "saldoDisponible": data.saldoDisponible,
        "deudaCliente": data.deudaCliente,
        "documentoCargado": data.documentoCargado,
        "nombreDocumento": data.nombreDocumento,
        "tipoDocumento": data.tipoDocumento,
        "observacion": data.observacion,
        "estadoNota": "BORRADOR",
        "datosValidos": False,
        "duplicado": False,
        "aprobadoOperador": False,
        "riesgo": {"nivel": "SIN CALCULAR", "puntaje": 0, "factores": []},
        "pendientes": [],
        "recomendacion": "Pendiente de análisis IA",
        "siguienteAccion": "Buscar antecedentes y ejecutar análisis IA",
        "precioSugerido": 0,
        "decisionIA": "Pendiente",
        "contextoIA": [],
        "responsableActual": data.usuario
    }
    notas.append(nota)
    agregar_historial(nota["id"], "Nota registrada", data.usuario, "Se creó expediente inicial con documento simulado")
    return {"mensaje": "Nota registrada correctamente", "nota": nota}

@app.get("/notas")
def listar_notas():
    return {"notas": notas, "historial": historial}
@app.get("/buscar")
def buscar_notas(titular: Optional[str] = None, ruc: Optional[str] = None, estado: Optional[str] = None):
    resultados = notas
    if titular:
        resultados = [n for n in resultados if titular.lower() in n["titular"].lower()]
    if ruc:
        resultados = [n for n in resultados if ruc in n["ruc"]]
    if estado:
        resultados = [n for n in resultados if estado.upper() == n["estadoNota"]]
    return {"resultados": resultados}
@app.get("/notas/{id_nota}/antecedentes")
def antecedentes(id_nota: int):
    nota = buscar_nota(id_nota)
    if not nota:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    resultado = buscar_antecedentes_ia(nota)
    nota["duplicado"] = resultado["duplicado"]
    nota["contextoIA"] = resultado["contextoUsado"]
    if resultado["duplicado"]:
        nota["estadoNota"] = "OBSERVADO"
    else:
        nota["estadoNota"] = "PENDIENTE_VALIDACION"
    nota["siguienteAccion"] = "Ejecutar análisis IA y revisar antecedentes sugeridos"
    agregar_historial(id_nota, "Búsqueda inteligente de antecedentes", nota["responsableActual"], "IA consultó antecedentes simulados por RUC y título")
    return resultado

@app.post("/notas/{id_nota}/analizar-ia")
def analizar_ia(id_nota: int):
    nota = buscar_nota(id_nota)
    if not nota:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    resultado = analizar_nota_ia(nota)
    nota.update(resultado["actualizacionNota"])
    agregar_historial(id_nota, "Análisis IA", nota["responsableActual"], nota["decisionIA"])
    return resultado

@app.post("/notas/{id_nota}/aprobar")
def aprobar(id_nota: int, data: DecisionData):
    nota = buscar_nota(id_nota)
    if not nota:
        raise HTTPException(status_code=404, detail="Nota no encontrada")

    decision = data.decision.upper()
    if decision == "SI":
        nota["aprobadoOperador"] = True
        if nota["estadoNota"] == "VALIDADO":
            nota["estadoNota"] = "LISTO_PARA_NEGOCIAR"
            nota["siguienteAccion"] = "Generar ficha de negociación"
        mensaje = "Acción recomendada aprobada por el operador"
    elif decision == "EDITAR":
        nota["aprobadoOperador"] = False
        nota["estadoNota"] = "OBSERVADO"
        nota["observacion"] = data.observacion or nota["observacion"]
        nota["siguienteAccion"] = "Revisar cambios del operador"
        mensaje = "Acción editada y enviada a revisión"
    else:
        nota["aprobadoOperador"] = False
        mensaje = "Acción rechazada por el operador"

    agregar_historial(id_nota, "Aprobación humana", data.usuario, decision)
    return {"mensaje": mensaje, "nota": nota}

@app.post("/notas/{id_nota}/ficha")
def ficha(id_nota: int, data: DecisionData):
    nota = buscar_nota(id_nota)
    if not nota:
        raise HTTPException(status_code=404, detail="Nota no encontrada")

    ficha_resultado = generar_ficha_ia(nota)
    decision = data.decision.upper()
    if nota["estadoNota"] == "LISTO_PARA_NEGOCIAR" and nota["aprobadoOperador"]:
        if decision == "SI":
            nota["estadoNota"] = "FICHA_APROBADA"
            nota["siguienteAccion"] = "Publicar en mercado simulado"
        else:
            nota["estadoNota"] = "OBSERVADO"
            nota["siguienteAccion"] = "Editar ficha de negociación"
        agregar_historial(id_nota, "Ficha IA de negociación", data.usuario, decision)
        return {"mensaje": "Ficha generada por IA", "ficha": ficha_resultado, "nota": nota}

    raise HTTPException(status_code=400, detail="La nota debe estar validada, aprobada y lista para negociar")

@app.get("/notas/{id_nota}/expediente")
def expediente(id_nota: int):
    nota = buscar_nota(id_nota)
    if not nota:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    hist = [h for h in historial if h["idNota"] == id_nota]
    return {"responsable": nota["responsableActual"], 
"estadoActual": nota["estadoNota"],
    "siguienteAccion": nota["siguienteAccion"],
    "expediente": nota,
    "historial": hist
}

@app.post("/notas/{id_nota}/chat")
def chat(id_nota: int, data: ChatData):
    nota = buscar_nota(id_nota)
    if not nota:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    respuesta = responder_chat_ia(nota, data.pregunta)
    agregar_historial(id_nota, "Chat IA", nota["responsableActual"], data.pregunta)
    return {"pregunta": data.pregunta, "respuestaIA": respuesta}

@app.post("/mercado/publicar")
def publicar_mercado(data: MercadoPublicar):
    nota = buscar_nota(data.idNota)
    if not nota:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    if nota["estadoNota"] != "FICHA_APROBADA":
        raise HTTPException(status_code=400, detail="La nota debe tener ficha aprobada")

    item = {
        "idMercado": len(mercado) + 1,
        "idNota": nota["id"],
        "titulo": nota["numeroTitulo"],
        "saldo": nota["saldoDisponible"],
        "precioVenta": data.precioVenta,
        "precioSugeridoIA": nota["precioSugerido"],
        "vendedor": data.usuario,
        "comprador": None,
        "estadoNegociacion": "DISPONIBLE"
    }
    mercado.append(item)
    nota["estadoNota"] = "PUBLICADO"
    agregar_historial(nota["id"], "Publicación en mercado", data.usuario, "Nota publicada en mercado simulado")
    return {"mensaje": "Nota publicada en mercado simulado", "mercado": item}

@app.get("/mercado")
def ver_mercado():
    return {"mercado": mercado}

@app.post("/mercado/{id_mercado}/solicitar-compra")
def solicitar_compra(id_mercado: int, data: SolicitudCompra):
    item = buscar_item_mercado(id_mercado)
    if not item:
        raise HTTPException(status_code=404, detail="ID mercado no encontrado")
    if item["estadoNegociacion"] != "DISPONIBLE":
        raise HTTPException(status_code=400, detail="La nota no está disponible")
    item["comprador"] = data.usuario
    item["estadoNegociacion"] = "SOLICITUD_COMPRA"
    nota = buscar_nota(item["idNota"])
    nota["estadoNota"] = "EN_NEGOCIACION"
    agregar_historial(nota["id"], "Solicitud de compra", data.usuario, "Solicitud registrada; no es compra final")
    return {"mensaje": "Solicitud de compra registrada", "mercado": item}

@app.post("/mercado/{id_mercado}/avanzar")
def avanzar_mercado(id_mercado: int, data: UsuarioRol):
    if data.rol not in ["ADMIN", "OPERADOR"]:
        raise HTTPException(status_code=403, detail="Solo ADMIN u OPERADOR pueden avanzar negociación")
    item = buscar_item_mercado(id_mercado)
    if not item:
        raise HTTPException(status_code=404, detail="ID mercado no encontrado")
    flujo = {
        "SOLICITUD_COMPRA": "SOLICITUD_APROBADA",
        "SOLICITUD_APROBADA": "PROPUESTA_LIQUIDACION",
        "PROPUESTA_LIQUIDACION": "SOLICITUD_ENDOSO"
    }
    actual = item["estadoNegociacion"]
    if actual not in flujo:
        raise HTTPException(status_code=400, detail=f"No puede avanzar desde estado {actual}")
    item["estadoNegociacion"] = flujo[actual]
    nota = buscar_nota(item["idNota"])
    agregar_historial(nota["id"], "Avance negociación simulada", data.usuario, item["estadoNegociacion"])
    return {
        "mensaje": "Negociación avanzada en modo simulado",
        "mercado": item,
        "advertencia": "No se ejecuta liquidación, transferencia ni endoso real"
    }

@app.post("/mercado/{id_mercado}/cerrar")
def cerrar_mercado(id_mercado: int, data: DecisionData):
    item = buscar_item_mercado(id_mercado)
    if not item:
        raise HTTPException(status_code=404, detail="ID mercado no encontrado")
    if item["estadoNegociacion"] != "SOLICITUD_ENDOSO":
        raise HTTPException(status_code=400, detail="Debe existir solicitud de endoso simulada")
    if data.decision.upper() == "SI":
        item["estadoNegociacion"] = "NEGOCIACION_CERRADA"
        nota = buscar_nota(item["idNota"])
        nota["estadoNota"] = "CERRADO"
        agregar_historial(nota["id"], "Cierre simulado", data.usuario, "Cierre aprobado en simulación")
    else:
        item["estadoNegociacion"] = "PROPUESTA_LIQUIDACION"
    return {"mensaje": "Cierre procesado", "mercado": item}

@app.get("/dashboard")
def dashboard():
    return generar_dashboard(notas, mercado)

@app.get("/historial")
def ver_historial():
    return historial

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
