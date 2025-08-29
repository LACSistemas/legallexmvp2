import streamlit as st
from auth import AuthSystem
from datetime import datetime, timedelta
import pytz
import os
import glob
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/app.log'),
        logging.StreamHandler()
    ]
)

def show_logo():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image("legallexmvplogo.png", width=150)
        except:
            st.markdown("## ⚖️ LegalLex")

def admin_page():
    logging.info("Admin page accessed")
    show_logo()
    st.title("📤 Upload Análises Inteligentes")
    st.markdown("---")
    
    # Logout button
    if st.button("🚪 Sair", key="admin_logout"):
        AuthSystem.logout()
    
    st.markdown("### Enviar Análises Inteligentes")
    st.markdown("Faça upload de arquivos HTML com análises jurídicas que serão disponibilizadas aos clientes.")
    
    uploaded_files = st.file_uploader(
        "Selecione os arquivos HTML",
        type=['html'],
        accept_multiple_files=True,
        key="analysis_upload"
    )
    
    if uploaded_files:
        if st.button("📤 Enviar Análises", type="primary"):
            saved_count = 0
            
            # Create analyses directory if it doesn't exist
            os.makedirs("analyses", exist_ok=True)
            
            for uploaded_file in uploaded_files:
                try:
                    # Generate unique filename with timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    original_name = uploaded_file.name.replace('.html', '')
                    filename = f"analyses/{timestamp}_{original_name}.html"
                    
                    # Save file
                    with open(filename, 'wb') as f:
                        f.write(uploaded_file.getbuffer())
                    
                    logging.info(f"Analysis file uploaded: {filename}")
                    saved_count += 1
                except Exception as e:
                    logging.error(f"Error uploading file {uploaded_file.name}: {str(e)}")
                    st.error(f"Erro ao enviar {uploaded_file.name}: {str(e)}")
            
            st.success(f"✅ {saved_count} análise(s) enviada(s) com sucesso!")
    
    # Show existing analyses count and management
    existing_analyses = sorted(glob.glob("analyses/*.html"), key=os.path.getmtime, reverse=True)
    st.info(f"📊 Total de análises disponíveis: {len(existing_analyses)}")
    
    # Analysis management section
    if existing_analyses:
        st.markdown("### 🗂️ Gerenciar Análises Existentes")
        
        # Show list of analyses with delete buttons
        for analysis_path in existing_analyses[:10]:  # Show only latest 10
            filename = os.path.basename(analysis_path)
            readable_name = filename.replace('.html', '').replace('_', ' - ', 1)
            mod_time = datetime.fromtimestamp(os.path.getmtime(analysis_path))
            
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{readable_name}**")
                st.markdown(f"*Criado: {mod_time.strftime('%d/%m/%Y às %H:%M')}*")
            
            with col2:
                if st.button("🗑️ Deletar", key=f"delete_{filename}"):
                    try:
                        os.remove(analysis_path)
                        logging.info(f"Analysis file deleted: {analysis_path}")
                        st.success(f"✅ Arquivo deletado: {readable_name}")
                        st.rerun()
                    except Exception as e:
                        logging.error(f"Error deleting file {analysis_path}: {str(e)}")
                        st.error(f"❌ Erro ao deletar arquivo: {str(e)}")
            
            st.markdown("---")
        
        # Show total count if more than 10
        if len(existing_analyses) > 10:
            st.info(f"Mostrando 10 de {len(existing_analyses)} análises. Os demais podem ser gerenciados via sistema de arquivos.")

def client_dashboard():
    logging.info("Client dashboard accessed")
    # Logo in sidebar (centered)
    with st.sidebar:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            try:
                st.image("legallexmvplogo.png", width=100)
            except Exception as e:
                logging.warning(f"Logo not found: {str(e)}")
                st.markdown("### ⚖️ LegalLex")
    
    # Navigation
    st.sidebar.title("🧭 Navegação")
    
    # Logout button in sidebar
    if st.sidebar.button("🚪 Sair"):
        AuthSystem.logout()
    
    page = st.sidebar.radio(
        "Selecione uma página:",
        ["⚙️ Configurar Regras", "📋 Resultados Diários", "🔍 Análises Inteligentes"]
    )
    
    logging.info(f"Client navigated to page: {page}")
    
    if page == "⚙️ Configurar Regras":
        show_rules_config()
    elif page == "📋 Resultados Diários":
        show_daily_results()
    else:
        show_analyses_page()

