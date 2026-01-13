import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Factory Energy Retrofit Simulator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        color: #1E3A8A;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.4rem;
        color: #4B5563;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.6rem;
        color: #1E3A8A;
        font-weight: 600;
        border-bottom: 2px solid #E5E7EB;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border-radius: 10px;
        padding: 1.5rem;
        border-left: 5px solid #3B82F6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .recommendation-card {
        background-color: #F0F9FF;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #0EA5E9;
    }
    .stButton>button {
        background-color: #3B82F6;
        color: white;
        font-weight: 600;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #2563EB;
    }
    .footer {
        text-align: center;
        color: #6B7280;
        font-size: 0.9rem;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #E5E7EB;
    }
</style>
""", unsafe_allow_html=True)

# Title and header
st.markdown('<h1 class="main-header">🏭 Factory Energy Retrofit Simulator</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Professional Industrial Energy Audit & Simulation Tool</p>', unsafe_allow_html=True)

# Sidebar for inputs
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3649/3649897.png", width=80)
    st.markdown("## 🔧 Facility Configuration")
    
    # Factory type selection
    factory_type = st.selectbox(
        "Factory Type",
        ["Textile", "Automotive", "Food Processing", "Chemical", "Metal Fabrication", "Plastics"]
    )
    
    # Operating parameters
    st.markdown("### ⏰ Operating Parameters")
    operating_days = st.slider("Operating Days/Year", 200, 365, 300)
    shifts_per_day = st.slider("Shifts per Day", 1, 3, 2)
    hours_per_shift = st.slider("Hours per Shift", 4, 12, 8)
    total_hours = operating_days * shifts_per_day * hours_per_shift
    
    st.info(f"**Annual Operating Hours:** {total_hours:,}")
    
    # Energy costs
    st.markdown("### 💰 Energy Costs")
    electricity_cost = st.number_input("Electricity Cost ($/kWh)", 0.05, 0.30, 0.12, step=0.01)
    demand_cost = st.number_input("Demand Charge ($/kW-month)", 5.0, 30.0, 15.0, step=1.0)
    
    # Carbon factor
    carbon_factor = st.number_input("CO₂ Emission Factor (kg/kWh)", 0.1, 1.5, 0.5, step=0.01)
    
    st.markdown("---")
    st.markdown("### 🔄 Simulation Controls")
    simulation_year = st.slider("Analysis Period (Years)", 1, 10, 5)
    run_simulation = st.button("🚀 Run Energy Retrofit Simulation")

# Main content area
tab1, tab2, tab3, tab4 = st.tabs(["📊 Motor Systems", "💡 Lighting Systems", "📈 Simulation Results", "🎯 Recommendations"])

# Engineering Models
class MotorSystem:
    """Motor efficiency and performance models"""
    
    # Motor efficiency curves (IE2, IE3, IE4 standards)
    EFFICIENCY_CURVES = {
        'IE1': {0.25: 0.78, 0.50: 0.85, 0.75: 0.88, 1.00: 0.89},
        'IE2': {0.25: 0.82, 0.50: 0.88, 0.75: 0.90, 1.00: 0.91},
        'IE3': {0.25: 0.85, 0.50: 0.90, 0.75: 0.92, 1.00: 0.93},
        'IE4': {0.25: 0.88, 0.50: 0.93, 0.75: 0.95, 1.00: 0.96}
    }
    
    # Motor costs by rating ($/kW)
    MOTOR_COSTS = {
        'IE2': 50,
        'IE3': 65,
        'IE4': 85
    }
    
    @staticmethod
    def get_efficiency(efficiency_class, load_factor):
        """Get motor efficiency based on class and load factor"""
        curve = MotorSystem.EFFICIENCY_CURVES.get(efficiency_class, MotorSystem.EFFICIENCY_CURVES['IE2'])
        load_points = list(curve.keys())
        efficiencies = list(curve.values())
        
        # Interpolate for given load factor
        for i in range(len(load_points)-1):
            if load_points[i] <= load_factor <= load_points[i+1]:
                x1, x2 = load_points[i], load_points[i+1]
                y1, y2 = efficiencies[i], efficiencies[i+1]
                return y1 + (y2 - y1) * (load_factor - x1) / (x2 - x1)
        
        return efficiencies[-1] if load_factor >= 1.0 else efficiencies[0]
    
    @staticmethod
    def calculate_vfd_savings(load_factor, motor_power, operating_hours, electricity_cost):
        """Calculate savings from VFD implementation"""
        # VFD savings curve - typical savings at different load factors
        vfd_savings_curve = {
            0.25: 0.40,  # 40% savings at 25% load
            0.50: 0.25,  # 25% savings at 50% load
            0.75: 0.10,  # 10% savings at 75% load
            1.00: 0.00   # 0% savings at full load
        }
        
        # Interpolate savings percentage
        load_points = list(vfd_savings_curve.keys())
        savings_pct = list(vfd_savings_curve.values())
        
        for i in range(len(load_points)-1):
            if load_points[i] <= load_factor <= load_points[i+1]:
                x1, x2 = load_points[i], load_points[i+1]
                y1, y2 = savings_pct[i], savings_pct[i+1]
                savings = y1 + (y2 - y1) * (load_factor - x1) / (x2 - x1)
                break
        else:
            savings = savings_pct[-1] if load_factor >= 1.0 else savings_pct[0]
        
        # Calculate energy consumption without VFD
        base_power = motor_power * load_factor
        base_energy = base_power * operating_hours
        
        # Savings with VFD
        saved_energy = base_energy * savings
        cost_savings = saved_energy * electricity_cost
        
        return saved_energy, cost_savings, savings * 100

class LightingSystem:
    """Lighting system models"""
    
    LIGHTING_TYPES = {
        'Incandescent': {'efficacy': 15, 'lifetime': 1000, 'cost_per_unit': 2},
        'Fluorescent': {'efficacy': 60, 'lifetime': 8000, 'cost_per_unit': 8},
        'CFL': {'efficacy': 65, 'lifetime': 10000, 'cost_per_unit': 5},
        'Metal Halide': {'efficacy': 80, 'lifetime': 15000, 'cost_per_unit': 50},
        'LED': {'efficacy': 120, 'lifetime': 50000, 'cost_per_unit': 15}
    }
    
    @staticmethod
    def calculate_lighting_energy(num_fixtures, wattage_per_fixture, operating_hours):
        """Calculate annual lighting energy consumption"""
        return num_fixtures * wattage_per_fixture * operating_hours / 1000  # kWh

# Default motor data based on factory type
def get_default_motors(factory_type):
    """Get default motor configurations based on factory type"""
    defaults = {
        'Textile': [
            {'rating': 15, 'quantity': 8, 'load_factor': 0.75, 'current_class': 'IE2'},
            {'rating': 22, 'quantity': 6, 'load_factor': 0.80, 'current_class': 'IE2'},
            {'rating': 37, 'quantity': 4, 'load_factor': 0.70, 'current_class': 'IE2'},
            {'rating': 55, 'quantity': 2, 'load_factor': 0.85, 'current_class': 'IE1'},
        ],
        'Automotive': [
            {'rating': 18.5, 'quantity': 10, 'load_factor': 0.65, 'current_class': 'IE2'},
            {'rating': 30, 'quantity': 8, 'load_factor': 0.75, 'current_class': 'IE2'},
            {'rating': 45, 'quantity': 6, 'load_factor': 0.80, 'current_class': 'IE2'},
            {'rating': 75, 'quantity': 3, 'load_factor': 0.70, 'current_class': 'IE1'},
        ],
        'Food Processing': [
            {'rating': 11, 'quantity': 12, 'load_factor': 0.60, 'current_class': 'IE2'},
            {'rating': 18.5, 'quantity': 8, 'load_factor': 0.70, 'current_class': 'IE2'},
            {'rating': 22, 'quantity': 6, 'load_factor': 0.75, 'current_class': 'IE2'},
            {'rating': 37, 'quantity': 4, 'load_factor': 0.65, 'current_class': 'IE1'},
        ]
    }
    return defaults.get(factory_type, defaults['Textile'])

# Default lighting data based on factory type
def get_default_lighting(factory_type):
    """Get default lighting configurations based on factory type"""
    defaults = {
        'Textile': {'type': 'Fluorescent', 'fixtures': 200, 'wattage': 40, 'hours_per_day': 16},
        'Automotive': {'type': 'Metal Halide', 'fixtures': 150, 'wattage': 250, 'hours_per_day': 24},
        'Food Processing': {'type': 'Fluorescent', 'fixtures': 180, 'wattage': 60, 'hours_per_day': 20}
    }
    return defaults.get(factory_type, defaults['Textile'])

# Tab 1: Motor Systems
with tab1:
    st.markdown('<h2 class="section-header">Motor Systems Audit</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### Motor Inventory")
        
        # Motor data input
        default_motors = get_default_motors(factory_type)
        motors_data = []
        
        for i, motor in enumerate(default_motors):
            cols = st.columns([2, 2, 2, 2, 2])
            with cols[0]:
                rating = st.number_input(f"Rating (kW) #{i+1}", 0.75, 500.0, motor['rating'], step=0.5, key=f"rating_{i}")
            with cols[1]:
                quantity = st.number_input(f"Quantity #{i+1}", 1, 100, motor['quantity'], key=f"qty_{i}")
            with cols[2]:
                load_factor = st.slider(f"Load Factor #{i+1}", 0.1, 1.0, motor['load_factor'], 0.05, key=f"load_{i}")
            with cols[3]:
                current_class = st.selectbox(f"Current Class #{i+1}", ['IE1', 'IE2', 'IE3', 'IE4'], 
                                           index=['IE1', 'IE2', 'IE3', 'IE4'].index(motor['current_class']), 
                                           key=f"class_{i}")
            with cols[4]:
                vfd_applicable = st.checkbox(f"VFD Applicable #{i+1}", value=(load_factor < 0.8), key=f"vfd_{i}")
            
            motors_data.append({
                'rating': rating,
                'quantity': quantity,
                'load_factor': load_factor,
                'current_class': current_class,
                'vfd_applicable': vfd_applicable
            })
    
    with col2:
        st.markdown("#### Motor Efficiency Standards")
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/6/6a/IE-classes-en.svg/800px-IE-classes-en.svg.png", 
                caption="International Efficiency (IE) Classification")
        
        st.markdown("**IE Class Comparison:**")
        ie_data = pd.DataFrame({
            'Class': ['IE1', 'IE2', 'IE3', 'IE4'],
            'Efficiency Range': ['Standard', 'High', 'Premium', 'Super Premium'],
            'Typical Savings vs IE1': ['0%', '3-5%', '5-8%', '8-12%']
        })
        st.table(ie_data)
        
        st.info("""
        **VFD Recommendation:**
        Consider VFD for motors with:
        - Load factor < 80%
        - Variable torque loads
        - Long operating hours
        """)

# Tab 2: Lighting Systems
with tab2:
    st.markdown('<h2 class="section-header">Lighting Systems Audit</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        default_lighting = get_default_lighting(factory_type)
        
        st.markdown("#### Current Lighting Configuration")
        lighting_type = st.selectbox("Current Lighting Type", 
                                     list(LightingSystem.LIGHTING_TYPES.keys()),
                                     index=list(LightingSystem.LIGHTING_TYPES.keys()).index(default_lighting['type']))
        
        col1a, col1b, col1c = st.columns(3)
        with col1a:
            num_fixtures = st.number_input("Number of Fixtures", 1, 1000, default_lighting['fixtures'])
        with col1b:
            wattage_per = st.number_input("Wattage per Fixture (W)", 10, 1000, default_lighting['wattage'])
        with col1c:
            daily_hours = st.number_input("Operating Hours/Day", 1, 24, default_lighting['hours_per_day'])
        
        # Calculate current lighting energy
        annual_hours = daily_hours * operating_days
        current_energy = LightingSystem.calculate_lighting_energy(num_fixtures, wattage_per, annual_hours)
        
        st.markdown("#### LED Retrofit Proposal")
        led_wattage = st.slider("Proposed LED Wattage (W)", 10, 200, 
                               int(wattage_per * 0.4),  # Typical LED uses 40% of traditional lighting
                               help="LED fixtures typically provide same lumens at 40-60% of traditional wattage")
        
        # Calculate LED energy
        led_energy = LightingSystem.calculate_lighting_energy(num_fixtures, led_wattage, annual_hours)
        
    with col2:
        st.markdown("#### Lighting Technology Comparison")
        
        # Create comparison chart
        tech_data = []
        for tech, specs in LightingSystem.LIGHTING_TYPES.items():
            energy = LightingSystem.calculate_lighting_energy(num_fixtures, 
                                                             wattage_per if tech == lighting_type else led_wattage, 
                                                             annual_hours)
            tech_data.append({
                'Technology': tech,
                'Efficacy (lm/W)': specs['efficacy'],
                'Lifetime (hours)': f"{specs['lifetime']:,}",
                'Annual Energy (kWh)': f"{energy:,.0f}",
                'Relative Cost': '$$$' if tech == 'LED' else '$$' if tech == 'Metal Halide' else '$'
            })
        
        tech_df = pd.DataFrame(tech_data)
        st.table(tech_df)
        
        # Quick comparison metrics
        st.metric("Current Annual Energy", f"{current_energy:,.0f} kWh")
        st.metric("Proposed LED Energy", f"{led_energy:,.0f} kWh")
        
        if current_energy > 0:
            savings_pct = ((current_energy - led_energy) / current_energy) * 100
            st.metric("Potential Savings", f"{savings_pct:.1f}%", 
                     delta=f"{(current_energy - led_energy):,.0f} kWh")

# Tab 3: Simulation Results
with tab3:
    if run_simulation:
        st.markdown('<h2 class="section-header">Simulation Results</h2>', unsafe_allow_html=True)
        
        # Initialize results storage
        results = {
            'motor_upgrades': [],
            'vfd_savings': [],
            'lighting_retrofit': {}
        }
        
        # Calculate motor upgrade savings
        total_motor_upgrade_savings = 0
        total_motor_upgrade_cost = 0
        total_vfd_savings = 0
        total_vfd_cost = 0
        
        for i, motor in enumerate(motors_data):
            # Current energy consumption
            current_eff = MotorSystem.get_efficiency(motor['current_class'], motor['load_factor'])
            current_power = motor['rating'] * motor['load_factor']
            current_energy = current_power * total_hours * motor['quantity']
            current_input = current_energy / current_eff
            
            # IE4 upgrade
            ie4_eff = MotorSystem.get_efficiency('IE4', motor['load_factor'])
            ie4_input = current_energy / ie4_eff
            energy_savings_motor = current_input - ie4_input
            cost_savings_motor = energy_savings_motor * electricity_cost
            upgrade_cost = motor['rating'] * motor['quantity'] * (MotorSystem.MOTOR_COSTS['IE4'] - 
                                                                 MotorSystem.MOTOR_COSTS.get(motor['current_class'], 
                                                                                           MotorSystem.MOTOR_COSTS['IE2']))
            
            results['motor_upgrades'].append({
                'motor_id': i+1,
                'rating': motor['rating'],
                'quantity': motor['quantity'],
                'current_class': motor['current_class'],
                'energy_savings': energy_savings_motor,
                'cost_savings': cost_savings_motor,
                'upgrade_cost': max(upgrade_cost, 100),  # Minimum cost
                'payback_years': max(upgrade_cost, 100) / cost_savings_motor if cost_savings_motor > 0 else 999
            })
            
            total_motor_upgrade_savings += cost_savings_motor
            total_motor_upgrade_cost += max(upgrade_cost, 100)
            
            # VFD savings if applicable
            if motor['vfd_applicable']:
                vfd_energy_savings, vfd_cost_savings, vfd_savings_pct = MotorSystem.calculate_vfd_savings(
                    motor['load_factor'], motor['rating'], total_hours * motor['quantity'], electricity_cost
                )
                vfd_cost = motor['rating'] * motor['quantity'] * 100  # $100/kW for VFD
                
                results['vfd_savings'].append({
                    'motor_id': i+1,
                    'rating': motor['rating'],
                    'quantity': motor['quantity'],
                    'energy_savings': vfd_energy_savings,
                    'cost_savings': vfd_cost_savings,
                    'vfd_cost': vfd_cost,
                    'payback_years': vfd_cost / vfd_cost_savings if vfd_cost_savings > 0 else 999,
                    'savings_pct': vfd_savings_pct
                })
                
                total_vfd_savings += vfd_cost_savings
                total_vfd_cost += vfd_cost
        
        # Calculate lighting retrofit savings
        current_lighting_energy = LightingSystem.calculate_lighting_energy(
            num_fixtures, wattage_per, daily_hours * operating_days
        )
        led_energy = LightingSystem.calculate_lighting_energy(
            num_fixtures, led_wattage, daily_hours * operating_days
        )
        lighting_energy_savings = current_lighting_energy - led_energy
        lighting_cost_savings = lighting_energy_savings * electricity_cost
        lighting_retrofit_cost = num_fixtures * LightingSystem.LIGHTING_TYPES['LED']['cost_per_unit'] * 10  # Including installation
        
        results['lighting_retrofit'] = {
            'current_energy': current_lighting_energy,
            'led_energy': led_energy,
            'energy_savings': lighting_energy_savings,
            'cost_savings': lighting_cost_savings,
            'retrofit_cost': lighting_retrofit_cost,
            'payback_years': lighting_retrofit_cost / lighting_cost_savings if lighting_cost_savings > 0 else 999
        }
        
        # Display results
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_energy_savings = (sum([m['energy_savings'] for m in results['motor_upgrades']]) +
                                   sum([v['energy_savings'] for v in results['vfd_savings']]) +
                                   results['lighting_retrofit']['energy_savings'])
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Total Annual Energy Savings", f"{total_energy_savings:,.0f} kWh", 
                     delta=f"${total_energy_savings * electricity_cost:,.0f}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            total_cost_savings = (sum([m['cost_savings'] for m in results['motor_upgrades']]) +
                                 sum([v['cost_savings'] for v in results['vfd_savings']]) +
                                 results['lighting_retrofit']['cost_savings'])
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Total Annual Cost Savings", f"${total_cost_savings:,.0f}", 
                     delta=f"{total_cost_savings/electricity_cost:,.0f} kWh")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            co2_reduction = total_energy_savings * carbon_factor / 1000  # Tons
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("CO₂ Reduction", f"{co2_reduction:,.1f} tons/year", 
                     delta=f"Equivalent to {co2_reduction/5:.0f} cars off the road")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Detailed results in expandable sections
        with st.expander("📊 Motor Efficiency Upgrade Analysis", expanded=True):
            if results['motor_upgrades']:
                motor_df = pd.DataFrame(results['motor_upgrades'])
                st.dataframe(motor_df.style.format({
                    'rating': '{:.1f}',
                    'energy_savings': '{:,.0f}',
                    'cost_savings': '${:,.0f}',
                    'upgrade_cost': '${:,.0f}',
                    'payback_years': '{:.1f}'
                }))
                
                # Create visualization
                fig = go.Figure(data=[
                    go.Bar(name='Annual Savings', x=motor_df['motor_id'], y=motor_df['cost_savings']),
                    go.Bar(name='Upgrade Cost', x=motor_df['motor_id'], y=motor_df['upgrade_cost'])
                ])
                fig.update_layout(
                    title="Motor Upgrade Economics",
                    xaxis_title="Motor ID",
                    yaxis_title="Amount ($)",
                    barmode='group'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with st.expander("⚙️ VFD Implementation Analysis"):
            if results['vfd_savings']:
                vfd_df = pd.DataFrame(results['vfd_savings'])
                st.dataframe(vfd_df.style.format({
                    'rating': '{:.1f}',
                    'energy_savings': '{:,.0f}',
                    'cost_savings': '${:,.0f}',
                    'vfd_cost': '${:,.0f}',
                    'payback_years': '{:.1f}',
                    'savings_pct': '{:.1f}%'
                }))
                
                # Payback period visualization
                fig = px.bar(vfd_df, x='motor_id', y='payback_years',
                           title="VFD Payback Period by Motor",
                           labels={'payback_years': 'Payback Period (Years)', 'motor_id': 'Motor ID'})
                fig.add_hline(y=3, line_dash="dash", line_color="red", 
                            annotation_text="3-Year Target", annotation_position="top right")
                st.plotly_chart(fig, use_container_width=True)
        
        with st.expander("💡 Lighting Retrofit Analysis"):
            lighting_data = results['lighting_retrofit']
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Current System:**")
                st.metric("Annual Energy", f"{lighting_data['current_energy']:,.0f} kWh")
                st.metric("Annual Cost", f"${lighting_data['current_energy'] * electricity_cost:,.0f}")
            
            with col2:
                st.markdown("**LED System:**")
                st.metric("Annual Energy", f"{lighting_data['led_energy']:,.0f} kWh")
                st.metric("Annual Cost", f"${lighting_data['led_energy'] * electricity_cost:,.0f}")
            
            st.markdown("**Retrofit Economics:**")
            col3, col4, col5 = st.columns(3)
            with col3:
                st.metric("Energy Savings", f"{lighting_data['energy_savings']:,.0f} kWh", 
                         delta=f"{lighting_data['energy_savings']/lighting_data['current_energy']*100:.1f}%")
            with col4:
                st.metric("Cost Savings", f"${lighting_data['cost_savings']:,.0f}/year")
            with col5:
                st.metric("Payback Period", f"{lighting_data['payback_years']:.1f} years")
        
        # Cumulative savings over time
        with st.expander("📈 10-Year Projection"):
            years = list(range(1, 11))
            cumulative_savings = [total_cost_savings * y for y in years]
            cumulative_cost = [total_motor_upgrade_cost + total_vfd_cost + lighting_retrofit_cost] * len(years)
            net_savings = [cumulative_savings[i] - cumulative_cost[0] for i in range(len(years))]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=years, y=cumulative_savings, mode='lines+markers', 
                                    name='Cumulative Savings', line=dict(color='green', width=3)))
            fig.add_trace(go.Scatter(x=years, y=cumulative_cost, mode='lines', 
                                    name='Total Investment', line=dict(color='red', dash='dash')))
            fig.add_trace(go.Scatter(x=years, y=net_savings, mode='lines+markers', 
                                    name='Net Savings', line=dict(color='blue', width=2)))
            
            fig.update_layout(
                title="10-Year Financial Projection",
                xaxis_title="Year",
                yaxis_title="Amount ($)",
                hovermode='x unified'
            )
            
            # Find break-even point
            break_even = None
            for i, net in enumerate(net_savings):
                if net >= 0:
                    break_even = years[i]
                    fig.add_vline(x=break_even, line_dash="dash", line_color="orange",
                                annotation_text=f"Break-even: Year {break_even}")
                    break
            
            st.plotly_chart(fig, use_container_width=True)
            
            if break_even:
                st.success(f"💰 **Projected break-even point: Year {break_even}**")
            else:
                st.warning("⚠️ Break-even point beyond 10 years")

# Tab 4: Recommendations
with tab4:
    st.markdown('<h2 class="section-header">Prioritized Retrofit Recommendations</h2>', unsafe_allow_html=True)
    
    if not run_simulation:
        st.info("👈 Run the simulation first to get personalized recommendations")
    else:
        # Create priority list
        recommendations = []
        
        # Add motor upgrades
        for motor in results['motor_upgrades']:
            if motor['payback_years'] <= 5:  # Only recommend if payback <= 5 years
                recommendations.append({
                    'type': 'Motor Upgrade',
                    'description': f"Motor {motor['motor_id']}: IE{motor['current_class'][-1]} → IE4 ({motor['rating']}kW × {motor['quantity']})",
                    'investment': f"${motor['upgrade_cost']:,.0f}",
                    'annual_savings': f"${motor['cost_savings']:,.0f}",
                    'payback': f"{motor['payback_years']:.1f} years",
                    'priority': 'High' if motor['payback_years'] <= 2 else 'Medium',
                    'sort_key': 1/motor['payback_years'] if motor['payback_years'] > 0 else 0
                })
        
        # Add VFD implementations
        for vfd in results['vfd_savings']:
            if vfd['payback_years'] <= 4:  # Only recommend if payback <= 4 years
                recommendations.append({
                    'type': 'VFD Installation',
                    'description': f"Motor {vfd['motor_id']}: {vfd['rating']}kW VFD ({vfd['quantity']} units)",
                    'investment': f"${vfd['vfd_cost']:,.0f}",
                    'annual_savings': f"${vfd['cost_savings']:,.0f}",
                    'payback': f"{vfd['payback_years']:.1f} years",
                    'priority': 'High' if vfd['payback_years'] <= 2 else 'Medium',
                    'sort_key': 1/vfd['payback_years'] if vfd['payback_years'] > 0 else 0
                })
        
        # Add lighting retrofit
        lighting = results['lighting_retrofit']
        if lighting['payback_years'] <= 5:
            recommendations.append({
                'type': 'Lighting Retrofit',
                'description': f"LED Retrofit: {num_fixtures} fixtures × {led_wattage}W LED",
                'investment': f"${lighting['retrofit_cost']:,.0f}",
                'annual_savings': f"${lighting['cost_savings']:,.0f}",
                'payback': f"{lighting['payback_years']:.1f} years",
                'priority': 'High' if lighting['payback_years'] <= 2 else 'Medium',
                'sort_key': 1/lighting['payback_years'] if lighting['payback_years'] > 0 else 0
            })
        
        # Sort by priority (highest ROI first)
        recommendations.sort(key=lambda x: x['sort_key'], reverse=True)
        
        if not recommendations:
            st.warning("No retrofit measures meet the investment criteria. Consider reviewing input parameters.")
        else:
            # Display recommendations
            st.markdown(f"### 🎯 Found {len(recommendations)} Viable Retrofit Measures")
            
            for i, rec in enumerate(recommendations):
                priority_color = {
                    'High': '#EF4444',
                    'Medium': '#F59E0B',
                    'Low': '#10B981'
                }.get(rec['priority'], '#6B7280')
                
                st.markdown(f"""
                <div class="recommendation-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h4 style="margin: 0; color: {priority_color};">{rec['type']} • {rec['priority']} Priority</h4>
                            <p style="margin: 0.5rem 0; color: #4B5563;">{rec['description']}</p>
                        </div>
                        <div style="background-color: {priority_color}; color: white; padding: 0.5rem 1rem; border-radius: 5px; font-weight: bold;">
                            #{i+1}
                        </div>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-top: 1rem;">
                        <div>
                            <small>Investment</small>
                            <p style="font-weight: bold; margin: 0.25rem 0;">{rec['investment']}</p>
                        </div>
                        <div>
                            <small>Annual Savings</small>
                            <p style="font-weight: bold; margin: 0.25rem 0;">{rec['annual_savings']}</p>
                        </div>
                        <div>
                            <small>Payback Period</small>
                            <p style="font-weight: bold; margin: 0.25rem 0;">{rec['payback']}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Implementation roadmap
            st.markdown("### 🗺️ Recommended Implementation Roadmap")
            
            roadmap_data = []
            current_year = datetime.now().year
            
            for i, rec in enumerate(recommendations[:5]):  # Top 5 recommendations
                payback = float(rec['payback'].split()[0])
                roadmap_data.append({
                    'Year': current_year,
                    'Phase': 'Phase 1',
                    'Action': rec['description'],
                    'Duration': f"{min(6, int(payback*12))} months",
                    'Priority': rec['priority']
                })
                
                if i >= 2:  # Phase 2 for next set
                    roadmap_data.append({
                        'Year': current_year + 1,
                        'Phase': 'Phase 2',
                        'Action': rec['description'],
                        'Duration': f"{min(6, int(payback*12))} months",
                        'Priority': rec['priority']
                    })
            
            roadmap_df = pd.DataFrame(roadmap_data)
            st.dataframe(roadmap_df, use_container_width=True)
            
            # Download report
            st.markdown("### 📄 Download Report")
            
            report_data = {
                'Factory Type': factory_type,
                'Analysis Date': datetime.now().strftime("%Y-%m-%d"),
                'Annual Operating Hours': f"{total_hours:,}",
                'Electricity Cost': f"${electricity_cost}/kWh",
                'Total Energy Savings': f"{total_energy_savings:,.0f} kWh",
                'Total Cost Savings': f"${total_cost_savings:,.0f}",
                'CO₂ Reduction': f"{co2_reduction:,.1f} tons",
                'Number of Recommendations': len(recommendations)
            }
            
            report_df = pd.DataFrame(list(report_data.items()), columns=['Parameter', 'Value'])
            
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="📥 Download Summary Report (CSV)",
                    data=report_df.to_csv(index=False).encode('utf-8'),
                    file_name=f"energy_audit_report_{factory_type}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            
            with col2:
                st.download_button(
                    label="📥 Download Detailed Analysis (Excel)",
                    data=pd.DataFrame(recommendations).to_csv(index=False).encode('utf-8'),
                    file_name=f"detailed_analysis_{factory_type}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )

# Footer
st.markdown("---")
st.markdown("""
<div class="footer">
    <p><strong>Factory Energy Retrofit Simulator</strong> | Professional Energy Audit Tool v2.1</p>
    <p>Made By <strong>Areeb Rizwan</strong>, Mechanical Engineer</p>
    <p>🌐 Website: <a href="https://www.areebrizwan.com" target="_blank">www.areebrizwan.com</a></p>
    <p>💼 LinkedIn: <a href="https://www.linkedin.com/in/areebrizwan" target="_blank">www.linkedin.com/in/areebrizwan</a></p>
    <p style="font-size: 0.8rem; margin-top: 1rem; color: #9CA3AF;">
        Disclaimer: This tool provides estimates based on standard engineering models. 
        Actual savings may vary based on specific site conditions and implementation.
    </p>
</div>
""", unsafe_allow_html=True)
