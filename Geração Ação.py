import streamlit as st
from PIL import Image
import pandas as pd
import io
import smtplib
from email.message import EmailMessage

# CONFIGURAÇÕES - Atualize com seus dados
EMAIL_REMETENTE = "seu_email@gmail.com"             # Seu e-mail Gmail
EMAIL_SENHA_APP = "kjma dksk kbxu iwzn"           # Senha de app gerada no Gmail
EMAIL_DESTINO = "victormoreiraicnv@gmail.com"       # Destinatário do e-mail

# Estilo CSS (pode manter igual para ficar bonito)
st.markdown("""
<style>
h1 { color: #d72638; text-align: center; }
h3 { color: #666666; text-align: center; }
blockquote { color: #888888; font-style: italic; text-align: center; border-left: 4px solid #d72638; padding-left: 1rem; }
.event-card { background-color: #fcefee; padding: 1rem; border-radius: 15px; margin-bottom: 1rem; }
img { border-radius: 15px; box-shadow: 0 8px 15px rgba(0,0,0,0.2); }
.form-container { background-color: #f9f0f0; border-radius: 15px; padding: 20px; max-width: 600px; margin: 0 auto 2rem auto; }
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="Geração Vila", layout="wide", page_icon="🔥")

st.sidebar.title("🔗 Menu")
pagina = st.sidebar.radio("Navegue por aqui", ["🏠 Início", "📆 Eventos", "💡 Sugestões", "🙋‍♀️ Quem Somos"])

def gera_excel_bytes(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Inscrição', index=False)
        workbook = writer.book
        worksheet = writer.sheets['Inscrição']
        for i, col in enumerate(df.columns):
            max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.set_column(i, i, max_len)
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#d72638',
            'font_color': 'white',
            'border': 1})
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
    output.seek(0)
    return output

def enviar_email_anexo(nome, excel_bytes):
    try:
        msg = EmailMessage()
        msg['Subject'] = f'Nova inscrição - Geração Vila: {nome}'
        msg['From'] = EMAIL_REMETENTE
        msg['To'] = EMAIL_DESTINO
        msg.set_content(f'Você recebeu uma nova inscrição do participante: {nome}')

        msg.add_attachment(excel_bytes.read(),
                           maintype='application',
                           subtype='vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                           filename='inscricao_geracao_vila.xlsx')

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_REMETENTE, EMAIL_SENHA_APP)
            smtp.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Erro ao enviar email: {e}")
        return False

if pagina == "🏠 Início":
    st.markdown("<h1>🔥 GERAÇÃO VILA 🔥</h1>", unsafe_allow_html=True)
    st.markdown("<h3>Uma juventude cheia de propósito e presença!</h3>", unsafe_allow_html=True)
    st.markdown("<blockquote>“Ninguém despreze a tua mocidade...” (1Tm 4:12)</blockquote>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    if "mostrar_form" not in st.session_state:
        st.session_state.mostrar_form = False
    if "inscrito" not in st.session_state:
        st.session_state.inscrito = False
    if "dados_inscricao" not in st.session_state:
        st.session_state.dados_inscricao = None
    if "email_enviado" not in st.session_state:
        st.session_state.email_enviado = False

    col1, col2 = st.columns([3, 2])
    with col1:
        st.subheader("🎉 Retiro de Carnaval 2026")
        st.markdown("## \"Nós Precisamos de Avivamento\"")
        st.write("Um tempo de transformação, comunhão e fogo do Espírito! Não fique de fora. Prepare-se!")
        st.info("📍 Local: Sitio Amparo de Deus\n📅 Data: 13 Fevereiro de 2026 à 18 Fevereiro de 2026")

        if not st.session_state.mostrar_form and not st.session_state.inscrito:
            if st.button("Quero Participar!"):
                st.session_state.mostrar_form = True

        if st.session_state.mostrar_form and not st.session_state.inscrito:
            st.markdown('<div class="form-container">', unsafe_allow_html=True)
            st.markdown("### Inscreva-se para participar:")
            with st.form("form_inscricao"):
                nome = st.text_input("Nome Completo")
                idade = st.number_input("Idade", min_value=1, max_value=120, step=1)
                telefone = st.text_input("Telefone (WhatsApp preferencial)")
                igreja = st.text_input("Igreja que frequenta")
                enviar = st.form_submit_button("Enviar inscrição")

                if enviar:
                    if not nome.strip():
                        st.error("Por favor, preencha seu nome.")
                    elif not telefone.strip():
                        st.error("Por favor, preencha seu telefone.")
                    elif not igreja.strip():
                        st.error("Por favor, informe sua igreja.")
                    else:
                        st.session_state.mostrar_form = False
                        st.session_state.inscrito = True
                        st.session_state.email_enviado = False
                        st.session_state.dados_inscricao = {
                            "Nome Completo": nome,
                            "Idade": idade,
                            "Telefone": telefone,
                            "Igreja": igreja
                        }
                        st.success(f"Obrigado pela inscrição, {nome}! 🙌 Entraremos em contato via WhatsApp.")

        if st.session_state.inscrito and st.session_state.dados_inscricao and not st.session_state.email_enviado:
            df_inscricao = pd.DataFrame([st.session_state.dados_inscricao])
            excel_bytes = gera_excel_bytes(df_inscricao)
            enviado = enviar_email_anexo(st.session_state.dados_inscricao["Nome Completo"], excel_bytes)
            if enviado:
                st.success("Sua inscrição foi enviada por e-mail com sucesso! 📧")
                st.session_state.email_enviado = True
            else:
                st.error("Falha ao enviar o e-mail. Por favor, tente novamente mais tarde.")

        if st.session_state.inscrito and st.session_state.email_enviado:
            st.markdown("### Baixe sua inscrição em Excel:")
            df_inscricao = pd.DataFrame([st.session_state.dados_inscricao])
            excel_bytes = gera_excel_bytes(df_inscricao)
            st.download_button(
                label="📥 Baixar Planilha de Inscrição",
                data=excel_bytes,
                file_name="inscricao_geracao_vila.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            st.markdown("Se preferir, faça a inscrição novamente para gerar outra planilha.")

    with col2:
        # Certifique-se de ter a imagem retiro.jpeg na pasta do script
        img = Image.open("retiro.jpeg")
        st.image(img, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<blockquote>“Aviva, ó Senhor, a tua obra no meio dos anos...” (Hc 3:2)</blockquote>", unsafe_allow_html=True)

elif pagina == "📆 Eventos":
    st.markdown("<h2>📅 Próximos Encontros da Juventude</h2>", unsafe_allow_html=True)
    eventos = [
        {"nome": "Festa da Amizade ICNV Lote XV", "data": "16/08/2025"},
        {"nome": "Culto GA Local", "data": "30/08/2025"},
    ]
    for evento in eventos:
        st.markdown(f"""
        <div class="event-card">
            <strong>{evento['nome']}</strong><br>
            📅 <i>{evento['data']}</i>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("<blockquote>“Como é bom e agradável viverem unidos os irmãos...” (Sl 133:1)</blockquote>", unsafe_allow_html=True)

elif pagina == "💡 Sugestões":
    st.markdown("<h2>💡 Tem uma ideia? Conta pra gente!</h2>", unsafe_allow_html=True)
    with st.form("sugestao_form"):
        nome = st.text_input("Seu nome")
        sugestao = st.text_area("Escreva sua sugestão aqui")
        enviar = st.form_submit_button("Enviar")
        if enviar and sugestao:
            st.success(f"Obrigado pela sugestão, {nome if nome else 'anônimo'}! 🙌")
    st.markdown("<blockquote>“Grandes coisas fez o Senhor por nós...” (Sl 126:3)</blockquote>", unsafe_allow_html=True)

elif pagina == "🙋‍♀️ Quem Somos":
    st.markdown("<h2>🙋‍♀️ Quem Somos</h2>", unsafe_allow_html=True)
    st.write("""
Somos o **grupo de jovens da Baixada Fluminense**, uma geração vibrante e comprometida com a missão de alcançar vidas para a glória de Deus. Nosso foco é viver o evangelho com paixão, comunhão e transformação, sendo luz e sal na nossa comunidade.

🔹 Amamos a Palavra  
🔹 Nos reunimos com propósito  
🔹 Servimos com alegria  
🔹 Buscamos o Espírito Santo  
🔹 Somos ousados em fé!

Seja bem-vindo(a) a essa família cheia do fogo de Deus! ❤️‍🔥
    """)
    st.markdown("<blockquote>“Mas vós sois geração eleita, sacerdócio real...” (1Pe 2:9)</blockquote>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; font-size: 0.9em; color: gray;'>
    © 2025 Geração Vila • Feito com ❤️ e propósito
</div>
""", unsafe_allow_html=True)