def show_rules_config():
    st.title("⚙️ Configuração de Regras Automáticas")
    st.markdown("---")
    
    # Show next execution time
    brasilia_tz = pytz.timezone('America/Sao_Paulo')
    tomorrow_6am = datetime.now(brasilia_tz).replace(hour=6, minute=0, second=0, microsecond=0) + timedelta(days=1)
    
    st.info(f"⏰ **Próxima execução automática:** {tomorrow_6am.strftime('%d/%m/%Y às %H:%M')} (Brasília)")
    st.markdown("As regras configuradas abaixo serão executadas automaticamente todos os dias às 6:00 da manhã.")
    
    # Import the rule configuration from the original system
    from djesearchapp import create_rule_form, SearchRule, ExclusionRule
    
    # Initialize session state for rules with hardcoded defaults
    if 'auto_rules' not in st.session_state:
        # Create default hardcoded rules
        from djesearchapp import SearchRule
        
        default_rules = [
            SearchRule(
                name="OAB Principal",
                enabled=True,
                parameters={
                    'numeroOab': '8773', 
                    'ufOab': 'ES',
                    'dataDisponibilizacaoInicio': datetime.now().strftime('%Y-%m-%d')
                }
            ),
            SearchRule(
                name="Darwin",
                enabled=True,
                parameters={
                    'nomeParte': 'Darwin', 
                    'siglaOrgaoJulgador': 'TJES',
                    'dataDisponibilizacaoInicio': datetime.now().strftime('%Y-%m-%d')
                }
            ),
            SearchRule(
                name="Sinales",
                enabled=True,
                parameters={
                    'nomeParte': 'SINALES SINALIZAÇÃO ESPÍRITO SANTO LTDA',
                    'dataDisponibilizacaoInicio': datetime.now().strftime('%Y-%m-%d')
                },
                exclusions=[
                    ExclusionRule(
                        name="Excluir OAB 014072 ES",
                        field="numeroOab",
                        value="014072",
                        enabled=True
                    )
                ]
            ),
            SearchRule(
                name="Multivix",
                enabled=True,
                parameters={
                    'nomeParte': 'Multivix',
                    'dataDisponibilizacaoInicio': datetime.now().strftime('%Y-%m-%d')
                }
            ),
            SearchRule(
                name="CENTRO UNIVERSITÁRIO CLARETIANO",
                enabled=True,
                parameters={
                    'nomeParte': 'Claretiano',
                    'dataDisponibilizacaoInicio': datetime.now().strftime('%Y-%m-%d')
                }
            )
        ]
        
        # Load additional saved rules from file and append them
        try:
            from cronjob_scheduler import CronJobScheduler
            scheduler = CronJobScheduler()
            saved_custom_rules = scheduler.load_saved_rules()
            # Combine default rules with any custom saved rules
            all_rules = default_rules + saved_custom_rules
            st.session_state.auto_rules = all_rules
            logging.info(f"Loaded {len(default_rules)} default rules + {len(saved_custom_rules)} custom rules")
        except Exception as e:
            logging.warning(f"Could not load custom rules, using defaults only: {str(e)}")
            st.session_state.auto_rules = default_rules
    
    # Rule management buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("➕ Adicionar Regra"):
            st.session_state.auto_rules.append(None)
            st.rerun()
    
    with col2:
        if st.button("🗑️ Limpar Regras"):
            st.session_state.auto_rules = []
            st.rerun()
    
    with col3:
        if st.button("💾 Salvar Regras"):
            # Save rules using CronJobScheduler
            try:
                from cronjob_scheduler import CronJobScheduler
                scheduler = CronJobScheduler()
                
                # Get configured rules from session state
                rules_to_save = []
                for i in range(len(st.session_state.auto_rules)):
                    rule = st.session_state.auto_rules[i]
                    if rule:  # Only save non-None rules
                        rules_to_save.append(rule)
                
                # Save rules to file
                scheduler.save_rules(rules_to_save)
                
                logging.info(f"Successfully saved {len(rules_to_save)} rules to file")
                st.success(f"✅ {len(rules_to_save)} regra(s) salva(s)! Serão executadas automaticamente às 6:00 da manhã.")
                
            except Exception as e:
                logging.error(f"Error saving rules: {str(e)}")
                st.error(f"❌ Erro ao salvar regras: {str(e)}")
    
    # Rule configuration forms
    configured_rules = []
    for i in range(len(st.session_state.auto_rules)):
        existing_rule = st.session_state.auto_rules[i]
        rule = create_rule_form(i, existing_rule)
        if rule:
            configured_rules.append(rule)
    
    # Update rules in session state
    st.session_state.auto_rules = configured_rules
    
    # Display rule summary
    if configured_rules:
        st.markdown("## 📋 Resumo das Regras Configuradas")
        for rule in configured_rules:
            status = "✅ Ativa" if rule.enabled else "❌ Inativa"
            params_text = []
            for key, value in rule.parameters.items():
                if key != '_rule_name':
                    params_text.append(f"{key}: {value}")
            
            st.markdown(f"""
            <div style="border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin: 10px 0; background-color: #f9f9f9; border-left: 4px solid #28a745;">
                <strong>{rule.name}</strong> - {status}<br>
                <small>Parâmetros: {', '.join(params_text) if params_text else 'Nenhum'}</small><br>
                <small>Exclusões: {len(rule.exclusions) if hasattr(rule, 'exclusions') and rule.exclusions else 0}</small>
            </div>
            """, unsafe_allow_html=True)

