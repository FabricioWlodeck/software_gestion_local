# Bot de Telegram de Punto Lácteo (solo para la dueña).
#
# - Avisa lo que el backend deja en la tabla `notificacion`: stock bajo, ventas observadas,
#   mermas, ajustes y cajas cerradas con diferencia (ver docs/decisiones/0004).
# - Responde consultas de stock y de ventas, y dibuja un gráfico de ventas por día.
# - Manda un resumen los lunes (semana anterior) y el día 1 (mes anterior), a las 8:00.
# - Solo LEE la base, con un usuario que tiene permiso de SELECT.
#
# Sigue la forma del bot de la materia IoT: un solo archivo, python-telegram-bot (async),
# aiomysql con una conexión por consulta y matplotlib para los gráficos.
# Diferencia importante: todas las consultas usan parámetros (%s), nunca texto del usuario
# pegado en el SQL.
#
# Modo de prueba sin Telegram (imprime o guarda lo mismo que mandaría el bot):
#   python telegrambot.py --probar ventas-hoy | ventas-semana | ventas-mes
#   python telegrambot.py --probar resumen-semana | resumen-mes   [AAAA-MM-DD como "hoy"]
#   python telegrambot.py --probar stock-bajo | stock <texto> | notificaciones | autorizados
#   python telegrambot.py --probar grafico <archivo.png>

from telegram import Update, ReplyKeyboardMarkup, BotCommand
from telegram.constants import ParseMode
from telegram.error import BadRequest, Forbidden, TelegramError
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import logging, os, sys, re, json, html, signal, time, asyncio, aiomysql
from datetime import date, datetime, timedelta, time as hora
from decimal import Decimal, ROUND_HALF_UP
from io import BytesIO
from zoneinfo import ZoneInfo
import matplotlib
matplotlib.use("Agg")  # sin pantalla: matplotlib dibuja directo a un PNG
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


# ============================================================================
# Configuración
# ============================================================================

token = os.environ.get("TB_TOKEN", "").strip()

ZONA = ZoneInfo("America/Argentina/Buenos_Aires")
DIR_DATOS = os.environ.get("TB_DIR_DATOS", "/app/datos")   # volumen datos_bot en Docker
ARCHIVO_ESTADO = os.path.join(DIR_DATOS, "estado.json")

INTERVALO_NOTIFICACIONES = 30    # segundos entre cada lectura de la tabla notificacion
INTERVALO_AUTORIZADOS = 300      # segundos entre cada recarga de las dueñas autorizadas
MARGEN_NOTIFICACIONES = 5        # segundos de espera antes de leer un aviso (ver consultar_notificaciones_nuevas)
HORA_RESUMENES = hora(8, 0, tzinfo=ZONA)
LUNES = 1                        # en python-telegram-bot v20+ los días van de 0 (domingo) a 6 (sábado)
DIAS_GRAFICO = 14
MAX_PRODUCTOS_BUSQUEDA = 15
LIMITE_MENSAJE = 4000            # Telegram acepta hasta 4096 caracteres por mensaje

TECLADO = [["stock bajo", "ventas hoy"], ["ventas semana", "ventas mes"], ["gráfico ventas"]]

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
DIAS_SEMANA = ["lu", "ma", "mi", "ju", "vi", "sá", "do"]
MEDIOS_PAGO = {"efectivo": "💵 Efectivo", "transferencia": "🏦 Transferencia"}
MENOS = "−"  # signo menos tipográfico, como en los mensajes del backend

