import streamlit as st
from openai import OpenAI
import pandas as pd
import os
from dotenv import load_dotenv
from datetime import datetime
import json

# =============================
# CONFIG
# =============================

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("❌ OPENAI_API_KEY não configurada!")
    st.stop()

client = OpenAI(api_key=api_key)

st.set_page_config(
    page_title="Editais IFSC - Agente de Fomento",
    page_icon="📋",
    layout="wide"
)

# =============================
# CSS
# =============================

st.markdown("""
<style>
.header-logo {
    text-align: center;
    margin-bottom: 30px;
}

.presentation-box {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 10px;
    margin: 20px 0;
}

.edital-card {
    background: white;
    padding: 15px;
    border-radius: 8px;
    border-left: 4px solid #667eea;
    margin: 10px 0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.status-aberto {
    background: #c8e6c9;
    color: #2e7d32;
    padding: 5px 10px;
    border-radius: 5px;
    font-weight: bold;
}

.status-fechado {
    background: #ffcdd2;
    color: #c62828;
    padding: 5px 10px;
    border-radius: 5px;
    font-weight: bold;
}

.footer-box {
    background: #f5f5f5;
    padding: 15px;
    border-radius: 8px;
    margin-top: 30px;
    font-size: 12px;
    line-height: 1.6;
}

h1, h2, h3 {
    color: #667eea;
}
</style>
""", unsafe_allow_html=True)

# =============================
# DATABASE & CACHE
# =============================

def load_editais_csv():
    """Carrega editais do CSV"""
    try:
        df = pd.read_csv("editais_resultados.csv")
        return df
    except:
        return pd.DataFrame()

def save_editais_csv(data):
    """Salva editais em CSV"""
    try:
        df = pd.DataFrame(data)
        df.to_csv("editais_resultados.csv", index=False, encoding='utf-8')
        return True
    except Exception as e:
        st.error(f"Erro ao salvar CSV: {e}")
        return False

# =============================
# IA AGENT
# =============================

