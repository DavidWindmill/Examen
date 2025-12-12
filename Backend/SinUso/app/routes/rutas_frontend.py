import os
import httpx
import services.evento as EventoService
import services.calendario as CalendarioService
import services.comentario as ComentarioService 
import services.imagenes as ImagenesService
from fastapi import APIRouter, HTTPException, Query, Body
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from datetime import date, datetime
import calendar
router = APIRouter(tags=["Frontend"])

templates = Jinja2Templates(directory="templates")

# ------------------------------------------------------- #
#                   Rutas del Frontend                    #
# ------------------------------------------------------- #


@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):

    hoy = date.today()

    mes = int(request.query_params.get("m", hoy.month))
    anyo = int(request.query_params.get("y", hoy.year))

    # Nombres en español
    nombre_meses = [
        "Enero","Febrero","Marzo","Abril","Mayo","Junio",
        "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"
    ]
    mes_actual = f"{nombre_meses[mes-1]} {anyo}"

    # Navegación
    if mes == 1:
        mes_anterior, anyo_anterior = 12, anyo - 1
    else:
        mes_anterior, anyo_anterior = mes - 1, anyo

    if mes == 12:
        mes_siguiente, anyo_siguiente = 1, anyo + 1
    else:
        mes_siguiente, anyo_siguiente = mes + 1, anyo

    # Leer calendarios seleccionados
    cals_param = request.query_params.get("cals", "")
    def _valid_oid(oid: str) -> bool:
        return len(oid) == 24 and all(ch in "0123456789abcdefABCDEF" for ch in oid)
    calendarios_seleccionados = [c for c in cals_param.split(",") if c and _valid_oid(c)]

    # Para URLs de navegación
    def build_url(m, y):
        return f"/?m={m}&y={y}&cals={','.join(calendarios_seleccionados)}"

    lista_calendarios = await CalendarioService.get_calendarios()

    # Obtener eventos del backend
    eventos_raw = []
    if calendarios_seleccionados:
        fecha_inicio = f"01-{mes:02d}-{anyo}"
        for cal_id in calendarios_seleccionados:
            evs = await EventoService.get_eventos_por_calendario_y_mes(cal_id, fecha_inicio)
            if evs:
                eventos_raw.extend(evs)

    # 🌟 AQUÍ USAMOS EL NUEVO MOTOR
    data = await build_calendar(anyo, mes, eventos_raw)

    return templates.TemplateResponse("main.html", {
        "request": request,
        "lista_calendarios": lista_calendarios,
        "calendarios_seleccionados": calendarios_seleccionados,
        "mes_actual": mes_actual,
        "mes_matriz": data["mes_matriz"],
        "dias_semana": ["Lun","Mar","Mié","Jue","Vie","Sáb","Dom"],
        "hoy": hoy.day if hoy.month == mes and hoy.year == anyo else None,
        "url_mes_anterior": build_url(mes_anterior, anyo_anterior),
        "url_mes_siguiente": build_url(mes_siguiente, anyo_siguiente),
        "evento_barras": data["evento_barras"],
        "max_levels_per_week": data["max_levels_per_week"],
        "mes": mes,
        "anyo": anyo,
        "mostrar_selector": True,
    })
  



@router.get("/calendarios", response_class=HTMLResponse)
async def home(request: Request, q: str = Query(None)):
    """Página principal - listado de calendarios + vista del mes actual con eventos"""
    now = datetime.now()

    # ---------------- Obtener calendarios ----------------
    if q:
        calendarios = await CalendarioService.buscar_calendarios(q)
        is_searching = True
    else:
        calendarios = await  CalendarioService.get_calendarios()
        is_searching = False

    # Obtener eventos del backend
    eventos_raw = []
    if calendarios:
        fecha_inicio = f"01-{now.month:02d}-{now.year}"
        for cal_id in calendarios:
            evs = await EventoService.get_eventos_por_calendario_y_mes(cal_id["_id"], fecha_inicio)
            if evs:
                eventos_raw.extend(evs)

    # ---------------- Construir el calendario ----------------
    calendario = await build_calendar(now.year, now.month, eventos_raw)

    # ---------------- Mes en español ----------------
    meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
             'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

    # Propietario: true por ahora
    is_owner = True

    return templates.TemplateResponse("calendarios.html", {
        "request": request,
        "calendarios": calendarios,
        "is_searching": is_searching,
        "search_query": q or "",
        "is_owner": is_owner,
        
        # Datos del calendario avanzado
        "mes_matriz": calendario["mes_matriz"],
        "evento_barras": calendario["evento_barras"],
        "max_levels_per_week": calendario["max_levels_per_week"],

        # Mes / año actual
        "current_month": meses[now.month - 1],
        "current_year": now.year,
    })

