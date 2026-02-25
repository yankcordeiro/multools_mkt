import streamlit as st
import pandas as pd
import csv
import re
import io

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(
    page_title="Ferramentas Dgtais",
    layout="wide",
    page_icon="✅"
)

# =========================
# LOGO E CABEÇALHO
# =========================

# Se você tiver um logo em arquivo, basta trocar 'logo.png' pelo nome/path do seu arquivo
# Ex: 'static/logo_dgtais.png'
# Comentar/ajustar como preferir:

col_logo, col_title = st.columns([1, 4])
with col_logo:
    # TROQUE AQUI PELO SEU LOGO
    # Se não tiver logo, pode comentar a linha abaixo
    st.image("logo.png", use_container_width=True)  # <--- SUBSTITUA 'logo.png' PELO SEU ARQUIVO

with col_title:
    st.title("Ferramentas de Marketing Digital")
    st.write("Coleção de utilitários para planilhas, contatos e campanhas.")

st.markdown("---")

# =========================
# MENU LATERAL
# =========================
with st.sidebar:
    st.header("Módulos")
    aba = st.radio(
        "Escolha o módulo:",
        [
            "Contador de Eventos/Origens",
            "Separador de Números CSV",
            "Formatador de Telefones"
        ]
    )
    st.markdown("---")
    st.caption("Dgtais – Yank Cordeiro")

# =========================
# MÓDULO 1 – CONTADOR
# =========================
if aba == "Contador de Eventos/Origens":
    st.subheader("Contador de Eventos e Origens")

    st.markdown(
        "Envie uma planilha Excel com as colunas **`eventos`** e **`origens`**. "
        "O app conta quantas vezes cada evento e cada origem aparecem."
    )

    arquivo = st.file_uploader(
        "Selecione a planilha (.xlsx ou .xls)",
        type=["xlsx", "xls"],
        key="contador_uploader"
    )

    if arquivo is not None:
        if st.button("Processar planilha", type="primary"):
            try:
                df = pd.read_excel(arquivo)
            except Exception as e:
                st.error(f"Não foi possível ler a planilha: {e}")
            else:
                # Verifica colunas obrigatórias
                for col in ['eventos', 'origens']:
                    if col not in df.columns:
                        st.error(f"Coluna obrigatória **'{col}'** não encontrada na planilha.")
                        st.stop()

                # Limpeza e contagem
                df['evento_limpo'] = (
                    df['eventos'].astype(str)
                                 .str.split('/', n=1).str[0]
                                 .str.strip()
                )
                ce = df['evento_limpo'].value_counts()
                co = df['origens'].astype(str).value_counts()

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("### Contagem de Eventos")
                    df_eventos = ce.rename("Quantidade").reset_index()
                    df_eventos.columns = ["Evento", "Quantidade"]
                    st.dataframe(df_eventos, use_container_width=True)
                    st.info(f"**Total de registros de eventos:** {int(ce.sum())}")

                with col2:
                    st.markdown("### Contagem de Origens")
                    df_origens = co.rename("Quantidade").reset_index()
                    df_origens.columns = ["Origem", "Quantidade"]
                    st.dataframe(df_origens, use_container_width=True)
                    st.info(f"**Total de registros de origens:** {int(co.sum())}")

                # Pequenos gráficos (opcional)
                with st.expander("Ver gráficos"):
                    st.bar_chart(
                        df_eventos.set_index("Evento")["Quantidade"],
                        use_container_width=True
                    )
                    st.bar_chart(
                        df_origens.set_index("Origem")["Quantidade"],
                        use_container_width=True
                    )

