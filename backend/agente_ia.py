from datetime import datetime
from typing import Dict, Any, List

# =========================
# BASE DE CONOCIMIENTO / RAG SIMULADO
# =========================
base_conocimiento = [
    "Notas con saldo disponible menor o igual a 0 no deben avanzar a negociación.",
    "Notas con valor nominal mayor a 10000 requieren revisión humana reforzada por riesgo alto.",
    "Notas con valor nominal entre 5000 y 10000 se consideran de riesgo medio.",
    "Notas con documento de respaldo cargado reducen el riesgo operativo.",
    "Una coincidencia por número de título puede indicar duplicidad y debe revisarse manualmente.",
    "La liquidación, transferencia y endoso deben quedar como propuesta o solicitud de aprobación humana.",
    "El precio sugerido puede estimarse con base en riesgo, saldo disponible, valor nominal y contexto de negociación simulado."
]

antecedentes_simulados = [
    {
        "ruc": "0700000001",
        "titulo": "NCT-001",
        "titular": "Empresa Alfa",
        "tipoNota": "Reintegro tributario",
        "estado": "VALIDADO",
        "fuente": "Caso anterior simulado",
        "fecha": "2026-07-01"
    },
    {
        "ruc": "0700000002",
        "titulo": "NCT-002",
        "titular": "Empresa Beta",
        "tipoNota": "Crédito tributario",
        "estado": "OBSERVADO",
        "fuente": "Documento cargado",
        "fecha": "2026-07-03"
    },
    {
        "ruc": "0700000003",
        "titulo": "NCT-003",
        "titular": "Empresa Gamma",
        "tipoNota": "Nota SRI",
        "estado": "APROBADO",
        "fuente": "Base histórica simulada",
        "fecha": "2026-07-05"
    }
]

def recuperar_contexto(nota: Dict[str, Any]) -> List[str]:
    contexto = []
    for regla in base_conocimiento:
        if "saldo" in regla.lower() and nota.get("saldoDisponible", 0) <= 0:
            contexto.append(regla)
        elif "10000" in regla and nota.get("valorNominal", 0) > 10000:
            contexto.append(regla)
        elif "5000" in regla and 5000 < nota.get("valorNominal", 0) <= 10000:
            contexto.append(regla)
        elif "documento" in regla.lower() and nota.get("documentoCargado"):
            contexto.append(regla)
        elif "duplicidad" in regla.lower() and nota.get("duplicado"):
            contexto.append(regla)
        elif "liquidación" in regla.lower():
            contexto.append(regla)
        elif "precio sugerido" in regla.lower():
            contexto.append(regla)
    if not contexto:
        contexto = base_conocimiento[:3]
    return contexto

def buscar_antecedentes_ia(nota: Dict[str, Any]) -> Dict[str, Any]:
    coincidencias = []
    duplicado = False

    for ant in antecedentes_simulados:
        if nota.get("ruc") == ant["ruc"]:
            coincidencias.append({
                "tipoCoincidencia": "RUC",
                "fecha": ant["fecha"],
                "fuente": ant["fuente"],
                "estadoAnterior": ant["estado"],
                "datosSugeridos": {
                    "titular": ant["titular"],
                    "tipoNota": ant["tipoNota"]
                },
                "accionHumanaRequerida": "USAR / EDITAR / RECHAZAR"
            })
        if nota.get("numeroTitulo") == ant["titulo"]:
            duplicado = True
            coincidencias.append({
                "tipoCoincidencia": "TITULO_DUPLICADO",
                "fecha": ant["fecha"],
                "fuente": ant["fuente"],
                "estadoAnterior": ant["estado"],
                "evidencia": "Comparar número de título con expediente histórico",
                "accionHumanaRequerida": "REVISAR DUPLICIDAD"
            })

    contexto = recuperar_contexto({**nota, "duplicado": duplicado})
    return {
        "mensaje": "Búsqueda inteligente de antecedentes finalizada",
        "coincidencias": coincidencias,
        "duplicado": duplicado,
        "contextoUsado": contexto,
        "explicacionIA": "La IA comparó RUC y número de título contra antecedentes simulados y marcó duplicidad si encontró coincidencia exacta de título."
    }

def pendiente(prioridad: str, problema: str, evidencia: str, accion: str) -> Dict[str, str]:
    return {
        "prioridad": prioridad,
        "problema": problema,
        "evidencia": evidencia,
        "accionSugerida": accion
    }