@router.get("/calendario/{calendario_id}", response_class=HTMLResponse)
async def calendar_detail(
    request: Request,
    calendario_id: str,
    q: str = Query(None),
    year: int = Query(None),
    month: int = Query(None)
):
    try:
        # Obtener datos del calendario
        async with httpx.AsyncClient() as client:
            cal_response = await client.get(
                f"{os.getenv('CALENDARIO_SERVICE_URL', 'http://localhost:8002')}/api/v1/calendarios/{calendario_id}"
            )
            cal_response.raise_for_status()
            calendario = cal_response.json()

        # Fecha actual o pasada por query
        now = datetime.now()
        display_year = year if year else now.year
        display_month = month if month else now.month

        # Obtener eventos del microservicio de eventos
        eventos_raw = await EventoService.get_eventos_por_calendario(calendario_id)

        # Construir calendario avanzado (matriz + barras + niveles)
        calendario_completo = await build_calendar(display_year, display_month, eventos_raw)

        # Nombres de meses y días
        meses = [
            'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
            'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
        ]
        dias_semana = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]

        # Navegación de meses
        prev_month = 12 if display_month == 1 else display_month - 1
        prev_year = display_year - 1 if display_month == 1 else display_year
        next_month = 1 if display_month == 12 else display_month + 1
        next_year = display_year + 1 if display_month == 12 else display_year

        url_mes_anterior = f"/calendario/{calendario_id}?year={prev_year}&month={prev_month}"
        url_mes_siguiente = f"/calendario/{calendario_id}?year={next_year}&month={next_month}"

        back_url = "/calendarios" 

        return templates.TemplateResponse("detail.html", {
            "request": request,
            "calendario": calendario,
            "is_owner": True,
            "calendario_id": calendario_id,

            # Variables para el bloque de calendario
            "mes_actual":  f"{meses[display_month - 1]} {display_year}",
            "dias_semana": dias_semana,
            "mes_matriz": calendario_completo["mes_matriz"],
            "evento_barras": calendario_completo["evento_barras"],
            "url_mes_anterior": url_mes_anterior,
            "url_mes_siguiente": url_mes_siguiente,
            "mes": display_month,
            "anyo": now.year,

            #Crear Evento
            "mostrar_selector": False,


            # Otros datos de la página
            "back_url": back_url,
            "search_query": q or "",
        })

    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Calendario no encontrado: {str(e)}")

@router.get("/evento/{evento_id}", response_class=HTMLResponse)
async def evento(request: Request, evento_id: str, q: str = Query(None)):

    # Obtener el objeto evento mediante su id
    evento = await EventoService.get_evento_id(evento_id)

    # Obtiene los comentarios de ese evento en concreto
    comentarios = await ComentarioService.get_comentarios_evento(evento_id)
    
    return templates.TemplateResponse("evento.html", {
            "request": request,
            "evento": evento,
            "comentarios": comentarios
            
        })

# actualizar evento desde el frontend
@router.put("/evento/{evento_id}")
async def actualizar_evento_frontend(evento_id: str, data: dict = Body(...)):
    return await EventoService.actualizarEvento(evento_id, data)

@router.delete("/evento/{evento_id}")
async def eliminar_evento_frontend(evento_id: str):
    return await EventoService.deleteEvento(evento_id)


@router.get("/busquedas", response_class=HTMLResponse)
async def vista_busquedas(request: Request):
    """
    Renderiza la página de búsquedas
    (carga la lista de calendarios desde el microservicio de calendarios)
    """

    calendarios = await CalendarioService.get_calendarios()

    return templates.TemplateResponse(
        "busquedas.html",
        {
            "request": request,
            "calendarios": calendarios   # 👈 Se usa en el <select multiple>
        }
    )





# ------------------------------------------------------- #
#                   Métodos Adicionales                   #
# ------------------------------------------------------- #

