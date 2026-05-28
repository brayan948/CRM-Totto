import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_loader import load_all

# ── Configuración global ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="CRM Totto Colombia",
    page_icon="🎒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Colores de marca ──────────────────────────────────────────────────────────
TOTTO_NARANJA = "#E8521A"
TOTTO_AZUL    = "#1D3557"
COLORES_TIPO  = {
    "B2C - Consumidor final":    "#E8521A",
    "Colegio / Universidad":     "#1D9E75",
    "Empresa corporativa":       "#378ADD",
    "Distribuidor multimarca":   "#BA7517",
    "Franquiciado":              "#534AB7",
}
COLORES_ETAPA = {
    "Prospecto":       "#9CA3AF",
    "Primer contacto": "#60A5FA",
    "Primera compra":  "#34D399",
    "Recompra":        "#FBBF24",
    "Fidelizado":      "#E8521A",
}

# ── CSS personalizado ─────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stSidebar"] { background-color: #1D3557; }
[data-testid="stSidebar"] * { color: white !important; }
[data-testid="stSidebar"] .stSelectbox label { color: #CBD5E1 !important; }
.metric-card {
    background: white; border-radius: 12px; padding: 1.2rem 1.4rem;
    border-left: 4px solid #E8521A; box-shadow: 0 1px 6px rgba(0,0,0,.08);
}
.metric-title { font-size: 12px; color: #6B7280; font-weight: 500; text-transform: uppercase; letter-spacing: .05em; margin-bottom: 4px; }
.metric-value { font-size: 28px; font-weight: 700; color: #1D3557; }
.metric-delta { font-size: 12px; color: #10B981; margin-top: 2px; }
.section-title { font-size: 18px; font-weight: 600; color: #1D3557; margin: 1.5rem 0 .75rem; border-bottom: 2px solid #E8521A; padding-bottom: 6px; }
</style>
""", unsafe_allow_html=True)

# ── Carga de datos ────────────────────────────────────────────────────────────
clientes, pedidos, detalles, productos, tipos, etapas, canales = load_all()

# ── Sidebar - navegación ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎒 CRM Totto")
    st.markdown("**Colombia · Proyecto SCRUM**")
    st.markdown("---")
    pagina = st.radio("Navegación", [
        "📊 Dashboard",
        "👥 Clientes",
        "🏷️ Segmentación",
        "📈 Indicadores",
        "🔍 Perfil de Cliente",
    ])
    st.markdown("---")
    st.caption("Brayan Morera · Breyner Cortez")
    st.caption("Ucompensar · 2026")

# ═════════════════════════════════════════════════════════════════════════════
# PÁGINA 1 · DASHBOARD (US-10)
# ═════════════════════════════════════════════════════════════════════════════
if pagina == "📊 Dashboard":
    st.title("📊 Dashboard General — CRM Totto Colombia")

    total = len(clientes)
    activos = int((clientes["estado"] == "activo").sum())
    nuevos_30 = int((clientes["fecha_registro"] >= pd.Timestamp("2026-04-28")).sum())
    fidelizados = int((clientes["nombre_etapa"] == "Fidelizado").sum())

    c1, c2, c3, c4 = st.columns(4)
    for col, titulo, valor, delta in zip(
        [c1, c2, c3, c4],
        ["Total Clientes", "Clientes Activos", "Nuevos (30 días)", "Fidelizados"],
        [total, activos, nuevos_30, fidelizados],
        [None, f"{activos/total*100:.1f}% del total", "último mes", f"{fidelizados/total*100:.1f}% del total"],
    ):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">{titulo}</div>
                <div class="metric-value">{valor:,}</div>
                <div class="metric-delta">{delta or ''}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("")

    col_l, col_r = st.columns([1.1, 0.9])

    with col_l:
        st.markdown('<div class="section-title">Clientes nuevos por mes</div>', unsafe_allow_html=True)
        mens = (clientes.set_index("fecha_registro")
                .resample("ME")["id_cliente"].count()
                .reset_index(name="nuevos"))
        mens["mes"] = mens["fecha_registro"].dt.strftime("%b %Y")
        fig = px.bar(mens, x="mes", y="nuevos",
                     color_discrete_sequence=[TOTTO_NARANJA])
        fig.update_layout(xaxis_title="", yaxis_title="Nuevos clientes",
                          plot_bgcolor="white", paper_bgcolor="white",
                          xaxis=dict(tickangle=-45))
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-title">Distribución por tipo</div>', unsafe_allow_html=True)
        tipo_cnt = clientes["nombre_tipo"].value_counts().reset_index()
        tipo_cnt.columns = ["Tipo", "Cantidad"]
        fig2 = px.pie(tipo_cnt, names="Tipo", values="Cantidad",
                      color="Tipo", color_discrete_map=COLORES_TIPO, hole=0.45)
        fig2.update_traces(textposition="outside", textinfo="percent+label")
        fig2.update_layout(showlegend=False, paper_bgcolor="white")
        st.plotly_chart(fig2, use_container_width=True)

    col_b1, col_b2 = st.columns(2)

    with col_b1:
        st.markdown('<div class="section-title">Funnel de trazabilidad</div>', unsafe_allow_html=True)
        orden = ["Prospecto","Primer contacto","Primera compra","Recompra","Fidelizado"]
        etapa_cnt = (clientes["nombre_etapa"]
                     .value_counts()
                     .reindex(orden)
                     .reset_index())
        etapa_cnt.columns = ["Etapa", "Clientes"]
        fig3 = go.Figure(go.Funnel(
            y=etapa_cnt["Etapa"], x=etapa_cnt["Clientes"],
            textinfo="value+percent initial",
            marker_color=[COLORES_ETAPA[e] for e in orden],
        ))
        fig3.update_layout(paper_bgcolor="white", plot_bgcolor="white")
        st.plotly_chart(fig3, use_container_width=True)

    with col_b2:
        st.markdown('<div class="section-title">Top 8 ciudades</div>', unsafe_allow_html=True)
        ciudades = clientes["ciudad"].value_counts().head(8).reset_index()
        ciudades.columns = ["Ciudad", "Clientes"]
        fig4 = px.bar(ciudades, x="Clientes", y="Ciudad", orientation="h",
                      color_discrete_sequence=[TOTTO_AZUL])
        fig4.update_layout(yaxis=dict(autorange="reversed"),
                           plot_bgcolor="white", paper_bgcolor="white",
                           xaxis_title="", yaxis_title="")
        st.plotly_chart(fig4, use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
# PÁGINA 2 · CLIENTES CRUD (US-06)
# ═════════════════════════════════════════════════════════════════════════════
elif pagina == "👥 Clientes":
    st.title("👥 Gestión de Clientes")

    # Filtros
    with st.expander("🔍 Filtros", expanded=True):
        f1, f2, f3, f4 = st.columns(4)
        with f1:
            tipo_filtro = st.multiselect("Tipo de cliente",
                options=clientes["nombre_tipo"].unique(),
                default=list(clientes["nombre_tipo"].unique()))
        with f2:
            estado_filtro = st.selectbox("Estado", ["Todos", "activo", "inactivo"])
        with f3:
            ciudad_filtro = st.multiselect("Ciudad",
                options=sorted(clientes["ciudad"].unique()),
                default=list(clientes["ciudad"].unique()))
        with f4:
            buscar = st.text_input("Buscar por nombre", "")

    df = clientes.copy()
    if tipo_filtro:
        df = df[df["nombre_tipo"].isin(tipo_filtro)]
    if estado_filtro != "Todos":
        df = df[df["estado"] == estado_filtro]
    if ciudad_filtro:
        df = df[df["ciudad"].isin(ciudad_filtro)]
    if buscar:
        df = df[df["nombre"].str.contains(buscar, case=False, na=False)]

    st.markdown(f"**{len(df):,} clientes** encontrados")

    cols_show = ["id_cliente","nombre","nombre_tipo","ciudad","estado","nombre_etapa","fecha_registro","email","telefono"]
    st.dataframe(
        df[cols_show].rename(columns={
            "id_cliente":"ID","nombre":"Nombre","nombre_tipo":"Tipo",
            "ciudad":"Ciudad","estado":"Estado","nombre_etapa":"Etapa",
            "fecha_registro":"Registro","email":"Email","telefono":"Teléfono"
        }),
        use_container_width=True, height=480, hide_index=True,
    )

    st.download_button(
        "⬇️ Descargar filtrado (.csv)",
        df[cols_show].to_csv(index=False).encode("utf-8-sig"),
        "clientes_filtrado.csv", "text/csv",
    )


# ═════════════════════════════════════════════════════════════════════════════
# PÁGINA 3 · SEGMENTACIÓN (US-07)
# ═════════════════════════════════════════════════════════════════════════════
elif pagina == "🏷️ Segmentación":
    st.title("🏷️ Segmentación por Tipo de Cliente")

    tipo_stats = (clientes.groupby("nombre_tipo").agg(
        Cantidad=("id_cliente","count"),
        Activos=("estado", lambda x: (x=="activo").sum()),
    ).reset_index())
    tipo_stats["% del total"] = (tipo_stats["Cantidad"] / tipo_stats["Cantidad"].sum() * 100).round(1)
    tipo_stats["% activos"]   = (tipo_stats["Activos"] / tipo_stats["Cantidad"] * 100).round(1)
    tipo_stats = tipo_stats.sort_values("Cantidad", ascending=False)

    col_l, col_r = st.columns([1, 1])

    with col_l:
        st.markdown('<div class="section-title">Cantidad por segmento</div>', unsafe_allow_html=True)
        fig = px.bar(tipo_stats, x="nombre_tipo", y="Cantidad",
                     color="nombre_tipo", color_discrete_map=COLORES_TIPO,
                     text="Cantidad")
        fig.update_traces(textposition="outside")
        fig.update_layout(showlegend=False, xaxis_title="",
                          plot_bgcolor="white", paper_bgcolor="white",
                          xaxis=dict(tickangle=-20))
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-title">Participación porcentual</div>', unsafe_allow_html=True)
        fig2 = px.pie(tipo_stats, names="nombre_tipo", values="Cantidad",
                      color="nombre_tipo", color_discrete_map=COLORES_TIPO, hole=0.4)
        fig2.update_traces(textinfo="percent+label", textposition="outside")
        fig2.update_layout(showlegend=False, paper_bgcolor="white")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-title">Resumen por segmento</div>', unsafe_allow_html=True)
    st.dataframe(
        tipo_stats.rename(columns={"nombre_tipo":"Tipo de Cliente"}),
        use_container_width=True, hide_index=True,
    )

    st.markdown('<div class="section-title">Distribución por canal de compra y segmento</div>', unsafe_allow_html=True)
    canal_tipo = (pedidos.merge(clientes[["id_cliente","nombre_tipo"]], on="id_cliente")
                  .groupby(["nombre_canal","nombre_tipo"]).size().reset_index(name="Pedidos"))
    fig3 = px.bar(canal_tipo, x="nombre_canal", y="Pedidos", color="nombre_tipo",
                  barmode="group", color_discrete_map=COLORES_TIPO,
                  labels={"nombre_canal":"Canal","nombre_tipo":"Tipo"})
    fig3.update_layout(plot_bgcolor="white", paper_bgcolor="white", xaxis_title="")
    st.plotly_chart(fig3, use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
# PÁGINA 4 · INDICADORES (US-08)
# ═════════════════════════════════════════════════════════════════════════════
elif pagina == "📈 Indicadores":
    st.title("📈 Indicadores de Cantidad de Clientes")

    total     = len(clientes)
    activos   = int((clientes["estado"]=="activo").sum())
    inactivos = total - activos
    ret_rate  = activos / total * 100

    c1, c2, c3, c4 = st.columns(4)
    for col, titulo, val, sub in zip(
        [c1,c2,c3,c4],
        ["Total registrados","Activos","Inactivos","Tasa de retención"],
        [f"{total:,}", f"{activos:,}", f"{inactivos:,}", f"{ret_rate:.1f}%"],
        ["base total","con compras recientes","sin actividad","activos / total"],
    ):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">{titulo}</div>
                <div class="metric-value">{val}</div>
                <div class="metric-delta">{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("")

    st.markdown('<div class="section-title">Crecimiento acumulado de clientes (24 meses)</div>', unsafe_allow_html=True)
    mens = (clientes.set_index("fecha_registro")
            .resample("ME")["id_cliente"].count()
            .cumsum().reset_index())
    mens.columns = ["Fecha","Total acumulado"]
    fig = px.area(mens, x="Fecha", y="Total acumulado",
                  color_discrete_sequence=[TOTTO_NARANJA])
    fig.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                      xaxis_title="", yaxis_title="Clientes acumulados")
    st.plotly_chart(fig, use_container_width=True)

    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown('<div class="section-title">Nuevos clientes por mes</div>', unsafe_allow_html=True)
        nuevos = (clientes.set_index("fecha_registro")
                  .resample("ME")["id_cliente"].count().reset_index())
        nuevos.columns = ["Fecha","Nuevos"]
        nuevos["Mes"] = nuevos["Fecha"].dt.strftime("%b %Y")
        fig2 = px.bar(nuevos, x="Mes", y="Nuevos",
                      color_discrete_sequence=[TOTTO_AZUL])
        fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                           xaxis=dict(tickangle=-45), xaxis_title="")
        st.plotly_chart(fig2, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-title">Activos vs Inactivos por segmento</div>', unsafe_allow_html=True)
        estado_tipo = (clientes.groupby(["nombre_tipo","estado"])
                       .size().reset_index(name="Cantidad"))
        fig3 = px.bar(estado_tipo, x="nombre_tipo", y="Cantidad",
                      color="estado", barmode="stack",
                      color_discrete_map={"activo": TOTTO_NARANJA,"inactivo":"#D1D5DB"},
                      labels={"nombre_tipo":"Tipo","estado":"Estado"})
        fig3.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                           xaxis=dict(tickangle=-20), xaxis_title="")
        st.plotly_chart(fig3, use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
# PÁGINA 5 · PERFIL DE CLIENTE (US-09)
# ═════════════════════════════════════════════════════════════════════════════
elif pagina == "🔍 Perfil de Cliente":
    st.title("🔍 Perfil Detallado del Cliente")

    buscar_id = st.number_input("ID del cliente", min_value=1, max_value=1500, value=1, step=1)
    cliente_row = clientes[clientes["id_cliente"] == buscar_id]

    if cliente_row.empty:
        st.warning("Cliente no encontrado.")
    else:
        c = cliente_row.iloc[0]
        pedidos_cli = pedidos[pedidos["id_cliente"] == buscar_id]

        st.markdown('<div class="section-title">Datos generales</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"**Nombre:** {c['nombre']}")
            st.markdown(f"**Email:** {c['email']}")
            st.markdown(f"**Teléfono:** {c['telefono']}")
        with col2:
            st.markdown(f"**Tipo:** {c['nombre_tipo']}")
            st.markdown(f"**Ciudad:** {c['ciudad']}")
            st.markdown(f"**Estado:** {'✅ Activo' if c['estado']=='activo' else '❌ Inactivo'}")
        with col3:
            st.markdown(f"**Etapa:** {c['nombre_etapa']}")
            st.markdown(f"**Registro:** {str(c['fecha_registro'])[:10]}")

        st.markdown('<div class="section-title">Métricas de compra</div>', unsafe_allow_html=True)
        m1, m2, m3, m4 = st.columns(4)
        n_ped = len(pedidos_cli)
        total_comp = int(pedidos_cli["monto_total"].sum()) if n_ped > 0 else 0
        ticket_avg = int(pedidos_cli["monto_total"].mean()) if n_ped > 0 else 0
        ultima = str(pedidos_cli["fecha_pedido"].max())[:10] if n_ped > 0 else "Sin compras"
        for col, titulo, valor in zip(
            [m1,m2,m3,m4],
            ["Pedidos totales","Valor total (COP)","Ticket promedio","Última compra"],
            [n_ped, f"${total_comp:,}", f"${ticket_avg:,}", ultima],
        ):
            with col:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">{titulo}</div>
                    <div class="metric-value" style="font-size:20px">{valor}</div>
                </div>""", unsafe_allow_html=True)

        if n_ped > 0:
            st.markdown('<div class="section-title">Historial de pedidos</div>', unsafe_allow_html=True)
            hist = pedidos_cli[["id_pedido","fecha_pedido","nombre_canal","estado_pedido","monto_total"]].copy()
            hist = hist.sort_values("fecha_pedido", ascending=False)
            hist["monto_total"] = hist["monto_total"].apply(lambda x: f"${x:,}")
            hist.columns = ["ID Pedido","Fecha","Canal","Estado","Monto"]
            st.dataframe(hist, use_container_width=True, hide_index=True)

            st.markdown('<div class="section-title">Compras en el tiempo</div>', unsafe_allow_html=True)
            timeline = (pedidos_cli.set_index("fecha_pedido")
                        .resample("ME")["monto_total"].sum().reset_index())
            timeline.columns = ["Fecha","Monto"]
            fig = px.bar(timeline, x="Fecha", y="Monto",
                         color_discrete_sequence=[TOTTO_NARANJA])
            fig.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                              xaxis_title="", yaxis_title="Monto COP")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Este cliente aún no tiene pedidos registrados.")