# =========================
# MÓDULO 2 – SEPARADOR CSV
# =========================
elif aba == "Separador de Números CSV":
    st.subheader("Separador de Números CSV")

    st.markdown(
        "Envie um arquivo CSV com colunas: **Nome ; Email ; Telefones**. "
        "Se na coluna *Telefones* houver vários números separados por `;`, "
        "o app vai gerar uma linha para cada número."
    )

    arquivo = st.file_uploader(
        "Selecione o arquivo CSV",
        type=["csv"],
        key="separador_uploader"
    )
    nome_saida = st.text_input(
        "Nome do arquivo de saída (sem extensão)",
        value="telefones_separados"
    )

    if arquivo is not None and nome_saida.strip():
        if st.button("Processar CSV", type="primary"):
            conteudo = arquivo.read()
            data = None

            # Tenta ler em UTF-8, depois Latin-1
            for enc in ("utf-8", "latin-1"):
                try:
                    texto = conteudo.decode(enc)
                    reader = csv.reader(texto.splitlines(), delimiter=';')
                    data = list(reader)
                    break
                except Exception:
                    data = None

            if data is None:
                st.error("Falha ao ler o arquivo. Verifique o formato e o encoding.")
            else:
                new_data = []
                for row in data:
                    if len(row) >= 3:
                        name, email, phones = row[0], row[1], row[2]
                        for ph in phones.split(';'):
                            new_data.append([name, email, ph.strip()])

                # Gera CSV em memória para download
                buffer = io.StringIO()
                writer = csv.writer(buffer, delimiter=';')
                writer.writerows(new_data)
                buffer.seek(0)

                st.success(f"Processamento concluído. {len(new_data)} linhas geradas.")

                # Preview
                if new_data:
                    preview_cols = ["Nome", "Email", "Telefone"]
                    df_preview = pd.DataFrame(new_data, columns=preview_cols)
                    st.dataframe(df_preview.head(20), use_container_width=True)

                # Botão de download
                st.download_button(
                    label="Baixar CSV processado",
                    data=buffer.getvalue().encode("utf-8"),
                    file_name=f"{nome_saida}.csv",
                    mime="text/csv"
                )

# =========================
# MÓDULO 3 – FORMATADOR TELEFONES
# =========================
elif aba == "Formatador de Telefones":
    st.subheader("Formatador de Números de Telefone")

    st.markdown(
        "Envie um arquivo CSV com uma coluna de telefone (por exemplo: "
        "**telefone**, **Telefone**, **phone**, etc.).\n\n"
        "O app vai:\n"
        "- Limpar caracteres não numéricos\n"
        "- Padronizar para o formato internacional brasileiro (ex: 55DD9XXXXXXXX)\n"
        "- Classificar se é **Celular** ou **Fixo**"
    )

    arquivo = st.file_uploader(
        "Selecione o arquivo CSV",
        type=["csv"],
        key="formatador_uploader"
    )

    if arquivo is not None:
        if st.button("Formatar telefones", type="primary"):

            # Funções de limpeza e formatação (copiadas da sua lógica original)
            def limpar(numero):
                return re.sub(r'\D', '', str(numero))

            def formatar(numero):
                num = limpar(numero)
                if len(num) == 10:
                    # Adiciona nono dígito se 3º dígito for 6-9
                    if num[2] in '6789':
                        num = f"55{num[:2]}9{num[2:]}"
                    else:
                        num = f"55{num}"
                elif len(num) == 11:
                    num = f"55{num}"
                return num

            def tipo(num):
                s = str(num)
                if len(s) != 13:
                    return "Inválido"
                return "Celular" if s[4] == '9' else "Fixo"

            conteudo = arquivo.read()
            texto = None
            for enc in ("utf-8", "latin-1"):
                try:
                    texto = conteudo.decode(enc)
                    break
                except Exception:
                    texto = None

            if texto is None:
                st.error("Não foi possível decodificar o arquivo.")
            else:
                leitor = csv.reader(texto.splitlines(), delimiter=';')
                linhas = list(leitor)

                if not linhas:
                    st.error("Arquivo vazio ou sem linhas válidas.")
                else:
                    # encontra coluna de telefone
                    idx = next(
                        (i for i, h in enumerate(linhas[0])
                         if 'telefone' in h.lower() or 'phone' in h.lower()),
                        None
                    )

                    if idx is None:
                        st.error("Coluna de telefone não encontrada no cabeçalho.")
                    else:
                        novas = []
                        for i, row in enumerate(linhas):
                            if i == 0:
                                row = row + ["Numero_Formatado", "Tipo_Telefone"]
                            else:
                                fmt = formatar(row[idx])
                                row = row + [fmt, tipo(fmt)]
                            novas.append(row)

                        # Gera CSV em memória
                        buffer = io.StringIO()
                        writer = csv.writer(buffer, delimiter=';')
                        writer.writerows(novas)
                        buffer.seek(0)

                        df_preview = pd.DataFrame(novas[1:], columns=novas[0])

                        st.success("Telefones formatados com sucesso.")
                        st.dataframe(df_preview.head(20), use_container_width=True)

                        st.download_button(
                            label="Baixar CSV formatado",
                            data=buffer.getvalue().encode("utf-8"),
                            file_name="telefones_formatados.csv",
                            mime="text/csv"
                        )

# =========================
# RODAPÉ
# =========================
st.markdown("---")
st.caption("Dgtais – Yank Cordeiro – Marketing Digital")
