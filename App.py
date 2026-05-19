import streamlit as st
from datetime import date, datetime
from supabase import create_client, Client

# ---------------------------------------------------------------------------
# Configuração da página
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="CONTROLE DO REFEITORIO",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Estilo corporativo
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Source Sans 3', sans-serif;
    }

    .block-container {
        padding-top: 1.5rem;
        max-width: 1100px;
    }

    .app-header {
        display: flex;
        align-items: flex-start;
        gap: 1.25rem;
        margin-bottom: 0.5rem;
    }

    .app-logo {
        width: 72px;
        height: 72px;
        border-radius: 8px;
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a3d 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: #fff;
        font-size: 1.75rem;
        flex-shrink: 0;
    }

    .app-title {
        color: #262730;
        font-size: 1.85rem;
        font-weight: 700;
        line-height: 1.2;
        margin: 0;
    }

    .app-subtitle {
        color: #808495;
        font-size: 0.95rem;
        margin: 0.25rem 0 0 0;
    }

    .header-divider {
        border: none;
        border-top: 1px solid #e0e0e0;
        margin: 1rem 0 1.5rem 0;
    }

    div[data-testid="stForm"] {
        background: #fafbfc;
        border: 1px solid #e8eaed;
        border-radius: 8px;
        padding: 1.25rem 1.5rem 1.5rem;
    }

    .stTextInput > label,
    .stDateInput > label,
    .stNumberInput > label,
    .stSelectbox > label {
        color: #262730 !important;
        font-weight: 600 !important;
    }

    div[data-testid="stCheckbox"] label span {
        font-weight: 500;
    }

    div[data-testid="stCheckbox"] input:checked + div {
        border-color: #FF4B4B !important;
    }

    .stButton > button[kind="primary"] {
        background-color: #FF4B4B !important;
        border-color: #FF4B4B !important;
        color: white !important;
        font-weight: 600;
        border-radius: 6px;
        padding: 0.5rem 2rem;
    }

    .stButton > button[kind="primary"]:hover {
        background-color: #e04343 !important;
        border-color: #e04343 !important;
    }

    .metric-card {
        background: #F0F2F6;
        border-radius: 8px;
        padding: 1rem 1.25rem;
        text-align: center;
    }

    .metric-label {
        color: #808495;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }

    .metric-value {
        color: #262730;
        font-size: 1.75rem;
        font-weight: 700;
        margin-top: 0.25rem;
    }

    div[data-testid="stDataFrame"] thead tr th {
        background-color: #1a1a1a !important;
        color: white !important;
        font-weight: 700 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

MOTIVOS = [
    "Particular",
    "Prestador Serviço",
    "Deslocamento",
]


def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


def render_header():
    st.markdown(
        """
        <div class="app-header">
            <div class="app-logo">🍽️</div>
            <div>
                <p class="app-title">CONTROLE DO REFEITORIO</p>
                <p class="app-subtitle">
                    Registro diário de consumo no refeitório — café e refeições
                </p>
            </motion.div>
        </motion.div>
        <hr class="header-divider">
        """,
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
    sb.table("refeitorio").insert(
        {
            "data": data_lanc.isoformat(),
            "solicitante": solicitante.strip(),
            "setor": setor.strip() if setor else None,
            "motivo": motivo,
            "tipo_refeicao": tipo_refeicao,
            "qtd": qtd,
        }
    ).execute()


def load_registros(sb: Client, data_filtro: date | None):
    query = sb.table("refeitorio").select("*").order("created_at", desc=True)
    if data_filtro:
        query = query.eq("data", data_filtro.isoformat())
    return query.limit(500).execute().data


def format_registros(rows: list) -> list:
    formatted = []
    for r in rows:
        d = r.get("data", "")
        if d and len(str(d)) >= 10:
            try:
                d = datetime.strptime(str(d)[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
            except ValueError:
                pass
        formatted.append(
            {
                "Data": d,
                "Solicitante": r.get("solicitante", ""),
                "Setor": r.get("setor") or "",
                "Motivo": r.get("motivo", ""),
                "Tipo de Refeição": r.get("tipo_refeicao", ""),
                "QTD": r.get("qtd", 0),
            }
        )
    return formatted


def main():
    render_header()

    try:
        sb = get_supabase()
    except Exception as e:
        st.error(
            "Não foi possível conectar ao Supabase. "
            "Configure `SUPABASE_URL` e `SUPABASE_KEY` em `.streamlit/secrets.toml` "
            "(local) ou em Secrets no Streamlit Cloud."
        )
        st.caption(str(e))
        st.stop()

    tab_lanc, tab_consulta = st.tabs(["Novo lançamento", "Consultar registros"])

    with tab_lanc:
        with st.form("form_refeitorio", clear_on_submit=True):
            col_data, col_qtd = st.columns([2, 1])
            with col_data:
                data_lanc = st.date_input(
                    "DATA",
                    value=date.today(),
                    format="DD/MM/YYYY",
                )
            with col_qtd:
                qtd = st.number_input(
                    "QTD",
                    min_value=1,
                    max_value=999,
                    value=1,
                    step=1,
                    help="Quantidade consumida (conforme planilha)",
                )

            solicitante = st.text_input(
                "SOLICITANTE",
                placeholder="Nome do solicitante",
                max_chars=120,
            )

            col_setor, col_motivo = st.columns(2)
            with col_setor:
                setor = st.text_input(
                    "SETOR",
                    placeholder="Ex.: Máquinas, Pecuária, Florestal",
                    max_chars=80,
                )
            with col_motivo:
                motivo = st.selectbox("MOTIVO", options=MOTIVOS)

            st.markdown("**TIPO DE REFEIÇÃO** *(marque uma ou ambas)*")
            c1, c2 = st.columns(2)
            with c1:
                cafe = st.checkbox("CAFÉ")
            with c2:
                refeicao = st.checkbox("REFEIÇÃO")

            submitted = st.form_submit_button(
                "Registrar lançamento",
                type="primary",
                use_container_width=False,
            )

        if submitted:
            if not solicitante.strip():
                st.warning("Informe o **SOLICITANTE**.")
            elif not cafe and not refeicao:
                st.warning("Marque ao menos um tipo: **CAFÉ** e/ou **REFEIÇÃO**.")
            else:
                tipos = []
                if cafe:
                    tipos.append("Café")
                if refeicao:
                    tipos.append("Refeição")
                try:
                    for tipo in tipos:
                        insert_lancamento(
                            sb,
                            data_lanc,
                            solicitante,
                            setor,
                            motivo,
                            tipo,
                            qtd,
                        )
                    st.success(
                        f"Lançamento salvo: {', '.join(tipos)} — QTD {qtd} "
                        f"em {data_lanc.strftime('%d/%m/%Y')}."
                    )
                except Exception as e:
                    st.error(f"Erro ao salvar no banco: {e}")

    with tab_consulta:
        fc1, fc2 = st.columns([1, 2])
        with fc1:
            filtrar_data = st.checkbox("Filtrar por data", value=True)
        with fc2:
            data_filtro = (
                st.date_input(
                    "Data",
                    value=date.today(),
                    format="DD/MM/YYYY",
                    label_visibility="collapsed",
                )
                if filtrar_data
                else None
            )

        try:
            rows = load_registros(sb, data_filtro if filtrar_data else None)
            if rows:
                st.dataframe(
                    format_registros(rows),
                    use_container_width=True,
                    hide_index=True,
                )
                total_qtd = sum(r.get("qtd", 0) for r in rows)
                m1, m2, m3 = st.columns(3)
                with m1:
                    st.markdown(
                        f'<motion.div class="metric-card">'
                        f'<motion.div class="metric-label">Registros</motion.div>'
                        f'<motion.div class="metric-value">{len(rows)}</motion.div>'
                        f"</motion.div>",
                        unsafe_allow_html=True,
                    )
                with m2:
                    st.markdown(
                        f'<motion.div class="metric-card">'
                        f'<motion.div class="metric-label">Total QTD</motion.div>'
                        f'<motion.div class="metric-value">{total_qtd}</motion.div>'
                        f"</motion.div>",
                        unsafe_allow_html=True,
                    )
                with m3:
                    cafes = sum(
                        1 for r in rows if r.get("tipo_refeicao") == "Café"
                    )
                    st.markdown(
                        f'<motion.div class="metric-card">'
                        f'<motion.div class="metric-label">Cafés</motion.div>'
                        f'<motion.div class="metric-value">{cafes}</motion.div>'
                        f"</motion.div>",
                        unsafe_allow_html=True,
                    )
            else:
                st.info("Nenhum registro encontrado para o filtro selecionado.")
        except Exception as e:
            st.error(f"Erro ao carregar registros: {e}")


if __name__ == "__main__":
    main()