def analizar_nota_ia(nota: Dict[str, Any]) -> Dict[str, Any]:
    pendientes = []
    factores = []
    puntaje = 0

    if not nota.get("titular"):
        pendientes.append(pendiente("ALTA", "Falta titular", "Documento del cliente o registro tributario", "Completar titular"))
        factores.append("Titular incompleto")
        puntaje += 20

    if not nota.get("ruc"):
        pendientes.append(pendiente("ALTA", "Falta RUC", "Identificación tributaria del titular", "Solicitar o corregir RUC"))
        factores.append("RUC faltante")
        puntaje += 20

    if not nota.get("numeroTitulo"):
        pendientes.append(pendiente("ALTA", "Falta número de título", "Título valor o nota emitida", "Registrar número de título"))
        factores.append("Número de título faltante")
        puntaje += 20

    if nota.get("valorNominal", 0) <= 0:
        pendientes.append(pendiente("ALTA", "Valor nominal inválido", "Documento de respaldo del valor nominal", "Corregir valor nominal"))
        factores.append("Valor nominal inválido")
        puntaje += 25

    if nota.get("saldoDisponible", 0) <= 0:
        pendientes.append(pendiente("ALTA", "Saldo no disponible", "Consulta de saldo o fuente simulada", "No continuar hasta verificar saldo"))
        factores.append("Saldo no disponible")
        puntaje += 35

    if not nota.get("documentoCargado"):
        pendientes.append(pendiente("ALTA", "Falta documento de respaldo", "PDF, imagen o comprobante de respaldo", "Solicitar documento al cliente"))
        factores.append("Documento faltante")
        puntaje += 30

    if nota.get("duplicado"):
        pendientes.append(pendiente("ALTA", "Posible duplicado detectado", "Historial de títulos y antecedente encontrado", "Validar manualmente antes de continuar"))
        factores.append("Posible duplicidad")
        puntaje += 35

    valor = nota.get("valorNominal", 0)
    if valor > 10000:
        factores.append("Valor nominal alto")
        puntaje += 20
    elif valor > 5000:
        factores.append("Valor nominal medio")
        puntaje += 10

    if puntaje >= 70:
        nivel = "ALTO"
        factor_precio = 0.60
        prioridadGeneral = "ALTA"
    elif puntaje >= 35:
        nivel = "MEDIO"
        factor_precio = 0.80
        prioridadGeneral = "MEDIA"
    else:
        nivel = "BAJO"
        prioridadGeneral = "BAJA"
        factor_precio = 0.90
        
    
    precio_sugerido = min(nota.get("valorNominal", 0), nota.get("saldoDisponible", 0)) * factor_precio
    contexto = recuperar_contexto({**nota, "duplicado": nota.get("duplicado", False)})

    if nota.get("saldoDisponible", 0) <= 0:
        estado = "RECHAZADO"
        validacion = "Nota inválida por saldo no disponible"
        decision = "NO CONTINUAR: corregir o cerrar expediente"
        siguiente = "Verificar saldo disponible antes de cualquier negociación"
    elif pendientes:
        estado = "OBSERVADO"
        validacion = "Nota observada por pendientes o riesgo"
        decision = "REQUIERE REVISIÓN HUMANA"
        siguiente = "Corregir pendientes y revisar evidencia"
    else:
        estado = "VALIDADO"
        validacion = "Nota válida para avanzar"
        decision = "PUEDE PREPARARSE FICHA DE NEGOCIACIÓN"
        siguiente = "Solicitar aprobación humana para preparar ficha"

    explicacion = (
        f"La IA evaluó saldo, valor nominal, documento, duplicidad y datos obligatorios. "
        f"El nivel de riesgo resultó {nivel} con puntaje {puntaje}. "
        f"La decisión queda como recomendación y requiere aprobación humana."
    )

    actualizacion = {
        "estadoNota": estado,
        "datosValidos": estado == "VALIDADO",
        "prioridadGeneral": prioridadGeneral,
        "pendientes": pendientes,
        "riesgo": {"nivel": nivel, "puntaje": puntaje, "factores": factores},
        "recomendacion": validacion,
        "siguienteAccion": siguiente,
        "precioSugerido": round(precio_sugerido, 2),
        "decisionIA": decision,
        "contextoIA": contexto
    }

    return {
        "titulo": "ANÁLISIS IA DE NOTA DE CRÉDITO TRIBUTARIA",
        "validacion": validacion,
        "riesgo": actualizacion["riesgo"],
        "precioSugerido": actualizacion["precioSugerido"],
        "decisionIA": decision,
        "pendientes": pendientes,
        "contextoUsado": contexto,
        "explicacionIA": explicacion,
        "actualizacionNota": actualizacion
    }

def generar_recomendacion(nota: Dict[str, Any]) -> Dict[str, Any]:
    if nota.get("estadoNota") == "VALIDADO":
        if nota.get("saldoDisponible", 0) >= nota.get("deudaCliente", 0):
            return {
                "recomendacion": "La nota puede cubrir la deuda total",
                "siguienteAccion": "Preparar ficha de negociación con aprobación humana"
            }
        return {
            "recomendacion": "La nota cubre parcialmente la deuda",
            "siguienteAccion": "Preparar propuesta de uso parcial o negociar diferencia"
        }
    if nota.get("estadoNota") == "OBSERVADO":
        return {
            "recomendacion": "Existen inconsistencias o pendientes",
            "siguienteAccion": "Revisar evidencias antes de continuar"
        }
    if nota.get("estadoNota") == "RECHAZADO":
        return {
            "recomendacion": "No se recomienda continuar",
            "siguienteAccion": "Cerrar o corregir expediente"
        }
    return {
        "recomendacion": "Revisar expediente y completar análisis IA",
        "siguienteAccion": "Ejecutar análisis IA"
    }

