const API = "";
let sesion = null;

function mostrar(data) {
  document.getElementById("resultadoBox").classList.remove("hidden");
  document.getElementById("resultado").textContent = JSON.stringify(data, null, 2);
}

function abrirPaneles() {
  ["panelBox", "iaBox", "chatBox", "mercadoBox", "dashboardBox", "resultadoBox"].forEach(id => {
    document.getElementById(id).classList.remove("hidden");
  });
}

async function login() {
  const usuario = document.getElementById("usuario").value;
  const clave = document.getElementById("clave").value;
  try {
    const res = await fetch(`${API}/login`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({usuario, clave})
    });
    const data = await res.json();
    if (data.acceso) {
      sesion = data;
      document.getElementById("loginBox").classList.add("hidden");
      document.getElementById("usuarioActivo").textContent = data.usuario;
      document.getElementById("rolActivo").textContent = data.rol;
      abrirPaneles();
    } else {
      document.getElementById("loginMsg").textContent = data.detail || "Acceso denegado";
    }
    mostrar(data);
  } catch (e) {
    mostrar({error: "No se pudo conectar con el backend", detalle: String(e)});
  }
}

async function registrarNota() {
  const archivo = document.getElementById("documento").files[0];
  const datos = {
    usuario: sesion.usuario,
    rol: sesion.rol,
    titular: document.getElementById("titular").value,
    ruc: document.getElementById("ruc").value,
    numeroTitulo: document.getElementById("numeroTitulo").value,
    tipoNota: document.getElementById("tipoNota").value,
    valorNominal: parseFloat(document.getElementById("valorNominal").value || 0),
    saldoDisponible: parseFloat(document.getElementById("saldoDisponible").value || 0),
    deudaCliente: parseFloat(document.getElementById("deudaCliente").value || 0),
    documentoCargado: archivo ? true : false,
    nombreDocumento: archivo ? archivo.name : "Sin documento",
    tipoDocumento: archivo ? archivo.type : "No aplica",
    observacion: document.getElementById("observacion").value
  };
  const res = await fetch(`${API}/notas`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(datos)
  });
  mostrar(await res.json());
}

function idNota() { return document.getElementById("idNota").value; }

async function buscarAntecedentes() {
  const res = await fetch(`${API}/notas/${idNota()}/antecedentes`);
  mostrar(await res.json());
}

async function analizarIA() {
  const res = await fetch(`${API}/notas/${idNota()}/analizar-ia`, {method: "POST"});
  mostrar(await res.json());
}

async function aprobarAccion() {
  const decision = prompt("¿Aprueba la recomendación IA? SI / NO / EDITAR", "SI");
  const observacion = decision && decision.toUpperCase() === "EDITAR" ? prompt("Nueva observación:") : "";
  const res = await fetch(`${API}/notas/${idNota()}/aprobar`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({usuario: sesion.usuario, decision, observacion})
  });
  mostrar(await res.json());
}

async function generarFicha() {
  const decision = prompt("¿Aprobar ficha IA para publicación simulada? SI / NO", "SI");
  const res = await fetch(`${API}/notas/${idNota()}/ficha`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({usuario: sesion.usuario, decision})
  });
  mostrar(await res.json());
}

async function consultarExpediente() {
  const res = await fetch(`${API}/notas/${idNota()}/expediente`);
  mostrar(await res.json());
}

async function preguntarAgente() {
  const pregunta = document.getElementById("preguntaAgente").value;
  const res = await fetch(`${API}/notas/${idNota()}/chat`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({pregunta})
  });
  mostrar(await res.json());
}

async function publicarMercado() {
  const res = await fetch(`${API}/mercado/publicar`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      usuario: sesion.usuario,
      idNota: parseInt(idNota()),
      precioVenta: parseFloat(document.getElementById("precioVenta").value || 0)
    })
  });
  mostrar(await res.json());
}

async function verMercado() {
  const res = await fetch(`${API}/mercado`);
  mostrar(await res.json());
}

async function solicitarCompra() {
  const idMercado = prompt("Ingrese ID de mercado:");
  const res = await fetch(`${API}/mercado/${idMercado}/solicitar-compra`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({usuario: sesion.usuario})
  });
  mostrar(await res.json());
}

async function avanzarNegociacion() {
  const idMercado = prompt("Ingrese ID de mercado:");
  const res = await fetch(`${API}/mercado/${idMercado}/avanzar`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({usuario: sesion.usuario, rol: sesion.rol})
  });
  mostrar(await res.json());
}

async function cerrarNegociacion() {
  const idMercado = prompt("Ingrese ID de mercado:");
  const decision = prompt("¿Cerrar negociación simulada? SI / NO", "SI");
  const res = await fetch(`${API}/mercado/${idMercado}/cerrar`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({usuario: sesion.usuario, decision})
  });
  mostrar(await res.json());
}

async function verDashboard() {
  const res = await fetch(`${API}/dashboard`);
  const data = await res.json();
  mostrar(data);
  const dash = document.getElementById("dashboard");
  dash.innerHTML = "";
  Object.entries(data).forEach(([k, v]) => {
    dash.innerHTML += `<div class="metric"><b>${v}</b><span>${k}</span></div>`;
  });
}
