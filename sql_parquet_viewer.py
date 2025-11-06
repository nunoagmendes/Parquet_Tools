import sqlite3
import pandas as pd
import streamlit as st
import io

st.set_page_config(page_title="SQL Viewer", layout="wide")

st.title("🧠 SQL Viewer para Parquet / CSV ")


uploaded_file = st.file_uploader("📁 Carrega ficheiro Parquet ou CSV", type=["parquet", "csv"])

if uploaded_file is not None:

    # Ler o ficheiro
    if uploaded_file.name.lower().endswith(".parquet"):
        df = pd.read_parquet(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)

    st.success(f"✅ Ficheiro `{uploaded_file.name}` carregado com sucesso!")

    # =============================
    #  🔎 MOSTRAR COLUNAS COM PESQUISA
    # =============================
    st.subheader("📋 Colunas disponíveis")

    search = st.text_input("🔍 Procurar coluna")

    filtered_cols = [c for c in df.columns if search.lower() in c.lower()]

    if not filtered_cols:
        st.write("⚠️ Nenhuma coluna encontrada.")
    else:
        st.write("🗂️ Resultado da Pesquisa:")

        # Wrapper com scroll vertical
        with st.container():
            st.markdown(
                """
                <div style="border:1px solid #cccccc; border-radius:8px;
                            padding: 12px; height:260px; overflow-y:scroll;">
                """,
                unsafe_allow_html=True
            )

            # dividir colunas em 3 listas iguais
            col1, col2, col3 = st.columns(3)

            num_cols = len(filtered_cols)
            chunk = (num_cols + 2) // 3  # divide em 3 partes iguais

            col_groups = [
                filtered_cols[i:i + chunk] for i in range(0, num_cols, chunk)
            ]

            for idx, group in enumerate(col_groups):
                container = [col1, col2, col3][idx]
                with container:
                    for c in group:
                        st.markdown(f"- **{c}**")

            st.markdown("</div>", unsafe_allow_html=True)

    # =============================
    #  📊 MOSTRAR A TABELA
    # =============================
    st.subheader("📊 Dados carregados")

    st.dataframe(
        df,
        use_container_width=True,
        height=400
    )

    st.write(f"➡️ Número de linhas: **{len(df)}**")

    # =============================
    #  🧠 SQL
    # =============================
    st.subheader("🛠️ Executar Query SQL")

    conn = sqlite3.connect(":memory:")
    df.to_sql("data", conn, index=False, if_exists="replace")

    query = st.text_area("Escreve SQL aqui:", "SELECT * FROM data LIMIT 10")

    if st.button("Executar Query"):
        try:
            result = pd.read_sql_query(query, conn)

            st.success(f"✅ Query executada — {len(result)} linhas")

            # Mostrar tabela resultante
            st.subheader("📄 Resultado da Query")
            st.dataframe(result, use_container_width=True, height=350)

            # =============================
            #  📈 GRÁFICO AUTOMÁTICO
            # =============================
            st.subheader("📈 Gráfico (auto)")

            numeric_cols = result.select_dtypes(include=["number"]).columns

            if len(numeric_cols) >= 1:
                st.line_chart(result[numeric_cols])
            else:
                st.info("Não existem colunas numéricas para gerar gráfico.")

            # =============================
            #  ⬇️ EXPORTAR RESULTADO
            # =============================

            export_format = st.selectbox("📤 Exportar resultado como:", ["CSV", "Parquet"])

            if export_format == "CSV":
                buffer = io.StringIO()
                result.to_csv(buffer, index=False)
                st.download_button(
                    label="⬇️ Download CSV",
                    data=buffer.getvalue(),
                    file_name="resultado_query.csv",
                    mime="text/csv"
                )
            else:
                buffer = io.BytesIO()
                result.to_parquet(buffer, index=False)
                st.download_button(
                    label="⬇️ Download Parquet",
                    data=buffer.getvalue(),
                    file_name="resultado_query.parquet",
                    mime="application/octet-stream"
                )

        except Exception as e:
            st.error(f"❌ Erro na query: {e}")

else:
    st.info("👆 Carrega um ficheiro para começar.")

