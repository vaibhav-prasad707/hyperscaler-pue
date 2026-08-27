"""
Multi-page Streamlit dashboard for PUE Benchmark Analysis.
Main entry point.
"""

import streamlit as st
import pandas as pd
from pathlib import Path

from config.constants import BENCHMARK_CSV, DASHBOARD_TITLE, DASHBOARD_PAGE_ICON
from utils.logger import setup_logger


logger = setup_logger(__name__)

# Page configuration
st.set_page_config(
    page_title=DASHBOARD_TITLE,
    page_icon=DASHBOARD_PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def load_data():
    """Load and cache benchmark data."""
    csv_path = Path(BENCHMARK_CSV)

    if not csv_path.exists():
        st.error(f"Data file not found: {csv_path}")
        st.info("Please run the data collection and cleaning pipeline first.")
        st.stop()

    df = pd.read_csv(csv_path)
    return df


def main():
    """Main dashboard application."""

    # Load data
    df = load_data()

    # Sidebar
    st.sidebar.title("⚡ PUE Benchmark")
    st.sidebar.markdown("---")

    # Filters
    st.sidebar.header("🔍 Filters")

    # Tier filter
    all_tiers = ['All'] + sorted(df['tier'].dropna().unique().tolist())
    selected_tier = st.sidebar.selectbox("Tier", all_tiers)

    # Country filter
    all_countries = ['All'] + sorted(df['country'].dropna().unique().tolist())
    selected_country = st.sidebar.selectbox("Country", all_countries)

    # PUE type filter
    all_pue_types = ['All'] + sorted(df['pue_type'].dropna().unique().tolist())
    selected_pue_type = st.sidebar.selectbox("PUE Type", all_pue_types)

    # Apply filters
    filtered_df = df.copy()

    if selected_tier != 'All':
        filtered_df = filtered_df[filtered_df['tier'] == selected_tier]

    if selected_country != 'All':
        filtered_df = filtered_df[filtered_df['country'] == selected_country]

    if selected_pue_type != 'All':
        filtered_df = filtered_df[filtered_df['pue_type'] == selected_pue_type]

    # Store in session state
    st.session_state['filtered_df'] = filtered_df
    st.session_state['full_df'] = df

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Records:** {len(filtered_df)} / {len(df)}")

    # Navigation
    st.sidebar.header("📊 Navigation")

    page = st.sidebar.radio(
        "Select Page",
        [
            "🏆 Leaderboard",
            "📐 Design vs Operating",
            "🇮🇳 India Deep Dive",
            "💰 ROI Calculator",
        ]
    )

    # Route to pages
    if page == "🏆 Leaderboard":
        show_leaderboard(filtered_df)

    elif page == "📐 Design vs Operating":
        show_design_vs_operating(filtered_df)

    elif page == "🇮🇳 India Deep Dive":
        show_india_deep_dive(df)  # Use full dataset

    elif page == "💰 ROI Calculator":
        show_roi_calculator()

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        **Hyperscaler PUE Benchmark**
        Data Center Efficiency Analysis
        © 2026
        """
    )


def show_leaderboard(df):
    """Display PUE leaderboard."""
    st.title("🏆 PUE Efficiency Leaderboard")
    st.markdown("Compare data center efficiency across hyperscalers, Indian operators, and colocation providers")

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Facilities", len(df))

    with col2:
        avg_pue = df['pue_value'].mean()
        st.metric("Average PUE", f"{avg_pue:.3f}")

    with col3:
        best_pue = df['pue_value'].min()
        st.metric("Best PUE", f"{best_pue:.3f}")

    with col4:
        avg_renewable = df['renewable_pct'].mean()
        if pd.notna(avg_renewable):
            st.metric("Avg Renewable %", f"{avg_renewable:.1f}%")
        else:
            st.metric("Avg Renewable %", "N/A")

    st.markdown("---")

    # Leaderboard table
    st.subheader("📋 Facility Rankings")

    # Prepare display dataframe
    display_df = df[['company', 'facility_name', 'city', 'country', 'pue_value', 'pue_type',
                     'capacity_mw', 'renewable_pct', 'tier']].copy()

    display_df = display_df.sort_values('pue_value')
    display_df.insert(0, 'Rank', range(1, len(display_df) + 1))

    # Format columns
    display_df['pue_value'] = display_df['pue_value'].apply(lambda x: f"{x:.3f}")
    display_df['capacity_mw'] = display_df['capacity_mw'].apply(
        lambda x: f"{x:.1f}" if pd.notna(x) else "N/A"
    )
    display_df['renewable_pct'] = display_df['renewable_pct'].apply(
        lambda x: f"{x:.0f}%" if pd.notna(x) else "N/A"
    )

    st.dataframe(display_df, use_container_width=True, height=400)

    # Visualizations
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 PUE by Tier")
        import plotly.express as px

        tier_avg = df.groupby('tier')['pue_value'].mean().reset_index()
        tier_avg = tier_avg.sort_values('pue_value')

        fig = px.bar(
            tier_avg,
            x='tier',
            y='pue_value',
            title='Average PUE by Tier',
            labels={'pue_value': 'Average PUE', 'tier': 'Tier'},
            color='pue_value',
            color_continuous_scale='RdYlGn_r'
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🌍 PUE Distribution")

        fig = px.histogram(
            df,
            x='pue_value',
            nbins=20,
            title='PUE Distribution',
            labels={'pue_value': 'PUE Value', 'count': 'Frequency'},
            color_discrete_sequence=['#2ca02c']
        )
        st.plotly_chart(fig, use_container_width=True)

    # Download button
    st.markdown("---")
    csv = display_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Leaderboard CSV",
        data=csv,
        file_name="pue_leaderboard.csv",
        mime="text/csv"
    )


def show_design_vs_operating(df):
    """Compare design vs operating PUE."""
    st.title("📐 Design vs Operating PUE")
    st.markdown("Understanding the gap between design specifications and actual operations")

    # Filter for design and operating only
    comparison_df = df[df['pue_type'].isin(['design', 'operating', 'TTM'])].copy()

    if len(comparison_df) == 0:
        st.warning("No design or operating PUE data available")
        return

    # Summary metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        design_count = len(comparison_df[comparison_df['pue_type'] == 'design'])
        st.metric("Design PUE Records", design_count)

    with col2:
        operating_count = len(comparison_df[comparison_df['pue_type'].isin(['operating', 'TTM'])])
        st.metric("Operating PUE Records", operating_count)

    with col3:
        ttm_count = len(comparison_df[comparison_df['pue_type'] == 'TTM'])
        st.metric("TTM PUE Records", ttm_count)

    st.markdown("---")

    # Pie chart
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 PUE Type Distribution")
        import plotly.express as px

        type_counts = comparison_df['pue_type'].value_counts()

        fig = px.pie(
            values=type_counts.values,
            names=type_counts.index,
            title='Distribution of PUE Types',
            color_discrete_sequence=['#2ca02c', '#ff7f0e', '#1f77b4']
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("📈 Average by Type")

        type_avg = comparison_df.groupby('pue_type')['pue_value'].mean().reset_index()

        fig = px.bar(
            type_avg,
            x='pue_type',
            y='pue_value',
            title='Average PUE by Type',
            labels={'pue_value': 'Average PUE', 'pue_type': 'PUE Type'},
            color='pue_value',
            color_continuous_scale='RdYlGn_r'
        )
        st.plotly_chart(fig, use_container_width=True)

    # Scatter plot
    st.markdown("---")
    st.subheader("🎯 Company Comparison")

    import plotly.express as px

    fig = px.scatter(
        comparison_df,
        x='company',
        y='pue_value',
        color='pue_type',
        size='capacity_mw',
        hover_data=['facility_name', 'city', 'year'],
        title='PUE Values by Company and Type',
        labels={'pue_value': 'PUE Value', 'company': 'Company'},
        color_discrete_map={'design': '#ff7f0e', 'operating': '#2ca02c', 'TTM': '#1f77b4'}
    )
    fig.update_xaxis(tickangle=45)
    st.plotly_chart(fig, use_container_width=True)

    # Explanation
    st.markdown("---")
    st.info("""
    **Understanding PUE Types:**

    - **Design PUE**: Theoretical efficiency based on design specifications. Often optimistic.
    - **Operating PUE**: Actual measured efficiency during operations. More realistic.
    - **TTM (Trailing Twelve Month)**: Rolling 12-month average. Highest quality metric.

    **Key Insight**: Operating PUE is typically 10-20% higher than design PUE due to real-world conditions.
    """)


def show_india_deep_dive(df):
    """India-specific analysis."""
    st.title("🇮🇳 India Data Center Deep Dive")
    st.markdown("Analyzing India's data center efficiency landscape")

    # Filter Indian facilities
    india_df = df[df['country'] == 'India'].copy()
    global_df = df[df['country'] != 'India'].copy()

    if len(india_df) == 0:
        st.warning("No Indian facility data available")
        return

    # Comparison metrics
    st.subheader("📊 India vs Global Comparison")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        india_avg = india_df['pue_value'].mean()
        global_avg = global_df['pue_value'].mean()
        delta = india_avg - global_avg
        st.metric("India Avg PUE", f"{india_avg:.3f}", f"{delta:+.3f} vs Global")

    with col2:
        india_best = india_df['pue_value'].min()
        st.metric("India Best PUE", f"{india_best:.3f}")

    with col3:
        india_capacity = india_df['capacity_mw'].sum()
        st.metric("Total Capacity (MW)", f"{india_capacity:.1f}" if pd.notna(india_capacity) else "N/A")

    with col4:
        india_facilities = len(india_df)
        st.metric("Total Facilities", india_facilities)

    st.markdown("---")

    # City-wise analysis
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏙️ PUE by City")
        import plotly.express as px

        city_avg = india_df.groupby('city')['pue_value'].mean().reset_index()
        city_avg = city_avg.sort_values('pue_value')

        fig = px.bar(
            city_avg,
            x='city',
            y='pue_value',
            title='Average PUE by Indian City',
            labels={'pue_value': 'Average PUE', 'city': 'City'},
            color='pue_value',
            color_continuous_scale='RdYlGn_r'
        )
        fig.update_xaxis(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🏢 Top Operators")

        company_avg = india_df.groupby('company').agg({
            'pue_value': 'mean',
            'facility_name': 'count'
        }).reset_index()
        company_avg.columns = ['company', 'avg_pue', 'facility_count']
        company_avg = company_avg.sort_values('avg_pue')

        fig = px.bar(
            company_avg.head(10),
            x='company',
            y='avg_pue',
            title='Top 10 Indian Operators by PUE',
            labels={'avg_pue': 'Average PUE', 'company': 'Company'},
            color='avg_pue',
            color_continuous_scale='RdYlGn_r'
        )
        fig.update_xaxis(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

    # Facility table
    st.markdown("---")
    st.subheader("📋 Indian Facilities")

    display_df = india_df[['company', 'facility_name', 'city', 'pue_value', 'pue_type',
                            'capacity_mw', 'rack_count']].copy()
    display_df = display_df.sort_values('pue_value')

    st.dataframe(display_df, use_container_width=True, height=300)

    # Cost analysis
    st.markdown("---")
    st.subheader("💰 Waste Cost Analysis")

    india_df_with_capacity = india_df[india_df['capacity_mw'].notna()].copy()

    if len(india_df_with_capacity) > 0:
        # Calculate waste
        india_df_with_capacity['annual_waste_mwh'] = (
            (india_df_with_capacity['pue_value'] - 1.0) *
            india_df_with_capacity['capacity_mw'] * 8760
        )
        india_df_with_capacity['annual_cost_crores'] = (
            india_df_with_capacity['annual_waste_mwh'] * 1000 * 7.0 / 10000000
        )

        total_waste = india_df_with_capacity['annual_cost_crores'].sum()

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Annual Waste Cost", f"₹{total_waste:.2f} Crores")

        with col2:
            potential_savings = india_df_with_capacity.apply(
                lambda row: max(0, (row['pue_value'] - 1.2) * row['capacity_mw'] * 8760 * 1000 * 7.0 / 10000000),
                axis=1
            ).sum()
            st.metric("Potential Savings (to PUE 1.2)", f"₹{potential_savings:.2f} Crores")


def show_roi_calculator():
    """Interactive ROI calculator."""
    st.title("💰 PUE Improvement ROI Calculator")
    st.markdown("Calculate potential savings from PUE optimization")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📥 Inputs")

        current_pue = st.number_input(
            "Current PUE",
            min_value=1.0,
            max_value=3.0,
            value=1.5,
            step=0.1,
            help="Your facility's current Power Usage Effectiveness"
        )

        target_pue = st.number_input(
            "Target PUE",
            min_value=1.0,
            max_value=current_pue,
            value=1.2,
            step=0.1,
            help="Desired PUE after optimization"
        )

        capacity_mw = st.number_input(
            "IT Capacity (MW)",
            min_value=0.1,
            max_value=500.0,
            value=10.0,
            step=0.5,
            help="IT equipment power capacity in megawatts"
        )

        tariff = st.number_input(
            "Electricity Tariff (₹/kWh)",
            min_value=1.0,
            max_value=20.0,
            value=7.0,
            step=0.5,
            help="Industrial electricity rate in INR per kWh"
        )

    with col2:
        st.subheader("📤 Results")

        # Calculations
        current_waste_mwh = (current_pue - 1.0) * capacity_mw * 8760
        target_waste_mwh = (target_pue - 1.0) * capacity_mw * 8760
        savings_mwh = current_waste_mwh - target_waste_mwh

        current_cost = current_waste_mwh * 1000 * tariff / 10000000  # Crores
        target_cost = target_waste_mwh * 1000 * tariff / 10000000
        savings_crores = current_cost - target_cost

        # CO2 savings (using India grid factor)
        co2_savings = savings_mwh * 1000 * 0.82 / 1000  # tons

        st.metric("Annual Energy Savings", f"{savings_mwh:,.0f} MWh")
        st.metric("Annual Cost Savings", f"₹{savings_crores:.2f} Crores")
        st.metric("CO₂ Reduction", f"{co2_savings:,.0f} tons/year")

        pue_improvement = ((current_pue - target_pue) / current_pue) * 100
        st.metric("PUE Improvement", f"{pue_improvement:.1f}%")

    # Visualization
    st.markdown("---")
    st.subheader("📊 Cost Comparison")

    import plotly.graph_objects as go

    fig = go.Figure(data=[
        go.Bar(name='Current', x=['Annual Cost'], y=[current_cost], marker_color='#d62728'),
        go.Bar(name='Target', x=['Annual Cost'], y=[target_cost], marker_color='#2ca02c'),
    ])

    fig.update_layout(
        title='Annual Electricity Waste Cost (₹ Crores)',
        yaxis_title='Cost (₹ Crores)',
        barmode='group'
    )

    st.plotly_chart(fig, use_container_width=True)

    # Recommendations
    st.markdown("---")
    st.subheader("💡 Optimization Recommendations")

    if current_pue > 1.8:
        st.error("""
        **High PUE Alert**: Your PUE indicates significant inefficiency.

        **Priority Actions:**
        - Implement hot/cold aisle containment
        - Optimize CRAC/CRAH unit setpoints
        - Deploy economizers for free cooling
        - Upgrade to high-efficiency UPS systems
        """)
    elif current_pue > 1.5:
        st.warning("""
        **Moderate PUE**: Room for improvement.

        **Recommended Actions:**
        - Fine-tune cooling setpoints
        - Improve airflow management
        - Consider liquid cooling for high-density racks
        - Implement real-time monitoring
        """)
    else:
        st.success("""
        **Good PUE**: You're operating efficiently!

        **Continuous Improvement:**
        - Monitor for seasonal variations
        - Optimize based on workload patterns
        - Explore renewable energy integration
        - Benchmark against industry leaders
        """)


if __name__ == "__main__":
    main()
