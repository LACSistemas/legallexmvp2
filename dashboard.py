"""
Dashboard Interactive - LegalLex MVP2
Interactive dashboard for visualizing legal publication insights and analytics
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta, date
import logging
from database import DatabaseManager

# Page configuration
st.set_page_config(
    page_title="Dashboard - LegalLex MVP2",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def show_logo():
    """Display LegalLex logo"""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image("legallexmvplogo.png", width=120)
        except:
            st.markdown("### 📊 LegalLex Dashboard")

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_dashboard_data(start_date: str, end_date: str, selected_tribunals: list = None):
    """Get cached dashboard data"""
    db = DatabaseManager()
    
    # Get publications in date range
    publications = db.get_publications_by_date_range(start_date, end_date, selected_tribunals)
    
    # Get search executions
    search_executions = db.get_search_executions_by_date_range(start_date, end_date)
    
    # Get analyses coverage
    analyses = db.get_analyses_by_date_range(start_date, end_date)
    
    return publications, search_executions, analyses

def create_kpi_cards(publications: list, search_executions: list, analyses: list):
    """Create KPI cards section"""
    
    # Calculate metrics
    total_publications = len(publications)
    active_tribunals = len(set([pub.get('siglaTribunal', 'N/A') for pub in publications if pub.get('siglaTribunal')]))
    unique_lawyers = len(set([adv.get('numeroOab', 'N/A') for pub in publications for adv in pub.get('advogados', []) if adv.get('numeroOab')]))
    total_analyses = len(analyses)
    
    # Display KPIs in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📈 Total Publicações",
            value=f"{total_publications:,}",
            delta=f"Período selecionado"
        )
    
    with col2:
        st.metric(
            label="🏛️ Tribunais Ativos", 
            value=f"{active_tribunals}",
            delta=f"Jurisdições"
        )
    
    with col3:
        st.metric(
            label="⚖️ Advogados Únicos",
            value=f"{unique_lawyers:,}",
            delta=f"Profissionais"
        )
    
    with col4:
        analysis_coverage = (total_analyses / total_publications * 100) if total_publications > 0 else 0
        st.metric(
            label="🧠 Análises Criadas",
            value=f"{total_analyses}",
            delta=f"{analysis_coverage:.1f}% cobertura"
        )

def create_publications_timeline_chart(publications: list):
    """Create publications by date line chart"""
    if not publications:
        st.warning("Nenhuma publicação encontrada no período selecionado")
        return
    
    # Process data for timeline
    df = pd.DataFrame(publications)
    df['date'] = pd.to_datetime(df['datadisponibilizacao'], format='%d/%m/%Y', errors='coerce')
    
    # Group by date
    timeline_data = df.groupby(df['date'].dt.date).size().reset_index()
    timeline_data.columns = ['Data', 'Publicações']
    
    # Create line chart
    fig = px.line(
        timeline_data, 
        x='Data', 
        y='Publicações',
        title='📅 Publicações por Data',
        markers=True
    )
    
    fig.update_layout(
        height=400,
        showlegend=False,
        xaxis_title="Data",
        yaxis_title="Número de Publicações"
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_tribunals_chart(publications: list):
    """Create top tribunals bar chart"""
    if not publications:
        return
    
    # Process tribunal data
    tribunals = [pub.get('siglaTribunal', 'N/A') for pub in publications if pub.get('siglaTribunal')]
    tribunal_counts = pd.Series(tribunals).value_counts().head(10)
    
    # Create bar chart
    fig = px.bar(
        x=tribunal_counts.values,
        y=tribunal_counts.index,
        orientation='h',
        title='🏛️ Top 10 Tribunais por Volume',
        labels={'x': 'Número de Publicações', 'y': 'Tribunal'}
    )
    
    fig.update_layout(
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_communication_types_pie(publications: list):
    """Create communication types pie chart"""
    if not publications:
        return
    
    # Process communication types
    comm_types = [pub.get('tipoComunicacao', 'N/A') for pub in publications if pub.get('tipoComunicacao')]
    comm_counts = pd.Series(comm_types).value_counts()
    
    # Create pie chart
    fig = px.pie(
        values=comm_counts.values,
        names=comm_counts.index,
        title='📢 Distribuição por Tipo de Comunicação'
    )
    
    fig.update_layout(height=400)
    
    st.plotly_chart(fig, use_container_width=True)

def create_process_classes_chart(publications: list):
    """Create process classes horizontal bar chart"""
    if not publications:
        return
    
    # Process class data
    classes = [pub.get('nomeClasse', 'N/A') for pub in publications if pub.get('nomeClasse')]
    class_counts = pd.Series(classes).value_counts().head(10)
    
    # Create horizontal bar chart
    fig = px.bar(
        x=class_counts.values,
        y=class_counts.index,
        orientation='h',
        title='⚖️ Top 10 Classes Processuais',
        labels={'x': 'Número de Publicações', 'y': 'Classe Processual'}
    )
    
    fig.update_layout(
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

def main():
    """Main dashboard function"""
    show_logo()
    
    # Title
    st.title("📊 Dashboard Interativo")
    st.markdown("---")
    
    # Sidebar filters
    st.sidebar.header("🎛️ Filtros Interativos")
    
    # Date range selector
    col_start, col_end = st.sidebar.columns(2)
    with col_start:
        start_date = st.date_input(
            "📅 Data Inicial:",
            value=date.today() - timedelta(days=30),
            key="dash_start_date"
        )
    
    with col_end:
        end_date = st.date_input(
            "📅 Data Final:",
            value=date.today(),
            key="dash_end_date"
        )
    
    # Convert dates to string format
    start_date_str = start_date.strftime('%d/%m/%Y')
    end_date_str = end_date.strftime('%d/%m/%Y')
    
    # Tribunal filter
    db = DatabaseManager()
    all_tribunals = db.get_available_tribunals()
    
    selected_tribunals = st.sidebar.multiselect(
        "🏛️ Tribunais:",
        options=all_tribunals,
        default=all_tribunals[:5] if len(all_tribunals) > 5 else all_tribunals,
        help="Selecione os tribunais para análise"
    )
    
    # Load data with filters
    with st.spinner("Carregando dados do dashboard..."):
        publications, search_executions, analyses = get_dashboard_data(
            start_date_str, end_date_str, selected_tribunals
        )
    
    # Show data info
    if not publications:
        st.warning(f"⚠️ Nenhuma publicação encontrada no período de {start_date_str} a {end_date_str}")
        st.info("💡 Dica: Execute algumas buscas primeiro ou ajuste o período dos filtros")
        return
    
    st.success(f"📊 Exibindo dados de {start_date_str} a {end_date_str} • {len(publications)} publicações")
    
    # KPI Cards Section
    st.markdown("### 📈 Indicadores Principais")
    create_kpi_cards(publications, search_executions, analyses)
    
    st.markdown("---")
    
    # Charts Grid
    st.markdown("### 📊 Análises Visuais")
    
    # First row - Timeline and Tribunals
    col1, col2 = st.columns(2)
    
    with col1:
        create_publications_timeline_chart(publications)
    
    with col2:
        create_tribunals_chart(publications)
    
    # Second row - Communication types and Process classes
    col3, col4 = st.columns(2)
    
    with col3:
        create_communication_types_pie(publications)
    
    with col4:
        create_process_classes_chart(publications)
    
    # Footer
    st.markdown("---")
    st.markdown("*Dashboard atualizado automaticamente a cada 5 minutos* 🔄")

if __name__ == "__main__":
    main()