def agent_buscar_editais(tema_pesquisa: str, areas_interesse: str):
    """Agente IA que busca editais de fomento"""
    
    prompt = f"""
Você é um especialista em Editais de Fomento do Brasil. 
Sua missão é identificar oportunidades de financiamento para pesquisadores do IFSC.

CONTEXTO:
- Tema de Pesquisa: {tema_pesquisa}
- Áreas de Interesse: {areas_interesse}
- Instituição: IFSC (Instituto Federal de Santa Catarina)

TAREFA:
1. Busque mentalmente pelos principais editais abertos em 2026 das agências:
   - CNPq
   - CAPES
   - FINEP
   - Fundações estaduais
   - Agências internacionais

2. Para cada edital relevante, forneça:
   - Nome do Edital
   - Agência responsável
   - Objetivo
   - Elegibilidade (se aplica a IFSC)
   - Tipo de Fomento
   - Recursos financeiros estimados
   - Prazo de inscrição
   - Plataforma de submissão
   - Link/Contato
   - Alinhamento com tema pesquisado (%)

3. Classifique por relevância (Alta, Média, Baixa)

4. Retorne APENAS em JSON válido, sem markdown:
{{
    "editais": [
        {{
            "edital": "Nome",
            "agencia": "Agência",
            "objetivo": "Descrição",
            "elegibilidade": "Requisitos",
            "tipo_fomento": "Tipo",
            "recursos": "Valor",
            "prazo": "Data",
            "plataforma": "Plataforma",
            "link": "URL",
            "alinhamento": 85,
            "relevancia": "Alta",
            "justificativa": "Por que é relevante"
        }}
    ],
    "total_encontrados": 5,
    "recomendacoes": "Recomendações gerais"
}}
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=2000
        )
        
        content = response.choices[0].message.content.strip()
        
        # Limpar markdown
        if "```json" in content:
            content = content.replace("```json", "").replace("```", "").strip()
        elif "```" in content:
            content = content.replace("```", "").strip()
        
        data = json.loads(content)
        return data
    
    except Exception as e:
        st.error(f"Erro na busca: {e}")
        return None

# =============================
# MAIN APP
# =============================

def main():
    # Header com logo
    st.markdown("""
    <div class='header-logo'>
    <h1>📋 Agente de Busca de Editais de Fomento</h1>
    <p><b>Instituto Federal de Santa Catarina - IFSC</b></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Apresentação
    st.markdown("""
    <div class='presentation-box'>
    <h3>📧 Prezados Coordenadores de Pesquisa e Inovação dos Câmpus</h3>
    <h3>Prezados Docentes</h3>
    
    <p>Você está recebendo este contato pois identificamos que sua formação ou produção científica 
    poderia se alinhar com oportunidades de fomento à pesquisa.</p>
    
    <p><b>Mantenha seu LATTES sempre atualizado!</b></p>
    
    <p>A partir da seleção de Editais lançados pelas Agências e demais organizações de financiamento 
    de projetos, identificamos as oportunidades abaixo como propícias para participação dos Servidores do IFSC.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Sidebar - Configurações
    st.sidebar.title("⚙️ Configuração da Busca")
    
    tema_pesquisa = st.sidebar.text_input(
        "Tema de Pesquisa",
        value="Tecnologia, Inovação, Educação",
        help="Digite seu tema principal de pesquisa"
    )
    
    areas_interesse = st.sidebar.text_area(
        "Áreas de Interesse",
        value="Engenharia de Software, Sustentabilidade, Tecnologia Social",
        help="Lista de áreas de interesse separadas por vírgula"
    )
    
    agencias_selecionadas = st.sidebar.multiselect(
        "Agências",
        ["CNPq", "CAPES", "FINEP", "Fundações Estaduais", "Agências Internacionais"],
        default=["CNPq", "CAPES", "FINEP"]
    )
    
    # Abas
    tab1, tab2, tab3 = st.tabs(["🔍 Buscar Editais", "📊 Resultados", "📥 Download"])
    
    # =============================
    # TAB 1: BUSCAR
    # =============================
    
    with tab1:
        st.subheader("🔍 Busca Inteligente de Editais")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.write(f"**Tema:** {tema_pesquisa}")
            st.write(f"**Áreas:** {areas_interesse}")
            st.write(f"**Agências:** {', '.join(agencias_selecionadas)}")
        
        with col2:
            if st.button("🚀 Buscar Editais", key="btn_buscar", use_container_width=True):
                with st.spinner("🤖 Agente analisando editais..."):
                    result = agent_buscar_editais(tema_pesquisa, areas_interesse)
                    
                    if result:
                        st.session_state.editais_resultado = result
                        st.session_state.data_busca = datetime.now().strftime("%d/%m/%Y %H:%M")
                        st.success(f"✅ {result.get('total_encontrados', 0)} editais encontrados!")
                    else:
                        st.error("❌ Erro na busca")
    
    # =============================
    # TAB 2: RESULTADOS
    # =============================
    
    with tab2:
        st.subheader("📊 Editais Encontrados")
        
        if "editais_resultado" in st.session_state:
            result = st.session_state.editais_resultado
            
            st.info(f"📅 Busca realizada em: {st.session_state.get('data_busca', 'N/A')}")
            st.write(f"**Total de Editais:** {result.get('total_encontrados', 0)}")
            
            # Filtros
            col1, col2 = st.columns([1, 1])
            
            with col1:
                filtro_relevancia = st.selectbox(
                    "Filtrar por Relevância",
                    ["Todos", "Alta", "Média", "Baixa"]
                )
            
            with col2:
                ordenar_por = st.selectbox(
                    "Ordenar por",
                    ["Alinhamento", "Prazo", "Recursos"]
                )
            
            st.divider()
            
            # Exibir editais
            editais = result.get('editais', [])
            
            if filtro_relevancia != "Todos":
                editais = [e for e in editais if e.get('relevancia') == filtro_relevancia]
            
            if ordenar_por == "Alinhamento":
                editais = sorted(editais, key=lambda x: x.get('alinhamento', 0), reverse=True)
            elif ordenar_por == "Prazo":
                editais = sorted(editais, key=lambda x: x.get('prazo', ''))
            
            for idx, edital in enumerate(editais, 1):
                with st.container(border=False):
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.markdown(f"### {idx}. {edital.get('edital', 'N/A')}")
                    
                    with col2:
                        relevancia = edital.get('relevancia', 'Média')
                        if relevancia == "Alta":
                            st.markdown(f"<span class='status-aberto'>⭐ {relevancia}</span>", 
                                      unsafe_allow_html=True)
                        else:
                            st.markdown(f"<span class='status-fechado'>●  {relevancia}</span>", 
                                      unsafe_allow_html=True)
                    
                    with col3:
                        st.metric("Alinhamento", f"{edital.get('alinhamento', 0)}%")
                    
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.write(f"**Agência:** {edital.get('agencia', 'N/A')}")
                        st.write(f"**Objetivo:** {edital.get('objetivo', 'N/A')}")
                        st.write(f"**Elegibilidade:** {edital.get('elegibilidade', 'N/A')}")
                    
                    with col2:
                        st.write(f"**Tipo:** {edital.get('tipo_fomento', 'N/A')}")
                        st.write(f"**Recursos:** {edital.get('recursos', 'N/A')}")
                        st.write(f"**Prazo:** {edital.get('prazo', 'N/A')}")
                    
                    st.write(f"**Plataforma:** {edital.get('plataforma', 'N/A')}")
                    st.write(f"**Link:** {edital.get('link', 'N/A')}")
                    st.write(f"**Justificativa:** {edital.get('justificativa', 'N/A')}")
                    
                    st.divider()
            
            # Recomendações
            if result.get('recomendacoes'):
                st.write("### 💡 Recomendações")
                st.info(result.get('recomendacoes'))
        
        else:
            st.info("👈 Utilize a aba 'Buscar Editais' para iniciar uma pesquisa")
    
    # =============================
    # TAB 3: DOWNLOAD
    # =============================
    
    with tab3:
        st.subheader("📥 Exportar Resultados")
        
        if "editais_resultado" in st.session_state:
            result = st.session_state.editais_resultado
            editais = result.get('editais', [])
            
            if editais:
                df = pd.DataFrame(editais)
                
                # Download CSV
                csv = df.to_csv(index=False, encoding='utf-8')
                st.download_button(
                    label="📥 Baixar CSV",
                    data=csv,
                    file_name=f"editais_fomento_{datetime.now().strftime('%d%m%Y_%H%M%S')}.csv",
                    mime="text/csv"
                )
                
                # Download Excel
                try:
                    import io
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False)
                    buffer.seek(0)
                    
                    st.download_button(
                        label="📥 Baixar Excel",
                        data=buffer,
                        file_name=f"editais_fomento_{datetime.now().strftime('%d%m%Y_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                except:
                    st.info("Excel não disponível. Use CSV.")
                
                # Preview
                st.write("### Preview dos Dados")
                st.dataframe(df, use_container_width=True, height=400)
            
            else:
                st.info("Sem resultados para exportar")
        
        else:
            st.info("👈 Busque editais primeiro")
    
    # =============================
    # FOOTER
    # =============================
    
    st.divider()
    
    st.markdown("""
    <div class='footer-box'>
    <h4>ℹ️ Próximas Etapas</h4>
    
    <p><b>Ademais, solicitamos que nos informe quando efetivar a inscrição e de sua aprovação, caso haja.</b> 
    Assim podemos atualizar nossas estatísticas acerca destes importantes Indicadores da PROPPI.</p>
    
    <h4>📋 Processos Administrativos</h4>
    
    <p><b>Carta de Anuência:</b> 
    <a href="http://cpn.ifsc.edu.br/bpm/PROPPI/#diagram/58dcb896-75d6-49eb-b490-d05b974f283b" target="_blank">
    Acesse aqui</a></p>
    
    <p><b>Termo de Outorga:</b> 
    <a href="http://cpn.ifsc.edu.br/bpm/PROPPI/#diagram/b35eb9c3-891a-4ece-b832-5a2fb3a1f07b" target="_blank">
    Acesse aqui</a></p>
    
    <h4>💻 Sistema STELA EXPERTA</h4>
    
    <p>Todos podem solicitar a criação de uma conta de usuário para ter acesso ao Sistema Stela Experta. 
    Basta enviar um email para <b>inovacao@ifsc.edu.br</b> informando:</p>
    <ul>
    <li>Nome completo</li>
    <li>Email institucional</li>
    </ul>
    
    <h4>⚠️ IMPORTANTE</h4>
    
    <p>Vários pesquisadores ficam de fora destas listas de busca porque seus currículos Lattes não contêm 
    informações imprescindíveis, tais como:</p>
    <ul>
    <li>Área de formação</li>
    <li>Área da titulação máxima</li>
    <li>Área de conhecimento da produção científica</li>
    </ul>
    
    <p><b>MANTENHA SEMPRE ATUALIZADO SEU CURRÍCULO LATTES!</b></p>
    
    <hr>
    <p style='text-align: center; font-size: 10px; color: #666;'>
    Sistema de Busca de Editais de Fomento - IFSC | Powered by OpenAI
    </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