def generar_ficha_ia(nota: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "tituloFicha": f"Ficha de negociación simulada - {nota.get('numeroTitulo')}",
        "titular": nota.get("titular"),
        "ruc": nota.get("ruc"),
        "tipoNota": nota.get("tipoNota"),
        "valorNominal": nota.get("valorNominal"),
        "saldoDisponible": nota.get("saldoDisponible"),
        "deudaCliente": nota.get("deudaCliente"),
        "documento": nota.get("nombreDocumento"),
        "riesgoIA": nota.get("riesgo"),
        "precioSugeridoIA": nota.get("precioSugerido"),
        "recomendacionIA": nota.get("decisionIA"),
        "prioridadGeneral": nota.get("prioridadGeneral"),
        "advertencia": "Documento generado como propuesta. No ejecuta liquidación, transferencia ni endoso real.",
        "fechaGeneracion": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def responder_chat_ia(nota: Dict[str, Any], pregunta: str) -> str:
    p = pregunta.lower()

    if "falta" in p or "corregir" in p or "pendiente" in p:
        if not nota.get("pendientes"):
            return "No hay pendientes registrados. La nota puede avanzar según su estado actual."
        lista = []
        for x in nota.get("pendientes", []):
            lista.append(f"{x['prioridad']}: {x['problema']} | Evidencia: {x['evidencia']} | Acción: {x['accionSugerida']}")
        return "Pendientes detectados:\n" + "\n".join(lista)

    if "riesgo" in p:
        r = nota.get("riesgo", {})
        return f"El riesgo es {r.get('nivel')} con puntaje {r.get('puntaje')}. Factores: {', '.join(r.get('factores', []))}."

    if "precio" in p or "vender" in p or "venta" in p:
        return (
            f"Precio sugerido por IA: {nota.get('precioSugerido')}. "
            f"Decisión recomendada: {nota.get('decisionIA')}. "
            "Esto no ejecuta venta real; requiere aprobación humana."
        )

    if "negociar" in p or "negociación" in p:
        if nota.get("estadoNota") in ["VALIDADO", "LISTO_PARA_NEGOCIAR", "FICHA_APROBADA", "PUBLICADO"]:
            return "La nota puede avanzar hacia negociación simulada, siempre con aprobación humana y sin ejecutar acciones reguladas reales."
        return "Todavía no puede negociarse. Primero debe corregir pendientes, validar evidencia y aprobar la acción sugerida."

    if "observada" in p or "observado" in p:
        return f"La nota está en estado {nota.get('estadoNota')}. Recomendación: {nota.get('recomendacion')}. Siguiente acción: {nota.get('siguienteAccion')}."

    if "contexto" in p or "rag" in p or "base" in p:
        return "Contexto usado por IA:\n" + "\n".join(nota.get("contextoIA", recuperar_contexto(nota)))

    return (
        "Puedo ayudarte a explicar pendientes, riesgo, precio sugerido, contexto usado, "
        "estado actual, negociación y siguiente acción del expediente."
    )

def generar_dashboard(notas: List[Dict[str, Any]], mercado: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "totalNotas": len(notas),
        "prioridadAlta": sum(1 for n in notas if n.get("prioridadGeneral") == "ALTA"),
        "prioridadMedia": sum(1 for n in notas if n.get("prioridadGeneral") == "MEDIA"),
        "prioridadBaja": sum(1 for n in notas if n.get("prioridadGeneral") == "BAJA"),
        "borrador": sum(1 for n in notas if n.get("estadoNota") == "BORRADOR"),
        "validadas": sum(1 for n in notas if n.get("estadoNota") == "VALIDADO"),
        "observadas": sum(1 for n in notas if n.get("estadoNota") == "OBSERVADO"),
        "rechazadas": sum(1 for n in notas if n.get("estadoNota") == "RECHAZADO"),
        "publicadas": sum(1 for n in notas if n.get("estadoNota") == "PUBLICADO"),
        "cerradas": sum(1 for n in notas if n.get("estadoNota") == "CERRADO"),
        "riesgoAlto": sum(1 for n in notas if n.get("riesgo", {}).get("nivel") == "ALTO"),
        "riesgoMedio": sum(1 for n in notas if n.get("riesgo", {}).get("nivel") == "MEDIO"),
        "riesgoBajo": sum(1 for n in notas if n.get("riesgo", {}).get("nivel") == "BAJO"),
        "itemsMercado": len(mercado),
        "montoPublicado": round(sum(n.get("saldoDisponible", 0) for n in notas if n.get("estadoNota") == "PUBLICADO"), 2)
    }