logging.basicConfig(format='%(asctime)s - TelegramBot - %(levelname)s - %(message)s', level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

# Filtro con los telegram_id de las dueñas. Es UNA instancia que se reutiliza: al recargar se le
# agregan o quitan ids, y los handlers que la usan ven el cambio sin volver a registrarse.
# Vacío no deja pasar a nadie (allow_empty=False).
autorizados = filters.User(allow_empty=False)

# Último aviso de la tabla notificacion que ya se mandó (se guarda en ARCHIVO_ESTADO).
estado = {"ultimo_id": None}


# ============================================================================
# Formato (dinero, cantidades y fechas al estilo argentino)
# ============================================================================

h = html.escape  # los nombres de productos y sucursales se escapan antes de ir en HTML


def _con_miles(valor, decimales):
    """1234.5 → '1.234,50': punto para los miles y coma decimal, sin depender del locale."""
    texto = f"{abs(Decimal(valor)):,.{decimales}f}"          # '1,234.50'
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def formatear_dinero(valor):
    valor = Decimal(valor or 0).quantize(Decimal("0.01"), ROUND_HALF_UP)
    signo = MENOS if valor < 0 else ""
    return f"{signo}$ {_con_miles(valor, 2)}"


def formatear_cantidad(cantidad, unidad):
    """'0,350 kg' para los productos por peso y '2 u.' para los que se venden por unidad."""
    cantidad = Decimal(cantidad or 0)
    signo = MENOS if cantidad < 0 else ""
    if unidad == "kg":
        return f"{signo}{_con_miles(cantidad.quantize(Decimal('0.001'), ROUND_HALF_UP), 3)} kg"
    if cantidad == cantidad.to_integral_value():
        return f"{signo}{_con_miles(cantidad, 0)} u."
    return f"{signo}{_con_miles(cantidad, 3)} u."


def formatear_fecha(valor):
    return valor.strftime("%d/%m/%Y")


def formatear_fecha_hora(valor):
    return valor.strftime("%d/%m/%Y %H:%M")


def plural(n, singular, plural_):
    return f"{n} {singular if n == 1 else plural_}"


def partir_mensaje(texto, limite=LIMITE_MENSAJE):
    """Corta un texto largo en partes de menos de `limite` caracteres, siempre entre líneas
    (así no se parte una etiqueta HTML)."""
    partes, lineas, largo = [], [], 0
    for linea in texto.split("\n"):
        if lineas and largo + len(linea) + 1 > limite:
            partes.append("\n".join(lineas))
            lineas, largo = [], 0
        lineas.append(linea)
        largo += len(linea) + 1
    if lineas:
        partes.append("\n".join(lineas))
    return partes


def a_texto_plano(texto):
    """Para el modo --probar: saca las etiquetas HTML que entiende Telegram."""
    return html.unescape(re.sub(r"</?(b|i|code)>", "", texto))


# ============================================================================
# Períodos (fechas inclusivas, como en el contrato)
# ============================================================================

def hoy():
    # Se usa la zona explícita para no depender de la zona horaria del sistema
    return datetime.now(ZONA).date()


def periodo(nombre, referencia=None):
    """Devuelve (desde, hasta), las dos fechas inclusivas."""
    dia = referencia or hoy()
    if nombre == "hoy":
        return dia, dia
    if nombre == "semana":                    # de este lunes a hoy
        return dia - timedelta(days=dia.weekday()), dia
    if nombre == "mes":                       # del 1 a hoy
        return dia.replace(day=1), dia
    if nombre == "semana_anterior":           # de lunes a domingo de la semana pasada
        lunes = dia - timedelta(days=dia.weekday() + 7)
        return lunes, lunes + timedelta(days=6)
    if nombre == "mes_anterior":              # el mes pasado completo
        ultimo = dia.replace(day=1) - timedelta(days=1)
        return ultimo.replace(day=1), ultimo
    raise ValueError(f"Período desconocido: {nombre}")


def rango_sql(desde, hasta):
    """Pasa fechas inclusivas a [desde 00:00, día siguiente a hasta 00:00), que compara bien con
    DATETIME y aprovecha el índice (sucursal_id, fecha)."""
    return datetime.combine(desde, hora.min), datetime.combine(hasta + timedelta(days=1), hora.min)


def texto_periodo(desde, hasta):
    if desde == hasta:
        return formatear_fecha(desde)
    return f"del {formatear_fecha(desde)} al {formatear_fecha(hasta)}"


# ============================================================================
# Base de datos (solo lectura)
# ============================================================================

async def consultar(sql, parametros=None):
    """Abre una conexión, ejecuta la consulta y devuelve todas las filas.
    Como en la materia, una conexión por consulta: así cada consulta ve los datos recién
    confirmados por el backend."""
    conn = await aiomysql.connect(host=os.environ["MARIADB_SERVER"],
                                  port=int(os.environ.get("MARIADB_PORT", "3306")),
                                  user=os.environ["MARIADB_USER"],
                                  password=os.environ["MARIADB_USER_PASS"],
                                  db=os.environ["MARIADB_DB"],
                                  charset="utf8mb4")
    try:
        async with conn.cursor() as cur:
            await cur.execute(sql, parametros)
            return await cur.fetchall()
    finally:
        conn.close()


async def consultar_autorizados():
    filas = await consultar("""
        SELECT telegram_id FROM usuario
        WHERE rol = 'duenio' AND activo = 1 AND telegram_id IS NOT NULL""")
    return {int(fila[0]) for fila in filas}


async def consultar_stock_bajo():
    return await consultar("""
        SELECT s.nombre, p.nombre, p.unidad, st.cantidad, st.minimo
        FROM stock st
        JOIN producto p ON p.id = st.producto_id
        JOIN sucursal s ON s.id = st.sucursal_id
        WHERE p.activo = 1 AND s.activa = 1 AND st.cantidad < st.minimo
        ORDER BY s.id, p.nombre""")


def escapar_like(texto):
    """Para que un % o un _ escritos por el usuario se busquen como letras y no como comodines."""
    return texto.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


async def consultar_stock_producto(texto):
    return await consultar("""
        SELECT p.id, p.nombre, p.unidad, s.nombre, st.cantidad, st.minimo
        FROM producto p
        JOIN stock st ON st.producto_id = p.id
        JOIN sucursal s ON s.id = st.sucursal_id
        WHERE p.activo = 1 AND s.activa = 1 AND p.nombre LIKE %s
        ORDER BY p.nombre, s.id""", ("%" + escapar_like(texto) + "%",))


async def consultar_ventas(desde, hasta):
    """Totales de las ventas 'valida' del período por sucursal y medio de pago, y los 5 productos
    que más facturaron."""
    inicio, fin = rango_sql(desde, hasta)
    sucursales = await consultar("SELECT id, nombre FROM sucursal WHERE activa = 1 ORDER BY id")
    totales = await consultar("""
        SELECT s.id, s.nombre, v.medio_pago, COUNT(*), SUM(v.total)
        FROM venta v
        JOIN sucursal s ON s.id = v.sucursal_id
        WHERE v.estado = 'valida' AND v.fecha >= %s AND v.fecha < %s
        GROUP BY s.id, s.nombre, v.medio_pago
        ORDER BY s.id""", (inicio, fin))
    top = await consultar("""
        SELECT p.nombre, p.unidad, SUM(d.cantidad), SUM(d.subtotal)
        FROM venta_detalle d
        JOIN venta v ON v.id = d.venta_id
        JOIN producto p ON p.id = d.producto_id
        WHERE v.estado = 'valida' AND v.fecha >= %s AND v.fecha < %s
        GROUP BY p.id, p.nombre, p.unidad
        ORDER BY SUM(d.subtotal) DESC, p.nombre
        LIMIT 5""", (inicio, fin))

    # Todas las sucursales activas aparecen, aunque no hayan vendido
    por_sucursal = {id_: {"nombre": nombre, "total": Decimal(0), "cantidad": 0, "por_medio": {}}
                    for id_, nombre in sucursales}
    por_medio = {}
    for id_, nombre, medio, cantidad, total in totales:
        suc = por_sucursal.setdefault(id_, {"nombre": nombre, "total": Decimal(0), "cantidad": 0, "por_medio": {}})
        suc["total"] += total
        suc["cantidad"] += cantidad
        suc["por_medio"][medio] = total
        por_medio[medio] = por_medio.get(medio, Decimal(0)) + total
    return {
        "desde": desde, "hasta": hasta,
        "sucursales": list(por_sucursal.values()),
        "por_medio": por_medio,
        "total": sum((s["total"] for s in por_sucursal.values()), Decimal(0)),
        "cantidad": sum(s["cantidad"] for s in por_sucursal.values()),
        "top": top,
    }


async def consultar_resumen(desde, hasta):
    """Lo de consultar_ventas más lo que la dueña revisa una vez por semana o por mes."""
    datos = await consultar_ventas(desde, hasta)
    inicio, fin = rango_sql(desde, hasta)
    estados = await consultar("""
        SELECT estado, COUNT(*) FROM venta
        WHERE estado IN ('observada', 'anulada') AND fecha >= %s AND fecha < %s
        GROUP BY estado""", (inicio, fin))
    conteo = dict(estados)
    datos["observadas"] = conteo.get("observada", 0)
    datos["anuladas"] = conteo.get("anulada", 0)
    # La carga inicial de stock también es un 'ajuste' (contrato: motivo «Stock inicial»), pero no
    # es una corrección: se deja afuera para que no tape las mermas y los ajustes de verdad
    datos["mermas_ajustes"] = await consultar("""
        SELECT m.tipo, p.nombre, p.unidad, s.nombre, COUNT(*), SUM(m.cantidad)
        FROM movimiento_stock m
        JOIN producto p ON p.id = m.producto_id
        JOIN sucursal s ON s.id = m.sucursal_id
        WHERE m.tipo IN ('merma', 'ajuste') AND m.fecha >= %s AND m.fecha < %s
          AND NOT (m.tipo = 'ajuste' AND m.motivo = 'Stock inicial')
        GROUP BY m.tipo, p.id, p.nombre, p.unidad, s.id, s.nombre
        ORDER BY m.tipo DESC, p.nombre, s.id""", (inicio, fin))
    datos["diferencias_caja"] = await consultar("""
        SELECT c.id, s.nombre, c.cerrada_en, c.efectivo_esperado, c.efectivo_contado, c.diferencia
        FROM caja c
        JOIN sucursal s ON s.id = c.sucursal_id
        WHERE c.estado = 'cerrada' AND c.diferencia <> 0
          AND c.cerrada_en >= %s AND c.cerrada_en < %s
        ORDER BY c.cerrada_en""", (inicio, fin))
    return datos


async def consultar_ventas_diarias(desde, hasta):
    """Total de ventas 'valida' por día y sucursal. Devuelve (días, [(sucursal, [total por día])])."""
    inicio, fin = rango_sql(desde, hasta)
    filas = await consultar("""
        SELECT DATE(v.fecha), v.sucursal_id, SUM(v.total)
        FROM venta v
        WHERE v.estado = 'valida' AND v.fecha >= %s AND v.fecha < %s
        GROUP BY DATE(v.fecha), v.sucursal_id""", (inicio, fin))
    sucursales = await consultar("SELECT id, nombre, activa FROM sucursal ORDER BY id")
    con_ventas = {fila[1] for fila in filas}
    dias = [desde + timedelta(days=i) for i in range((hasta - desde).days + 1)]
    totales = {(dia, suc_id): total for dia, suc_id, total in filas}
    series = [(nombre, [totales.get((dia, id_), Decimal(0)) for dia in dias])
              for id_, nombre, activa in sucursales if activa or id_ in con_ventas]
    return dias, series


async def consultar_max_notificacion():
    filas = await consultar("SELECT COALESCE(MAX(id), 0) FROM notificacion")
    return int(filas[0][0])


async def consultar_notificaciones_nuevas(ultimo_id, limite=50):
    """Avisos posteriores a `ultimo_id`, del más viejo al más nuevo.
    Solo se leen los que tienen al menos MARGEN_NOTIFICACIONES segundos: si dos transacciones del
    backend insertan avisos a la vez y la del id más alto confirma primero, el margen evita
    avanzar ultimo_id por encima del otro aviso, que todavía no se ve, y perderlo."""
    return await consultar("""
        SELECT id, tipo, mensaje FROM notificacion
        WHERE id > %s AND creada_en <= NOW() - INTERVAL %s SECOND
        ORDER BY id
        LIMIT %s""", (ultimo_id, MARGEN_NOTIFICACIONES, limite))


async def consultar_ultimas_notificaciones(cantidad=5):
    filas = await consultar("""
        SELECT id, tipo, mensaje FROM notificacion ORDER BY id DESC LIMIT %s""", (cantidad,))
    return list(reversed(filas))


# ============================================================================
# Textos que manda el bot (HTML de Telegram: solo <b>, <i> y <code>)
# ============================================================================

def texto_stock_bajo(filas):
    if not filas:
        return "✅ <b>Stock bajo</b>\n\nNingún producto está por debajo del mínimo. 👌"
    lineas = ["⚠️ <b>Productos por debajo del mínimo</b>"]
    sucursal_actual = None
    for sucursal, producto, unidad, cantidad, minimo in filas:
        if sucursal != sucursal_actual:
            lineas += ["", f"🏪 <b>{h(sucursal)}</b>"]
            sucursal_actual = sucursal
        lineas.append(f"• {h(producto)}: {formatear_cantidad(cantidad, unidad)} "
                      f"(mínimo {formatear_cantidad(minimo, unidad)})")
    return "\n".join(lineas)


def texto_stock_producto(buscado, filas):
    if not filas:
        return f"🔎 No encontré productos activos que contengan «{h(buscado)}»."
    productos = {}  # id → (nombre, unidad, [(sucursal, cantidad, mínimo)]), en el orden de la consulta
    for id_, nombre, unidad, sucursal, cantidad, minimo in filas:
        productos.setdefault(id_, (nombre, unidad, []))[2].append((sucursal, cantidad, minimo))
    lineas = [f"🔎 <b>Stock de «{h(buscado)}»</b>"]
    for nombre, unidad, por_sucursal in list(productos.values())[:MAX_PRODUCTOS_BUSQUEDA]:
        lineas += ["", f"📦 <b>{h(nombre)}</b>"]
        for sucursal, cantidad, minimo in por_sucursal:
            alerta = " ⚠️" if cantidad < minimo else ""
            lineas.append(f"   {h(sucursal)}: {formatear_cantidad(cantidad, unidad)} "
                          f"(mínimo {formatear_cantidad(minimo, unidad)}){alerta}")
    sobran = len(productos) - MAX_PRODUCTOS_BUSQUEDA
    if sobran > 0:
        lineas += ["", f"… y {plural(sobran, 'producto más', 'productos más')}: afiná la búsqueda."]
    return "\n".join(lineas)


def texto_medios(por_medio):
    medios = list(MEDIOS_PAGO) + [m for m in por_medio if m not in MEDIOS_PAGO]
    return " · ".join(f"{MEDIOS_PAGO.get(m, h(m))}: {formatear_dinero(por_medio.get(m, 0))}" for m in medios)


def lineas_ventas(datos):
    """El bloque de ventas que comparten las consultas y los resúmenes."""
    if datos["cantidad"] == 0:
        return ["Sin ventas en el período."]
    lineas = []
    for suc in datos["sucursales"]:
        if suc["cantidad"] == 0:
            lineas.append(f"🏪 <b>{h(suc['nombre'])}</b>: sin ventas")
            continue
        lineas.append(f"🏪 <b>{h(suc['nombre'])}</b>: {formatear_dinero(suc['total'])} "
                      f"({plural(suc['cantidad'], 'venta', 'ventas')})")
        lineas.append(f"      {texto_medios(suc['por_medio'])}")
    lineas += ["",
               f"💰 <b>Total: {formatear_dinero(datos['total'])}</b> en {plural(datos['cantidad'], 'venta', 'ventas')}",
               f"      {texto_medios(datos['por_medio'])}",
               "",
               "🏆 <b>Más vendidos</b>"]
    for i, (nombre, unidad, cantidad, total) in enumerate(datos["top"], 1):
        lineas.append(f"{i}. {h(nombre)}: {formatear_cantidad(cantidad, unidad)} · {formatear_dinero(total)}")
    return lineas


def texto_ventas(cual, datos):
    desde, hasta = datos["desde"], datos["hasta"]
    if cual == "hoy":
        titulo = f"📈 <b>Ventas de hoy</b> ({formatear_fecha(hasta)})"
    elif cual == "semana":
        titulo = f"📈 <b>Ventas de esta semana</b>\n{texto_periodo(desde, hasta)}"
    else:
        titulo = f"📈 <b>Ventas de {MESES[desde.month - 1]} {desde.year}</b>\n{texto_periodo(desde, hasta)}"
    return "\n".join([titulo, ""] + lineas_ventas(datos))


def texto_resumen(cual, datos):
    desde, hasta = datos["desde"], datos["hasta"]
    if cual == "semana":
        titulo = f"🗓️ <b>Resumen semanal</b>\n{texto_periodo(desde, hasta)}"
    else:
        titulo = f"🗓️ <b>Resumen de {MESES[desde.month - 1]} {desde.year}</b>\n{texto_periodo(desde, hasta)}"
    lineas = [titulo, ""] + lineas_ventas(datos)
    lineas += ["", f"👀 Ventas observadas: {datos['observadas']} · ❌ Anuladas: {datos['anuladas']}"]

    # Mermas y ajustes: cuántas veces y cuánto en total por producto y sucursal
    lineas.append("")
    if not datos["mermas_ajustes"]:
        lineas.append("🗑️ Sin mermas ni ajustes.")
    titulos = {"merma": "🗑️ <b>Mermas</b>", "ajuste": "🔧 <b>Ajustes</b>"}
    tipo_actual = None
    for tipo, producto, unidad, sucursal, veces, total in datos["mermas_ajustes"]:
        if tipo != tipo_actual:
            if tipo_actual is not None:
                lineas.append("")
            lineas.append(titulos.get(tipo, h(tipo)))
            tipo_actual = tipo
        lineas.append(f"• {h(producto)} ({h(sucursal)}): {plural(veces, 'vez', 'veces')}, "
                      f"{formatear_cantidad(total, unidad)}")

    # Cajas cerradas con diferencia
    lineas.append("")
    if not datos["diferencias_caja"]:
        lineas.append("💵 Ninguna caja cerró con diferencia.")
    else:
        lineas.append("💵 <b>Cajas con diferencia</b>")
        for caja_id, sucursal, cerrada_en, esperado, contado, diferencia in datos["diferencias_caja"]:
            lineas.append(f"• {h(sucursal)}, {formatear_fecha_hora(cerrada_en)}: {formatear_dinero(diferencia)} "
                          f"(esperado {formatear_dinero(esperado)}, contado {formatear_dinero(contado)})")
    return "\n".join(lineas)


# ============================================================================
# Gráfico (matplotlib → PNG en memoria, como en la materia)
# ============================================================================

# Colores categóricos en orden fijo (paleta validada para daltonismo): cada sucursal conserva el suyo
COLORES_SUCURSALES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
COLOR_OTRAS = "#898781"
FONDO, TINTA, TINTA_SECUNDARIA, GRILLA, EJE = "#fcfcfb", "#0b0b0b", "#52514e", "#e1e0d9", "#c3c2b7"


def dibujar_grafico_ventas(dias, series):
    """Barras agrupadas: una por sucursal y por día. Devuelve los bytes del PNG."""
    fig, ax = plt.subplots(figsize=(9, 4.5), dpi=120)
    fig.patch.set_facecolor(FONDO)
    ax.set_facecolor(FONDO)

    ancho_grupo = 0.8
    ancho = ancho_grupo / max(len(series), 1)
    for i, (nombre, totales) in enumerate(series):
        posiciones = [x - ancho_grupo / 2 + ancho * (i + 0.5) for x in range(len(dias))]
        color = COLORES_SUCURSALES[i] if i < len(COLORES_SUCURSALES) else COLOR_OTRAS
        total = sum(totales, Decimal(0))
        ax.bar(posiciones, [float(t) for t in totales], width=ancho, color=color,
               edgecolor=FONDO, linewidth=1.5,   # separación fina entre barras vecinas
               label=f"{nombre} · total {formatear_dinero(total)}")

    ax.set_xticks(range(len(dias)))
    ax.set_xticklabels([f"{DIAS_SEMANA[d.weekday()]}\n{d:%d/%m}" for d in dias])
    ax.yaxis.set_major_formatter(FuncFormatter(lambda valor, _: f"$ {_con_miles(Decimal(valor), 0)}"))
    ax.set_ylim(bottom=0)
    ax.grid(axis="y", color=GRILLA, linewidth=0.8)
    ax.set_axisbelow(True)
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.spines["bottom"].set_color(EJE)
    ax.tick_params(colors=TINTA_SECUNDARIA, labelsize=8, length=0)
    ax.set_title(f"Ventas válidas por día, del {formatear_fecha(dias[0])} al {formatear_fecha(dias[-1])}",
                 fontsize=12, color=TINTA, loc="left", pad=12)
    ax.legend(frameon=False, loc="upper left", ncol=len(series), fontsize=9,
              labelcolor=TINTA_SECUNDARIA, bbox_to_anchor=(0, -0.14))

    buffer = BytesIO()
    fig.tight_layout()
    fig.savefig(buffer, format="png", facecolor=FONDO)
    plt.close(fig)
    return buffer.getvalue()


# ============================================================================
# Lo que comparten los handlers de Telegram y el modo --probar
# ============================================================================

async def generar_texto_ventas(cual, referencia=None):
    desde, hasta = periodo(cual, referencia)
    return texto_ventas(cual, await consultar_ventas(desde, hasta))


async def generar_texto_resumen(cual, referencia=None):
    """Resumen de la semana o el mes ANTERIOR completo (lo que mandan las tareas programadas)."""
    desde, hasta = periodo(f"{cual}_anterior", referencia)
    return texto_resumen(cual, await consultar_resumen(desde, hasta))


async def generar_grafico_ventas(referencia=None):
    """PNG de los últimos DIAS_GRAFICO días (hoy incluido), o None si no hubo ventas."""
    hasta = referencia or hoy()
    desde = hasta - timedelta(days=DIAS_GRAFICO - 1)
    dias, series = await consultar_ventas_diarias(desde, hasta)
    if not any(total for _, totales in series for total in totales):
        return None
    return dibujar_grafico_ventas(dias, series)


async def cargar_autorizados():
    """Recarga las dueñas autorizadas desde la base y actualiza el filtro `autorizados`."""
    nuevos = await consultar_autorizados()
    actuales = set(autorizados.user_ids)
    if nuevos - actuales:
        autorizados.add_user_ids(nuevos - actuales)
    if actuales - nuevos:
        autorizados.remove_user_ids(actuales - nuevos)
    if nuevos != actuales:
        logging.info("dueñas autorizadas: %s", sorted(nuevos))


def leer_estado():
    """Devuelve el estado guardado o None si no hay archivo (primer arranque)."""
    try:
        with open(ARCHIVO_ESTADO, encoding="utf-8") as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        return None
    except (ValueError, OSError) as error:
        logging.warning("No pude leer %s (%s): se toma como primer arranque", ARCHIVO_ESTADO, error)
        return None


def guardar_estado():
    os.makedirs(DIR_DATOS, exist_ok=True)
    temporal = ARCHIVO_ESTADO + ".tmp"
    with open(temporal, "w", encoding="utf-8") as archivo:
        json.dump({"ultimo_id": estado["ultimo_id"]}, archivo)
    os.replace(temporal, ARCHIVO_ESTADO)  # reemplazo atómico: nunca queda un archivo a medio escribir


# ============================================================================
# Handlers de Telegram
# ============================================================================

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE, texto):
    for parte in partir_mensaje(texto):
        await context.bot.send_message(update.effective_chat.id, text=parte, parse_mode=ParseMode.HTML)