def show_daily_results():
    st.title("📋 Resultados das Buscas Automáticas")
    st.markdown("---")
    
    st.info("📅 Esta página mostra os resultados das buscas executadas automaticamente às 6:00 da manhã baseadas nas suas regras configuradas.")
    
    # Date selector for viewing results
    selected_date = st.date_input(
        "Selecione a data dos resultados:",
        value=datetime.now().date()
    )
    
    # Mock results for now - in production this would load from database
    st.markdown(f"### Resultados de {selected_date.strftime('%d/%m/%Y')}")
    
    # Check if we have stored results for this date
    publications = None
    
    # First, try to load from database for the selected date
    try:
        from database import DatabaseManager
        
        db = DatabaseManager()
        date_str = selected_date.strftime('%d/%m/%Y')
        
        # Get publications from database
        publications = db.get_publications_by_date(date_str)
        if publications:
            logging.info(f"Loaded {len(publications)} publications from database for {date_str}")
            
    except Exception as e:
        logging.error(f"Error loading results from database for {selected_date}: {str(e)}")
    
    # Fallback to session state if no file found and date matches today
    if not publications and 'last_auto_search_results' in st.session_state and 'last_search_date' in st.session_state:
        if st.session_state.last_search_date.date() == selected_date:
            publications = st.session_state.last_auto_search_results
            logging.info(f"Using session state results for {selected_date}")
    
    # If we have publications, display them
    if publications:
        from djesearchapp import display_publication_card
        import math
        
        # Pagination
        items_per_page = 10
        total_items = len(publications)
        total_pages = math.ceil(total_items / items_per_page) if total_items > 0 else 1
        
        if total_pages > 1:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                page = st.selectbox("Página", range(1, total_pages + 1))
        else:
            page = 1
        
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        current_items = publications[start_idx:end_idx]
        
        st.info(f"📊 Mostrando {len(current_items)} de {total_items} publicações encontradas")
        
        for i, pub in enumerate(current_items):
            display_publication_card(pub, start_idx + i)
        
        # Excel download button
        st.markdown("---")
        st.markdown("## 📊 Exportar Resultados")
        if st.button("📋 Baixar em Excel"):
            try:
                import pandas as pd
                from io import BytesIO
                
                # Prepare data for Excel
                excel_data = []
                for pub in publications:
                    # Extract destinatarios (nome and polo are inside destinatarios array)
                    destinatarios = pub.get('destinatarios', [])
                    destinatarios_text = '; '.join([
                        f"{dest.get('nome', '')} ({dest.get('polo', '')})" 
                        for dest in destinatarios
                    ]) if destinatarios else ''
                    
                    # Extract advogados
                    advogados = pub.get('destinatarioadvogados', [])
                    advogados_text = '; '.join([
                        f"{adv.get('advogado', {}).get('nome', '')} - OAB {adv.get('advogado', {}).get('numero_oab', '')} {adv.get('advogado', {}).get('uf_oab', '')}"
                        for adv in advogados
                    ]) if advogados else ''
                    
                    # Extract correct fields for Excel - each publicação becomes one row
                    row = {
                        'data_disponibilizacao': pub.get('data_disponibilizacao', ''),
                        'sigla_tribunal': pub.get('siglaTribunal', ''),
                        'tipo_comunicacao': pub.get('tipoComunicacao', ''),
                        'nome_orgao': pub.get('nomeOrgao', ''),
                        'texto': pub.get('texto', ''),
                        'numero_processo': pub.get('numeroprocessocommascara', ''),
                        'numero_processo_simples': pub.get('numero_processo', ''),
                        'meio': pub.get('meio', ''),
                        'link': pub.get('link', ''),
                        'tipo_documento': pub.get('tipoDocumento', ''),
                        'nome_classe': pub.get('nomeClasse', ''),
                        'codigo_classe': pub.get('codigoClasse', ''),
                        'destinatarios': destinatarios_text,
                        'advogados': advogados_text,
                        'hash': pub.get('hash', ''),
                        'data_disponibilizacao_alt': pub.get('datadisponibilizacao', ''),
                        'fonte_regra': pub.get('_source_rule', '')
                    }
                    excel_data.append(row)
                
                # Create DataFrame
                df = pd.DataFrame(excel_data)
                
                # Create Excel file in memory
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Publicações')
                
                # Get the Excel data
                excel_bytes = output.getvalue()
                
                # Generate filename with date
                brasilia_tz = pytz.timezone('America/Sao_Paulo')
                date_str = selected_date.strftime('%d-%m-%Y')
                filename = f"Busca_do_dia_{date_str}.xlsx"
                
                st.download_button(
                    label="💾 Download Excel",
                    data=excel_bytes,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_excel"
                )
                
            except Exception as e:
                logging.error(f"Error creating Excel file: {str(e)}")
                st.error(f"❌ Erro ao criar arquivo Excel: {str(e)}")
        else:
            st.warning("⚠️ Nenhum resultado encontrado para esta data.")
    else:
        st.warning("⚠️ Nenhum resultado encontrado para esta data.")
    
    # Debug database info
    try:
        from database import DatabaseManager
        db = DatabaseManager()
        search_history = db.get_search_history(limit=10)
        if search_history:
            st.info(f"📊 Database conectada! Últimas {len(search_history)} buscas encontradas.")
            with st.expander("Ver histórico de buscas"):
                for search in search_history:
                    st.write(f"• {search['name']} - {search['date']} ({search['publications_found']} publicações)")
        else:
            st.warning("⚠️ Database conectada mas nenhuma busca encontrada.")
    except Exception as e:
        st.error(f"❌ Erro na database: {str(e)}")
        logging.error(f"Database debug error: {str(e)}")

    # Manual execution button (for testing)
    if st.button("🔍 Executar Busca Manual (Teste)", type="secondary"):
        if 'auto_rules' in st.session_state and st.session_state.auto_rules:
            from djesearchapp import OptimizedDJESearcher
            
            searcher = OptimizedDJESearcher()
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            def update_progress(message):
                status_text.markdown(f'🔍 {message}')
            
            try:
                logging.info(f"Manual search started with {len(st.session_state.auto_rules)} rules")
                publications, stats = searcher.execute_rules(st.session_state.auto_rules, update_progress)
                progress_bar.progress(100)
                status_text.success(f"✅ Busca concluída! {len(publications)} publicações encontradas.")
                
                logging.info(f"Manual search completed: {len(publications)} publications found, stats: {stats}")
                
                # Store results in session state
                st.session_state.last_auto_search_results = publications
                st.session_state.last_search_date = datetime.now()
                
                # Save results to database
                try:
                    from database import DatabaseManager
                    
                    # Create database manager instance
                    db = DatabaseManager()
                    
                    # Create filename with today's date
                    brasilia_tz = pytz.timezone('America/Sao_Paulo')
                    brasilia_now = datetime.now(brasilia_tz)
                    date_str = brasilia_now.strftime('%d/%m/%Y')
                    filename = f"Busca do dia {date_str}"
                    
                    # Save to database
                    search_execution_id = db.save_search_execution(
                        name=filename,
                        date=date_str,
                        timestamp=brasilia_now,
                        rules_executed=len(st.session_state.auto_rules),
                        publications=publications,
                        stats=stats
                    )
                    
                    logging.info(f"Manual search results saved to database with ID {search_execution_id}")
                    status_text.success(f"✅ Busca concluída e salva como '{filename}'! {len(publications)} publicações encontradas.")
                    
                    # Debug: verify it was saved
                    verify_pubs = db.get_publications_by_date(date_str)
                    st.info(f"🔍 Debug: Verificação - {len(verify_pubs)} publicações salvas para {date_str}")
                    
                except Exception as e:
                    logging.error(f"Error saving manual search results to database: {str(e)}")
                    # Don't show error to user, just log it
                
                st.rerun()
                
            except Exception as e:
                logging.error(f"Error during manual search: {str(e)}")
                st.error(f"❌ Erro durante a busca: {str(e)}")
        else:
            st.warning("⚠️ Configure as regras primeiro na página 'Configurar Regras'.")

