import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
import tempfile
import os

# Configuração da página
st.set_page_config(
    page_title="Software de Performance de Compressores",
    page_icon=":compression:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar estado da sessão
if 'units' not in st.session_state:
    st.session_state.units = {
        'pressure': 'psig',
        'temperature': 'C',
        'length': 'mm',
        'flow': 'E3*m3/d'
    }

if 'equipment' not in st.session_state:
    st.session_state.equipment = {
        'motor_type': 'Elétrico',
        'rpm': 1800,
        'derate': 0.0,
        'stroke': 150.0,
        'num_cylinders': 2,
        'cylinders': []
    }

if 'process' not in st.session_state:
    st.session_state.process = {
        'suction_pressure': 100.0,
        'discharge_pressure': 500.0,
        'power': 0.0
    }

if 'report' not in st.session_state:
    st.session_state.report = ""

if 'multirun' not in st.session_state:
    st.session_state.multirun = {
        'suction_min': 50.0,
        'suction_max': 200.0,
        'discharge_min': 300.0,
        'discharge_max': 600.0
    }

# Barra lateral
st.sidebar.title("Navegação")
st.sidebar.markdown("Selecione uma aba:")

# Função para criar aba de navegação
def navigation():
    pages = [
        "Sistema de Unidades",
        "Configuração do Equipamento",
        "Processo",
        "Performance",
        "Relatório",
        "Multirun"
    ]
    
    selected_page = st.sidebar.selectbox("Selecione uma aba", pages)
    return selected_page

# Carregar página selecionada
selected_page = navigation()

# Página: Sistema de Unidades
if selected_page == "Sistema de Unidades":
    st.title("Sistema de Unidades")
    
    # Pressão
    st.subheader("Pressão")
    pressure_unit = st.radio(
        "Selecione a unidade de pressão:",
        ['psig', 'kgf/cm²g'],
        index=0,
        key='pressure_unit'
    )
    st.session_state.units['pressure'] = pressure_unit
    
    # Temperatura
    st.subheader("Temperatura")
    temp_unit = st.radio(
        "Selecione a unidade de temperatura:",
        ['°C', '°F'],
        index=0,
        key='temp_unit'
    )
    st.session_state.units['temperature'] = temp_unit
    
    # Comprimento
    st.subheader("Comprimento")
    length_unit = st.radio(
        "Selecione a unidade de comprimento:",
        ['mm', 'polegadas'],
        index=0,
        key='length_unit'
    )
    st.session_state.units['length'] = length_unit
    
    # Vazão Volumétrica
    st.subheader("Vazão Volumétrica")
    flow_unit = st.radio(
        "Selecione a unidade de vazão:",
        ['E3*m³/d', 'MMSCFD'],
        index=0,
        key='flow_unit'
    )
    st.session_state.units['flow'] = flow_unit
    
    st.success(f"Unidades atualizadas: Pressão ({pressure_unit}), Temperatura ({temp_unit}), Comprimento ({length_unit}), Vazão ({flow_unit})")

# Página: Configuração do Equipamento
elif selected_page == "Configuração do Equipamento":
    st.title("Configuração do Equipamento")
    
    # Motor
    st.subheader("Motor")
    motor_type = st.radio(
        "Tipo de Motor:",
        ['Gás Natural', 'Elétrico'],
        index=1,
        key='motor_type'
    )
    st.session_state.equipment['motor_type'] = motor_type
    
    rpm = st.number_input(
        "RPM:",
        min_value=0,
        value=st.session_state.equipment['rpm'],
        key='rpm'
    )
    st.session_state.equipment['rpm'] = rpm
    
    derate = st.number_input(
        "Derate (%):",
        min_value=0.0,
        max_value=100.0,
        value=st.session_state.equipment['derate'],
        key='derate'
    )
    st.session_state.equipment['derate'] = derate
    
    # Air Cooler
    st.subheader("Air Cooler")
    st.write("Perda de carga: 1% por estágio")
    st.write("Temperatura de Saída: 120°F por estágio")
    
    # Compressor
    st.subheader("Compressor")
    stroke = st.number_input(
        "Stroke:",
        min_value=0.0,
        value=st.session_state.equipment['stroke'],
        key='stroke'
    )
    st.session_state.equipment['stroke'] = stroke
    
    num_cylinders = st.number_input(
        "Número de Cilindros:",
        min_value=1,
        value=st.session_state.equipment['num_cylinders'],
        key='num_cylinders'
    )
    st.session_state.equipment['num_cylinders'] = num_cylinders
    
    # Configuração de cilindros
    if st.button("Configurar Cilindros"):
        st.session_state.configure_cylinders = True
    
    if st.session_state.get('configure_cylinders', False):
        st.subheader("Configuração dos Cilindros")
        cylinders = []
        
        for i in range(st.session_state.equipment['num_cylinders']):
            st.write(f"**Cilindro {i+1}**")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                stage = st.number_input(
                    f"Estágio (Cilindro {i+1}):",
                    min_value=1,
                    value=1,
                    key=f'stage_{i}'
                )
            
            with col2:
                clearance = st.number_input(
                    f"Clearance (%) (Cilindro {i+1}):",
                    min_value=0.0,
                    max_value=100.0,
                    value=10.0,
                    key=f'clearance_{i}'
                )
            
            with col3:
                sace_type = st.radio(
                    f"SACE (Cilindro {i+1}):",
                    ['SACE', 'SACE/Cilindro'],
                    key=f'sace_{i}'
                )
            
            vvcp = st.number_input(
                f"VVCP (%) (Cilindro {i+1}):",
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                key=f'vvcp_{i}'
            )
            
            cylinders.append({
                'stage': stage,
                'clearance': clearance,
                'sace_type': sace_type,
                'vvcp': vvcp
            })
        
        st.session_state.equipment['cylinders'] = cylinders
        
        if st.button("Salvar Configuração dos Cilindros"):
            st.session_state.configure_cylinders = False
            st.success("Configuração dos cilindros salva!")
    
    # Diagrama ilustrativo
    st.subheader("Diagrama de Configuração do Equipamento")
    fig, ax = plt.subplots(figsize=(8, 4))
    
    # Desenho do compressor
    ax.add_patch(plt.Rectangle((1, 1), 4, 2, fill=False))
    ax.text(3, 2, "Compressor", ha='center')
    
    # Desenho dos cilindros
    for i in range(st.session_state.equipment['num_cylinders']):
        ax.add_patch(plt.Circle((1.5 + i*1.5, 2), 0.3, fill=False))
        ax.text(1.5 + i*1.5, 2, f"C{i+1}", ha='center')
    
    ax.set_xlim(0, 6)
    ax.set_ylim(0, 4)
    ax.axis('off')
    st.pyplot(fig)

# Página: Processo
elif selected_page == "Processo":
    st.title("Processo")
    
    # PFD
    st.subheader("Diagrama de Fluxo do Processo (PFD)")
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Sucção
    ax.annotate('Sucção', xy=(1, 2), xytext=(0.5, 2), arrowprops=dict(arrowstyle='->'))
    
    # Compressor
    ax.add_patch(plt.Rectangle((1, 1.5), 2, 1, fill=False))
    ax.text(2, 2, "Compressor", ha='center')
    
    # Air Cooler
    ax.annotate('', xy=(4, 2), xytext=(3, 2), arrowprops=dict(arrowstyle='->'))
    ax.add_patch(plt.Rectangle((4, 1.5), 2, 1, fill=False))
    ax.text(5, 2, "Air Cooler", ha='center')
    
    # Descarga
    ax.annotate('', xy=(7, 2), xytext=(6, 2), arrowprops=dict(arrowstyle='->'))
    ax.text(7.5, 2, "Descarga")
    
    ax.set_xlim(0, 8)
    ax.set_ylim(1, 3)
    ax.axis('off')
    st.pyplot(fig)
    
    # Potência requerida
    st.subheader("Potência Requerida")
    st.write(f"**{st.session_state.process['power']:.2f} BHP**")

# Página: Performance
elif selected_page == "Performance":
    st.title("Cálculo de Performance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        suction_pressure = st.number_input(
            "Pressão de Sucção:",
            min_value=0.0,
            value=st.session_state.process['suction_pressure'],
            key='suction_pressure'
        )
        st.session_state.process['suction_pressure'] = suction_pressure
    
    with col2:
        discharge_pressure = st.number_input(
            "Pressão de Descarga:",
            min_value=0.0,
            value=st.session_state.process['discharge_pressure'],
            key='discharge_pressure'
        )
        st.session_state.process['discharge_pressure'] = discharge_pressure
    
    if st.button("Calcular Performance"):
        # Lógica de cálculo (simplificada)
        k = 0.001  # Constante fictícia
        power = k * (st.session_state.process['discharge_pressure'] - st.session_state.process['suction_pressure']) * st.session_state.equipment['rpm']
        st.session_state.process['power'] = power
        st.success(f"Potência Requerida: {power:.2f} BHP")
        
        # Atualizar relatório
        update_report(power)
    
    def update_report(power):
        report = f"""
        RELATÓRIO DE PERFORMANCE
        -------------------------
        Pressão de Sucção: {st.session_state.process['suction_pressure']} {st.session_state.units['pressure']}
        Pressão de Descarga: {st.session_state.process['discharge_pressure']} {st.session_state.units['pressure']}
        RPM: {st.session_state.equipment['rpm']}
        Potência Requerida: {power:.2f} BHP
        
        Configuração do Equipamento:
        - Motor: {st.session_state.equipment['motor_type']}
        - Derate: {st.session_state.equipment['derate']}%
        - Stroke: {st.session_state.equipment['stroke']} {st.session_state.units['length']}
        """
        st.session_state.report = report

# Página: Relatório
elif selected_page == "Relatório":
    st.title("Relatório")
    
    st.text_area(
        "Relatório de Performance",
        st.session_state.report,
        height=300
    )
    
    if st.button("Exportar PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Relatório de Performance", ln=1, align='C')
        pdf.multi_cell(0, 10, st.session_state.report)
        
        # Salvar PDF em um arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            pdf.output(tmp_file.name)
            tmp_file_path = tmp_file.name
        
        # Botão de download
        with open(tmp_file_path, "rb") as f:
            st.download_button(
                label="Download PDF",
                data=f.read(),
                file_name="relatorio_performance.pdf",
                mime="application/pdf"
            )
        
        # Remover arquivo temporário
        os.unlink(tmp_file_path)

# Página: Multirun
elif selected_page == "Multirun":
    st.title("Multirun")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Faixa de Pressão de Sucção")
        suction_min = st.number_input(
            "Mínimo:",
            min_value=0.0,
            value=st.session_state.multirun['suction_min'],
            key='suction_min'
        )
        st.session_state.multirun['suction_min'] = suction_min
        
        suction_max = st.number_input(
            "Máximo:",
            min_value=0.0,
            value=st.session_state.multirun['suction_max'],
            key='suction_max'
        )
        st.session_state.multirun['suction_max'] = suction_max
    
    with col2:
        st.subheader("Faixa de Pressão de Descarga")
        discharge_min = st.number_input(
            "Mínimo:",
            min_value=0.0,
            value=st.session_state.multirun['discharge_min'],
            key='discharge_min'
        )
        st.session_state.multirun['discharge_min'] = discharge_min
        
        discharge_max = st.number_input(
            "Máximo:",
            min_value=0.0,
            value=st.session_state.multirun['discharge_max'],
            key='discharge_max'
        )
        st.session_state.multirun['discharge_max'] = discharge_max
    
    if st.button("Gerar Gráficos"):
        # Gerar dados
        suction_range = np.linspace(
            st.session_state.multirun['suction_min'],
            st.session_state.multirun['suction_max'],
            10
        )
        discharge_range = np.linspace(
            st.session_state.multirun['discharge_min'],
            st.session_state.multirun['discharge_max'],
            5
        )
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        for p_discharge in discharge_range:
            flows = []
            powers = []
            for p_suction in suction_range:
                # Cálculos fictícios
                flow = 1000 * (p_discharge - p_suction) / st.session_state.equipment['rpm']
                power = 0.001 * (p_discharge - p_suction) * st.session_state.equipment['rpm']
                flows.append(flow)
                powers.append(power)
            
            # Plotar
            ax1.plot(suction_range, flows, label=f'Descarga: {p_discharge:.0f}')
            ax2.plot(suction_range, powers, label=f'Descarga: {p_discharge:.0f}')
        
        # Configurar gráficos
        ax1.set_xlabel('Pressão de Sucção')
        ax1.set_ylabel('Vazão Volumétrica')
        ax1.legend()
        ax1.grid(True)
        
        ax2.set_xlabel('Pressão de Sucção')
        ax2.set_ylabel('Potência (BHP)')
        ax2.legend()
        ax2.grid(True)
        
        st.pyplot(fig)