async def sin_autorizacion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    usuario = update.effective_user
    if usuario is None or update.effective_chat is None:
        return
    logging.warning("intento de conexión de: %s (%s)", usuario.id, usuario.full_name)
    # Puede ser una dueña que acaba de cargar su telegram_id: se recarga antes de rechazarla
    try:
        await cargar_autorizados()
    except aiomysql.Error as error:
        logging.warning("No pude recargar las autorizadas: %s", error)
    if usuario.id in autorizados.user_ids:
        await context.bot.send_message(update.effective_chat.id, text="✅ Ya estás autorizada/o.")
        await start(update, context)
    else:
        await context.bot.send_message(
            update.effective_chat.id,
            text=f"⛔ No estás autorizado para usar este bot.\n\n"
                 f"Si sos la dueña, cargá este ID de Telegram en tu usuario del sistema: <code>{usuario.id}</code>",
            parse_mode=ParseMode.HTML)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    usuario = update.effective_user
    logging.info("se conectó: " + str(usuario.id))
    nombre = usuario.first_name or ""
    apellido = usuario.last_name or ""
    nombre_completo = f"{nombre} {apellido}".strip()
    await context.bot.send_message(
        update.effective_chat.id,
        text=f"¡Hola, {nombre_completo}! 👋 Te doy la bienvenida al bot de Punto Lácteo 🧀\n\n"
             "Usá los botones de abajo o estos comandos:\n"
             "/stock texto: stock de los productos que contienen ese texto\n"
             "/ventas: ventas de hoy (o /ventas semana, /ventas mes)\n"
             "/resumen semana o /resumen mes: resumen de la semana o el mes pasado\n"
             "/acercade: qué hace este bot\n\n"
             "También te aviso cuando el stock baja del mínimo, cuando observan una venta, "
             "cuando hay mermas o ajustes y cuando una caja cierra con diferencia. 🔔",
        reply_markup=ReplyKeyboardMarkup(TECLADO, resize_keyboard=True))