def show_analyses_page():
    st.title("🔍 Análises Inteligentes")
    st.markdown("---")
    
    st.markdown("### Análises Jurídicas Especializadas")
    st.markdown("Aqui você encontra análises detalhadas por IA dos casos jurídicos de Educação (Configurado pelo Darwin e Multivix), Será automaticamente renovada diariamente as 06 da manhã.")
    
    # Get all analysis files
    analysis_files = sorted(glob.glob("analyses/*.html"), key=os.path.getmtime, reverse=True)
    
    if not analysis_files:
        st.info("📄 Nenhuma análise disponível no momento. Novas análises são adicionadas diariamente.")
        return
    
    # Pagination
    items_per_page = 10
    total_items = len(analysis_files)
    total_pages = (total_items + items_per_page - 1) // items_per_page
    
    if total_pages > 1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            page = st.selectbox("Página", range(1, total_pages + 1), key="analyses_page")
    else:
        page = 1
    
    start_idx = (page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)
    current_files = analysis_files[start_idx:end_idx]
    
    st.info(f"📊 Mostrando {len(current_files)} de {total_items} análises (Página {page} de {total_pages})")
    
    # Display analyses
    for i, file_path in enumerate(current_files):
        filename = os.path.basename(file_path)
        # Extract readable name from filename
        readable_name = filename.replace('.html', '').replace('_', ' - ', 1)
        
        # Get file modification time
        mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        
        with st.expander(f"📄 {readable_name}", expanded=False):
            st.markdown(f"**Data:** {mod_time.strftime('%d/%m/%Y às %H:%M')}")
            
            # Read and display HTML content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                # Display HTML content in an iframe-like container
                st.components.v1.html(html_content, height=600, scrolling=True)
                
            except Exception as e:
                st.error(f"Erro ao carregar análise: {str(e)}")

def main():
    try:
        logging.info("Application started")
        
        # Check authentication first
        if not AuthSystem.check_authentication():
            logging.info("User not authenticated, showing login page")
            return
        
        # Get current user
        user = AuthSystem.get_current_user()
        logging.info(f"User authenticated: {user['username']} with role: {user['role']}")
        
        if user["role"] == "admin":
            admin_page()
        else:  # client
            client_dashboard()
            
    except Exception as e:
        logging.error(f"Critical error in main application: {str(e)}")
        st.error(f"❌ Erro crítico na aplicação: {str(e)}")
        st.info("Por favor, recarregue a página ou contate o suporte.")

if __name__ == "__main__":
    main()