async def build_calendar(anyo: int, mes: int, eventos_raw: list):
    """
    Construye un calendario COMPLETO con:
    - matriz del mes
    - eventos divididos en semanas
    - stacking
    """

    # -------- MATRIZ DEL MES ----------
    cal = calendar.Calendar(firstweekday=0)
    mes_matriz = cal.monthdayscalendar(anyo, mes)

    # -------- Normalización de eventos ----------
    eventos_normalizados = []
    _, ultimo_dia = calendar.monthrange(anyo, mes)
    inicio_mes = date(anyo, mes, 1)
    fin_mes = date(anyo, mes, ultimo_dia)

    for ev in eventos_raw:
        try:
            inicio_dt = datetime.fromisoformat(ev["hora_comienzo"])
            fin_dt = datetime.fromisoformat(ev["hora_fin"])
        except Exception:
            continue

        if inicio_dt.date() <= fin_mes and fin_dt.date() >= inicio_mes:
            dia_ini = max(inicio_dt.date(), inicio_mes).day
            dia_fin = min(fin_dt.date(), fin_mes).day

            eventos_normalizados.append({
                "titulo": ev.get("titulo", "Sin título"),
                "raw": ev,
                "inicio": dia_ini,
                "fin": dia_fin,
                "id": ev.get("_id")
            })

    # -------- Segmentación por semanas ----------
    semanas = len(mes_matriz)
    eventos_segments = []

    def locate(day):
        for w, semana in enumerate(mes_matriz):
            if day in semana:
                return w, semana.index(day)
        return None, None

    for ev in eventos_normalizados:
        dia_ini = ev["inicio"]
        dia_fin = ev["fin"]

        w_ini, col_ini = locate(dia_ini)
        w_fin, col_fin = locate(dia_fin)
        if w_ini is None: continue

        if w_ini == w_fin:
            # mismo fragmento
            eventos_segments.append({
                "semana": w_ini,
                "start_col": col_ini,
                "span": col_fin - col_ini + 1,
                "titulo": ev["titulo"],
                "inicio_dia": dia_ini,
                "fin_dia": dia_fin,
                "raw": ev["raw"],
                "id": ev["id"]
            })
        else:
            # primera semana
            eventos_segments.append({
                "semana": w_ini,
                "start_col": col_ini,
                "span": 7 - col_ini,
                "titulo": ev["titulo"],
                "inicio_dia": dia_ini,
                "fin_dia": mes_matriz[w_ini][-1],
                "raw": ev["raw"],
                "id": ev["id"]
            })
            # semanas intermedias
            for w in range(w_ini + 1, w_fin):
                eventos_segments.append({
                    "semana": w,
                    "start_col": 0,
                    "span": 7,
                    "titulo": ev["titulo"],
                    "inicio_dia": mes_matriz[w][0],
                    "fin_dia": mes_matriz[w][-1],
                    "raw": ev["raw"],
                    "id": ev["id"]
                })
            # última semana
            eventos_segments.append({
                "semana": w_fin,
                "start_col": 0,
                "span": col_fin + 1,
                "titulo": ev["titulo"],
                "inicio_dia": mes_matriz[w_fin][0],
                "fin_dia": dia_fin,
                "raw": ev["raw"],
                "id": ev["id"]
            })

    # -------- Stacking ----------
    max_levels_per_week = [0] * semanas
    occupied = {w: [] for w in range(semanas)}

    eventos_sorted = sorted(eventos_segments, key=lambda s: (s["semana"], s["start_col"], -s["span"]))

    for seg in eventos_sorted:
        w = seg["semana"]
        cols = set(range(seg["start_col"], seg["start_col"] + seg["span"]))

        placed = False
        for lvl_idx, occ in enumerate(occupied[w]):
            if occ.isdisjoint(cols):
                occ.update(cols)
                seg["level"] = lvl_idx
                placed = True
                break

        if not placed:
            occupied[w].append(set(cols))
            seg["level"] = len(occupied[w]) - 1

        max_levels_per_week[w] = max(max_levels_per_week[w], seg["level"] + 1)

    return {
        "mes_matriz": mes_matriz,
        "evento_barras": eventos_sorted,
        "max_levels_per_week": max_levels_per_week
    }