async def acercade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        update.effective_chat.id,
        text="🧀 Bot de Punto Lácteo, el sistema de ventas y stock del local.\n"
             "Avisa las novedades de las dos sucursales y manda un resumen los lunes y el primer día de cada mes.\n"
             "Hecho para la materia IoT de la FIO (UNaM).")


async def stock_bajo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("stock bajo")
    await responder(update, context, texto_stock_bajo(await consultar_stock_bajo()))


async def stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buscado = " ".join(context.args).strip()[:80]
    if not buscado:
        await context.bot.send_message(update.effective_chat.id,
                                       text="Uso: /stock texto, por ejemplo /stock queso 🧀")
        return
    logging.info("stock: %s", buscado)
    await responder(update, context, texto_stock_producto(buscado, await consultar_stock_producto(buscado)))


async def ventas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Con el botón llega "ventas hoy|semana|mes" (el Regex lo captura); con /ventas, hoy
    # (o lo que se escriba después: /ventas semana)
    if context.matches:
        cual = context.matches[0].group(1).lower()
    elif context.args and context.args[0].lower() in ("hoy", "semana", "mes"):
        cual = context.args[0].lower()
    else:
        cual = "hoy"
    logging.info("ventas %s", cual)
    await responder(update, context, await generar_texto_ventas(cual))


