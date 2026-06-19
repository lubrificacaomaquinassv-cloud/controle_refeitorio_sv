import streamlit as st
import pandas as pd
from datetime import date, datetime
from io import BytesIO
from supabase import create_client, Client

st.set_page_config(
    page_title="CONTROLE DIÁRIO REFEITÓRIO - SIGCF",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from sigcf_auth import exigir_acesso, logo_html

MOTIVOS = ["Particular", "Prestador Serviço", "Visita", "Deslocamento interno", "Outros"]

exigir_acesso("CONTROLE DIÁRIO REFEITÓRIO")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700&display=swap');
[data-testid="stAppViewContainer"]{background:#0a1409;}
[data-testid="stSidebar"]{background:#111c10;border-right:1px solid #1e2e1c;}
[data-testid="stHeader"]{background:#0a1409;}
h1,h2,h3,h4,p,span,label{color:#e8edd0;}
h1{font-family:'Barlow Condensed',sans-serif;letter-spacing:1px;}
.stCaption,[data-testid="stCaptionContainer"] p{color:#8aab80!important;}
.sec{font-family:'Barlow Condensed',sans-serif;font-size:12px;font-weight:700;
 letter-spacing:2px;text-transform:uppercase;color:#8aab80;
 border-left:4px solid #4a9e3f;padding-left:10px;margin:8px 0 12px;}
.cat-badge{display:inline-block;background:#0d180c;border:1px solid #4a9e3f;color:#6fcf60;
 font-family:'Barlow Condensed',sans-serif;font-weight:700;letter-spacing:1px;
 padding:4px 12px;border-radius:8px;font-size:13px;}
.cat-badge.outros{border-color:#669bbc;color:#669bbc;}
.ctx-box{background:#0d180c;border:1px solid #1e2e1c;border-radius:12px;padding:14px 16px;margin-bottom:12px;}
.logo-frame{background:linear-gradient(145deg,#0a1628,#0d2040);border:2px solid #c9a227;
 border-radius:12px;padding:5px;display:inline-block;box-shadow:0 4px 18px rgba(0,0,0,.45);}
.logo-frame img{display:block;border-radius:8px;}

.stTextInput input,.stNumberInput input,.stTextArea textarea,
[data-testid="stDateInput"] input{
 background:#dce6d2!important;color:#1a2818!important;
 border:1px solid #4a6644!important;border-radius:8px!important;}
.stTextInput input:focus,.stNumberInput input:focus,.stTextArea textarea:focus,
[data-testid="stDateInput"] input:focus{
 border-color:#6fcf60!important;box-shadow:0 0 0 1px #6fcf6044!important;}
div[data-baseweb="select"] > div{
 background:#dce6d2!important;border:1px solid #4a6644!important;
 color:#1a2818!important;border-radius:8px!important;}
div[data-baseweb="select"] div{color:#1a2818!important;}
div[data-baseweb="select"] svg{fill:#4a6644!important;}
ul[data-testid="stSelectboxVirtualDropdown"],
div[data-baseweb="popover"] ul{background:#e8edd0!important;}
div[data-baseweb="popover"] li{color:#1a2818!important;}
[data-testid="stNumberInput"] button{
 background:#cdd9c4!important;border-color:#4a6644!important;color:#1a2818!important;}
[data-testid="stForm"]{
 background:#0d180c!important;border:1px solid #1e2e1c!important;
 border-radius:12px;padding:12px 16px;}
[data-testid="stVerticalBlockBorderWrapper"]{
 background:#0d180c!important;border-color:#1e2e1c!important;}
div[data-testid="stMetric"]{background:#0d180c;border:1px solid #1e2e1c;border-radius:10px;padding:10px 14px;}
div[data-testid="stMetric"] label{color:#8aab80!important;}
div[data-testid="stMetricValue"]{color:#6fcf60!important;font-family:'Barlow Condensed',sans-serif;}

.stTabs [data-baseweb="tab-list"]{background:#0d180c;border-bottom:1px solid #1e2e1c;gap:8px;}
.stTabs [data-baseweb="tab"]{
 color:#8aab80!important;font-family:'Barlow Condensed',sans-serif;
 font-weight:600;letter-spacing:0.5px;}
.stTabs [aria-selected="true"]{
 color:#e8edd0!important;border-bottom-color:#4a9e3f!important;}
[data-testid="stExpander"]{
 background:#0d180c!important;border:1px solid #1e2e1c!important;border-radius:10px;}
[data-testid="stExpander"] summary{color:#e8edd0!important;}
div[data-testid="stCheckbox"] label span{color:#e8edd0!important;}
.stButton button,[data-testid="stFormSubmitButton"] button{
 background:#4a9e3f!important;color:#ffffff!important;border:1px solid #6fcf60!important;
 font-family:'Barlow Condensed',sans-serif;font-weight:700;letter-spacing:1.5px;
 text-transform:uppercase;border-radius:8px;}
.stButton button:hover,[data-testid="stFormSubmitButton"] button:hover{background:#3d8534!important;}
</style>
""", unsafe_allow_html=True)


def dark_table(df, height=320):
    if df.empty:
        st.info("Nenhum registro.")
        return
    rows = "".join(
        "<tr>" + "".join(
            f'<td style="padding:6px 10px;border-bottom:1px solid #1e2e1c;'
            f'color:#e8edd0;font-size:12px;white-space:nowrap;">{v}</td>'
            for v in row) + "</tr>"
        for _, row in df.iterrows())
    headers = "".join(
        f'<th style="padding:7px 10px;background:#111c10;color:#8aab80;font-size:10px;'
        f'font-weight:700;text-transform:uppercase;letter-spacing:1px;'
        f'border-bottom:2px solid #1e2e1c;white-space:nowrap;">{c}</th>'
        for c in df.columns)
    st.markdown(
        f'<div style="overflow-x:auto;border:1px solid #1e2e1c;border-radius:10px;">'
        f'<div style="max-height:{height}px;overflow-y:auto;">'
        f'<table style="width:100%;border-collapse:collapse;background:#0d180c;'
        f'font-family:Barlow Condensed,sans-serif;"><thead><tr>{headers}</tr></thead>'
        f'<tbody>{rows}</tbody></table></div></div>',
        unsafe_allow_html=True,
    )


def get_supabase() -> Client:
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


def render_header():
    col_logo, col_titulo, col_acao = st.columns([1.1, 5, 1])
    with col_logo:
        st.markdown(logo_html(118), unsafe_allow_html=True)
    with col_titulo:
        st.title("CONTROLE DIÁRIO REFEITÓRIO")
        st.caption("SIGCF — REGISTRO DIÁRIO DE CONSUMO REFEITÓRIO · DESCONTO EM FOLHA → RH")
    with col_acao:
        if st.button("🔄 Atualizar"):
            st.cache_data.clear()
            st.rerun()


def badge_motivo(motivo: str):
    cls = "" if motivo == "Particular" else " outros"
    label = "DESCONTO FOLHA" if motivo == "Particular" else motivo.upper()
    st.markdown(
        f'<p style="margin:0 0 6px;color:#8aab80;font-size:12px;text-transform:uppercase;'
        f'letter-spacing:1px;">Motivo</p>'
        f'<span class="cat-badge{cls}">{label}</span>',
        unsafe_allow_html=True,
    )


def insert_lancamento(
    sb: Client,
    data_lanc: date,
    solicitante: str,
    setor: str,
    motivo: str,
    tipo_refeicao: str,
    qtd: int,
) -> None:
    sb.table("refeitorio").insert({
        "data": data_lanc.isoformat(),
        "solicitante": solicitante.strip(),
        "setor": setor.strip() if setor else None,
        "motivo": motivo,
        "tipo_refeicao": tipo_refeicao,
        "qtd": qtd,
    }).execute()


def load_registros(sb: Client, data_filtro: date | None):
    query = sb.table("refeitorio").select("*").order("created_at", desc=True)
    if data_filtro:
        query = query.eq("data", data_filtro.isoformat())
    return query.limit(500).execute().data


def ciclo_fechamento(ref: date | None = None) -> tuple[date, date]:
    """Ciclo mensal: dia 21 do mês anterior até dia 20 do mês de referência."""
    ref = ref or date.today()
    fim = date(ref.year, ref.month, 20)
    if ref.month == 1:
        inicio = date(ref.year - 1, 12, 21)
    else:
        inicio = date(ref.year, ref.month - 1, 21)
    return inicio, fim


def load_registros_periodo(sb: Client, inicio: date, fim: date) -> list:
    return (
        sb.table("refeitorio")
        .select("*")
        .gte("data", inicio.isoformat())
        .lte("data", fim.isoformat())
        .order("data")
        .limit(5000)
        .execute()
        .data
        or []
    )


def eh_particular(motivo: str) -> bool:
    return str(motivo or "").strip().lower() == "particular"


def resumo_rh_particular(rows: list) -> pd.DataFrame:
    agg: dict[str, dict] = {}
    for r in rows:
        if not eh_particular(r.get("motivo", "")):
            continue
        nome = str(r.get("solicitante", "")).strip()
        if not nome:
            continue
        if nome not in agg:
            agg[nome] = {"Setor": str(r.get("setor") or "").strip(), "Café": 0, "Refeição": 0}
        tipo = str(r.get("tipo_refeicao", "")).strip()
        qtd = int(r.get("qtd") or 0)
        if tipo == "Café":
            agg[nome]["Café"] += qtd
        elif tipo == "Refeição":
            agg[nome]["Refeição"] += qtd

    if not agg:
        return pd.DataFrame(columns=["Nome", "Setor", "Café", "Refeição", "Total"])

    return pd.DataFrame([
        {
            "Nome": nome,
            "Setor": dados["Setor"],
            "Café": dados["Café"],
            "Refeição": dados["Refeição"],
            "Total": dados["Café"] + dados["Refeição"],
        }
        for nome, dados in sorted(agg.items(), key=lambda x: x[0].upper())
    ])


def gerar_excel(df: pd.DataFrame) -> bytes:
    buf = BytesIO()
    df.to_excel(buf, index=False, sheet_name="Desconto Folha")
    return buf.getvalue()


def format_registros(rows: list) -> pd.DataFrame:
    formatted = []
    for r in rows:
        d = r.get("data", "")
        if d and len(str(d)) >= 10:
            try:
                d = datetime.strptime(str(d)[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
            except ValueError:
                pass
        formatted.append({
            "Data": d,
            "Solicitante": r.get("solicitante", ""),
            "Setor": r.get("setor") or "",
            "Motivo": r.get("motivo", ""),
            "Tipo de Refeição": r.get("tipo_refeicao", ""),
            "QTD": r.get("qtd", 0),
        })
    return pd.DataFrame(formatted)


def main():
    render_header()
    st.divider()

    try:
        sb = get_supabase()
    except Exception as e:
        st.error(
            "Não foi possível conectar ao Supabase. "
            "Configure SUPABASE_URL e SUPABASE_KEY nos Secrets do Streamlit Cloud."
        )
        st.caption(str(e))
        st.stop()

    tab_lanc, tab_consulta, tab_rh = st.tabs([
        "📝 Novo lançamento",
        "📋 Consultar registros",
        "📊 Resumo RH — Desconto Folha",
    ])

    with tab_lanc:
        st.markdown('<div class="sec">Registrar consumo</div>', unsafe_allow_html=True)
        st.markdown('<div class="ctx-box">', unsafe_allow_html=True)

        cm1, cm2 = st.columns([3, 1])
        with cm1:
            motivo = st.selectbox("📌 Motivo", options=MOTIVOS, index=0, key="motivo_lanc")
        with cm2:
            badge_motivo(motivo)

        with st.form("form_refeitorio", clear_on_submit=True):
            col_data, col_qtd = st.columns([2, 1])
            with col_data:
                data_lanc = st.date_input("📅 Data", value=date.today(), format="DD/MM/YYYY")
            with col_qtd:
                qtd = st.number_input(
                    "🔢 QTD",
                    min_value=1,
                    max_value=999,
                    value=1,
                    step=1,
                    help="Quantidade consumida",
                )

            solicitante = st.text_input("👤 Solicitante", placeholder="Nome do solicitante", max_chars=120)
            setor = st.text_input("🏢 Setor", placeholder="Ex.: Máquinas, Pecuária, Florestal", max_chars=80)

            st.markdown('<div class="sec">Tipo de refeição</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                cafe = st.checkbox("☕ Café")
            with c2:
                refeicao = st.checkbox("🍽️ Refeição")

            submitted = st.form_submit_button("✅ Registrar lançamento", type="primary", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if submitted:
            if not solicitante.strip():
                st.warning("Informe o solicitante.")
            elif not motivo.strip():
                st.warning("Informe o motivo.")
            elif not cafe and not refeicao:
                st.warning("Marque ao menos um tipo: Café e/ou Refeição.")
            else:
                tipos = []
                if cafe:
                    tipos.append("Café")
                if refeicao:
                    tipos.append("Refeição")
                try:
                    for tipo in tipos:
                        insert_lancamento(sb, data_lanc, solicitante, setor, motivo.strip(), tipo, qtd)
                    st.success(
                        f"Lançamento salvo: {', '.join(tipos)} — QTD {qtd} "
                        f"em {data_lanc.strftime('%d/%m/%Y')}."
                    )
                except Exception as e:
                    st.error(f"Erro ao salvar no banco: {e}")

    with tab_consulta:
        st.markdown('<div class="sec">Consultar registros</div>', unsafe_allow_html=True)
        fc1, fc2 = st.columns([1, 2])
        with fc1:
            filtrar_data = st.checkbox("Filtrar por data", value=True)
        with fc2:
            data_filtro = (
                st.date_input("Data", value=date.today(), format="DD/MM/YYYY", label_visibility="collapsed")
                if filtrar_data
                else None
            )

        try:
            rows = load_registros(sb, data_filtro if filtrar_data else None)
            if rows:
                df = format_registros(rows)
                total_qtd = sum(r.get("qtd", 0) for r in rows)
                cafes = sum(1 for r in rows if r.get("tipo_refeicao") == "Café")

                m1, m2, m3 = st.columns(3)
                m1.metric("Registros", len(rows))
                m2.metric("Total QTD", total_qtd)
                m3.metric("Cafés", cafes)

                dark_table(df, height=360)
            else:
                st.info("Nenhum registro encontrado para o filtro selecionado.")
        except Exception as e:
            st.error(f"Erro ao carregar registros: {e}")

    with tab_rh:
        inicio_padrao, fim_padrao = ciclo_fechamento()
        st.markdown('<div class="sec">Resumo para desconto em folha (RH)</div>', unsafe_allow_html=True)
        st.caption(
            f"Ciclo de fechamento: **{inicio_padrao.strftime('%d/%m/%Y')}** a "
            f"**{fim_padrao.strftime('%d/%m/%Y')}** — somente motivo **Particular**. "
            f"Gerar todo dia **21** e enviar ao RH."
        )

        c1, c2 = st.columns(2)
        with c1:
            data_ini = st.date_input(
                "Período — início",
                value=inicio_padrao,
                format="DD/MM/YYYY",
                key="rh_ini",
            )
        with c2:
            data_fim = st.date_input(
                "Período — fim",
                value=fim_padrao,
                format="DD/MM/YYYY",
                key="rh_fim",
            )

        if data_ini > data_fim:
            st.error("A data inicial não pode ser maior que a data final.")
        else:
            try:
                rows_periodo = load_registros_periodo(sb, data_ini, data_fim)
                df_rh = resumo_rh_particular(rows_periodo)

                total_cafe = int(df_rh["Café"].sum()) if not df_rh.empty else 0
                total_refeicao = int(df_rh["Refeição"].sum()) if not df_rh.empty else 0
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Colaboradores", len(df_rh))
                m2.metric("Total Cafés", total_cafe)
                m3.metric("Total Refeições", total_refeicao)
                m4.metric("Total Geral", total_cafe + total_refeicao)

                if df_rh.empty:
                    st.info(
                        "Nenhum lançamento **Particular** no período selecionado. "
                        "Confira se o motivo foi registrado como Particular."
                    )
                else:
                    dark_table(df_rh, height=400)
                    nome_arquivo = (
                        f"refeitorio_desconto_folha_"
                        f"{data_ini.strftime('%Y%m%d')}_{data_fim.strftime('%Y%m%d')}.xlsx"
                    )
                    st.download_button(
                        "⬇️ Exportar Excel para RH",
                        data=gerar_excel(df_rh),
                        file_name=nome_arquivo,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                    )
                    st.caption(
                        f"Arquivo pronto para enviar ao RH — período "
                        f"{data_ini.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}."
                    )
            except Exception as e:
                st.error(f"Erro ao gerar resumo RH: {e}")

    st.divider()
    st.caption("SIGCF | NÚCLEO DE CONTROLADORIA | GESTÃO E ANÁLISE DE DADOS")


if __name__ == "__main__":
    main()