async def resumen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cual = context.args[0].lower() if context.args else ""
    if cual not in ("semana", "mes"):
        await context.bot.send_message(update.effective_chat.id,
                                       text="Uso: /resumen semana o /resumen mes (la semana o el mes pasado completo)")
        return
    logging.info("resumen %s (pedido a mano)", cual)
    await responder(update, context, await generar_texto_resumen(cual))


async def grafico(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("gráfico ventas")
    png = await generar_grafico_ventas()
    if png is None:
        await context.bot.send_message(update.effective_chat.id,
                                       text=f"📊 Sin ventas en los últimos {DIAS_GRAFICO} días.")
        return
    buffer = BytesIO(png)
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=buffer,
                                 caption=f"📊 Ventas válidas de los últimos {DIAS_GRAFICO} días por sucursal")
    buffer.close()


async def desconocido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(update.effective_chat.id,
                                   text="No entendí 🤔 Usá los botones o escribí /start para ver los comandos.")


async def manejar_error(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Registra cualquier error de un handler o de una tarea y, si vino de un mensaje, avisa."""
    if isinstance(context.error, aiomysql.Error):
        logging.error("Error de la base: %s", context.error)
    else:
        logging.error("Error inesperado", exc_info=context.error)
    if isinstance(update, Update) and update.effective_chat:
        try:
            await context.bot.send_message(update.effective_chat.id,
                                           text="😵 Hubo un problema al consultar los datos. Probá de nuevo en un rato.")
        except TelegramError:
            pass


# ============================================================================
# Tareas programadas (JobQueue)
# ============================================================================

async def refrescar_autorizados(context: ContextTypes.DEFAULT_TYPE):
    await cargar_autorizados()


async def revisar_notificaciones(context: ContextTypes.DEFAULT_TYPE):
    """Cada 30 s: manda a las dueñas los avisos nuevos de la tabla notificacion."""
    if estado["ultimo_id"] is None:
        guardado = leer_estado()
        try:
            estado["ultimo_id"] = int(guardado["ultimo_id"])
            logging.info("avisos: se sigue desde el id %s", estado["ultimo_id"])
        except (TypeError, KeyError, ValueError):
            # Primer arranque (o volumen borrado): se empieza desde el último aviso existente,
            # para no inundar a la dueña con avisos viejos
            estado["ultimo_id"] = await consultar_max_notificacion()
            guardar_estado()
            logging.info("primer arranque: los avisos empiezan después del id %s", estado["ultimo_id"])
            return

    filas = await consultar_notificaciones_nuevas(estado["ultimo_id"])
    if not filas:
        return
    await cargar_autorizados()
    chats = sorted(autorizados.user_ids)   # en un chat privado, chat_id = id del usuario

    if not chats:
        # Decisión: sin dueñas con telegram_id los avisos se saltean igual. Si se guardaran, la
        # dueña recibiría de golpe todo lo acumulado el día que se registre.
        estado["ultimo_id"] = filas[-1][0]
        guardar_estado()
        logging.warning("%s avisos nuevos sin dueñas con telegram_id cargado: se saltean hasta el id %s",
                        len(filas), estado["ultimo_id"])
        return

    for id_, tipo, mensaje in filas:
        for chat_id in chats:
            try:
                # El mensaje ya viene listo del backend; va como texto común (sin HTML)
                await context.bot.send_message(chat_id, text=mensaje)
            except (Forbidden, BadRequest) as error:
                # La dueña bloqueó el bot o nunca le escribió: reintentar no sirve, se saltea
                logging.warning("No pude mandar el aviso %s a %s: %s", id_, chat_id, error)
            except TelegramError as error:
                # Telegram no respondió: no se avanza, y el aviso se reintenta en la próxima vuelta.
                # Si ya le llegó a otra dueña, a ella le llega dos veces (preferible a perderlo).
                logging.warning("Telegram falló con el aviso %s: %s. Se reintenta en %s s",
                                id_, error, INTERVALO_NOTIFICACIONES)
                return
        estado["ultimo_id"] = id_
        guardar_estado()
        logging.info("aviso %s (%s) enviado", id_, tipo)


async def enviar_a_duenias(context: ContextTypes.DEFAULT_TYPE, texto):
    await cargar_autorizados()
    if not autorizados.user_ids:
        logging.warning("No hay dueñas con telegram_id cargado: el resumen no se manda")
        return
    for chat_id in sorted(autorizados.user_ids):
        try:
            for parte in partir_mensaje(texto):
                await context.bot.send_message(chat_id, text=parte, parse_mode=ParseMode.HTML)
        except TelegramError as error:
            logging.warning("No pude mandar el resumen a %s: %s", chat_id, error)


async def enviar_resumen_semanal(context: ContextTypes.DEFAULT_TYPE):
    logging.info("resumen semanal programado")
    await enviar_a_duenias(context, await generar_texto_resumen("semana"))


async def enviar_resumen_mensual(context: ContextTypes.DEFAULT_TYPE):
    logging.info("resumen mensual programado")
    await enviar_a_duenias(context, await generar_texto_resumen("mes"))


async def al_iniciar(application: Application):
    """Se ejecuta una vez, antes de empezar a recibir mensajes."""
    try:
        # El menú de comandos que muestra Telegram al escribir /
        await application.bot.set_my_commands([
            BotCommand("start", "Menú y botones"),
            BotCommand("stock", "Stock de un producto: /stock queso"),
            BotCommand("ventas", "Ventas de hoy (o /ventas semana, /ventas mes)"),
            BotCommand("resumen", "Resumen de la semana o el mes pasado"),
            BotCommand("acercade", "Qué hace este bot"),
        ])
    except TelegramError as error:
        logging.warning("No pude cargar el menú de comandos: %s", error)
    try:
        await cargar_autorizados()
    except aiomysql.Error as error:
        logging.warning("No pude cargar las dueñas autorizadas (se reintenta en %s s): %s",
                        INTERVALO_AUTORIZADOS, error)


# ============================================================================
# Modo --probar (sin Telegram)
# ============================================================================

AYUDA_PROBAR = """Uso: python telegrambot.py --probar MODO
  ventas-hoy | ventas-semana | ventas-mes        [AAAA-MM-DD para usar otra fecha como hoy]
  resumen-semana | resumen-mes                   [AAAA-MM-DD] (semana o mes ANTERIOR completo)
  stock-bajo
  stock <texto>
  notificaciones                                 (avisos pendientes; no modifica el estado)
  autorizados
  grafico <archivo.png>                          [AAAA-MM-DD]"""


async def probar(argumentos):
    if not argumentos:
        print(AYUDA_PROBAR)
        return 2
    modo, resto = argumentos[0], argumentos[1:]

    def fecha_opcional(posicion=0):
        return date.fromisoformat(resto[posicion]) if len(resto) > posicion else None

    if modo in ("ventas-hoy", "ventas-semana", "ventas-mes"):
        texto = await generar_texto_ventas(modo.split("-")[1], fecha_opcional())
    elif modo in ("resumen-semana", "resumen-mes"):
        texto = await generar_texto_resumen(modo.split("-")[1], fecha_opcional())
    elif modo == "stock-bajo":
        texto = texto_stock_bajo(await consultar_stock_bajo())
    elif modo == "stock":
        buscado = " ".join(resto).strip()
        if not buscado:
            print(AYUDA_PROBAR)
            return 2
        texto = texto_stock_producto(buscado, await consultar_stock_producto(buscado))
    elif modo == "notificaciones":
        guardado = leer_estado()
        maximo = await consultar_max_notificacion()
        if guardado is None:
            lineas = [f"Sin {ARCHIVO_ESTADO}: en el primer arranque ultimo_id = MAX(id) = {maximo} "
                      "y no se manda nada viejo.", "", "Últimos avisos de la tabla, como ejemplo:"]
            filas = await consultar_ultimas_notificaciones()
        else:
            lineas = [f"ultimo_id guardado: {guardado['ultimo_id']} · MAX(id): {maximo}", "", "Pendientes de envío:"]
            filas = await consultar_notificaciones_nuevas(int(guardado["ultimo_id"]))
        lineas += [f"[{id_}] {tipo}: {mensaje}" for id_, tipo, mensaje in filas] or ["(ninguno)"]
        texto = "\n".join(lineas)
    elif modo == "autorizados":
        ids = sorted(await consultar_autorizados())
        texto = f"Dueñas autorizadas: {len(ids)}" + (f" ({', '.join(map(str, ids))})" if ids else "")
    elif modo == "grafico":
        archivo = resto[0] if resto else "grafico_ventas.png"
        png = await generar_grafico_ventas(fecha_opcional(1))
        if png is None:
            texto = f"📊 Sin ventas en los últimos {DIAS_GRAFICO} días (no se guardó {archivo})."
        else:
            with open(archivo, "wb") as salida:
                salida.write(png)
            texto = f"📊 Gráfico guardado en {archivo} ({len(png)} bytes)"
    else:
        print(AYUDA_PROBAR)
        return 2

    print(a_texto_plano(texto))
    return 0


# ============================================================================
# Arranque
# ============================================================================

def esperar_para_siempre():
    """Sin token el bot no puede hacer nada, pero tampoco termina: el contenedor tiene
    restart: unless-stopped y se reiniciaría sin parar."""
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))   # para que docker stop no espere 10 s
    while True:
        time.sleep(3600)


def registrar(application: Application):
    """Registra los handlers y las tareas programadas (separado de main para poder probarlo)."""
    # Primero: todo lo que venga de alguien que no es una dueña autorizada termina acá
    application.add_handler(MessageHandler(filters.ALL & ~autorizados, sin_autorizacion))
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('acercade', acercade))
    application.add_handler(CommandHandler('stock', stock))
    application.add_handler(CommandHandler('ventas', ventas))
    application.add_handler(CommandHandler('resumen', resumen))
    application.add_handler(MessageHandler(filters.Regex(re.compile(r"^stock bajo$", re.IGNORECASE)), stock_bajo))
    application.add_handler(MessageHandler(filters.Regex(re.compile(r"^ventas (hoy|semana|mes)$", re.IGNORECASE)), ventas))
    application.add_handler(MessageHandler(filters.Regex(re.compile(r"^gr[aá]fico ventas$", re.IGNORECASE)), grafico))
    application.add_handler(MessageHandler(filters.TEXT, desconocido))   # el resto, incluidos comandos desconocidos
    application.add_error_handler(manejar_error)

    tareas = application.job_queue
    tareas.run_repeating(revisar_notificaciones, interval=INTERVALO_NOTIFICACIONES, first=5)
    tareas.run_repeating(refrescar_autorizados, interval=INTERVALO_AUTORIZADOS, first=INTERVALO_AUTORIZADOS)
    tareas.run_daily(enviar_resumen_semanal, time=HORA_RESUMENES, days=(LUNES,))
    tareas.run_monthly(enviar_resumen_mensual, when=HORA_RESUMENES, day=1)


def main():
    if not token:
        logging.warning("TB_TOKEN no configurado: el bot queda inactivo hasta que se cargue en .env "
                        "(después: docker compose up -d telegrambot)")
        esperar_para_siempre()

    application = Application.builder().token(token).post_init(al_iniciar).build()
    registrar(application)
    application.run_polling()


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == "--probar":
        sys.stdout.reconfigure(encoding="utf-8")   # para los emojis en la consola de Windows
        sys.exit(asyncio.run(probar(sys.argv[2:])))
    main()
