import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

# Configure page settings
st.set_page_config(page_title="Carbon-Cost Dashboard", layout="wide")
st.title("🌱 Carbon-Cost Dashboard")

# Backend API configuration
BACKEND_URL: str = "http://localhost:5000"

@st.cache_data(ttl=60)
def fetch_data() -> Optional[Dict[str, Any]]:
    """
    Fetch emission data from the Flask backend API
    
    Returns:
        Dictionary containing emission statistics or None if failed
    """
    try:
        response: requests.Response = requests.get(f"{BACKEND_URL}/stats")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch data: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {e}")
        return None

def create_emissions_dataframe(data: Dict[str, Any]) -> pd.DataFrame:
    """
    Convert API data to pandas DataFrame with proper date handling
    
    Args:
        data: Dictionary containing emissions data from API
        
    Returns:
        DataFrame with processed emission data
    """
    df: pd.DataFrame = pd.DataFrame(data['emissions'])
    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['date'] = df['timestamp'].dt.date
    return df

def filter_data_by_date_range(df: pd.DataFrame, date_range: Tuple[datetime, datetime]) -> pd.DataFrame:
    """
    Filter DataFrame by date range
    
    Args:
        df: Input DataFrame
        date_range: Tuple of (start_date, end_date)
        
    Returns:
        Filtered DataFrame
    """
    if len(date_range) == 2:
        start_date, end_date = date_range
        return df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    return df

def display_metrics(data: Dict[str, Any]) -> None:
    """
    Display key metrics in a 4-column layout
    
    Args:
        data: Dictionary containing emission statistics
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total CO₂", f"{data['total_co2']:.3f} kg")
    
    with col2:
        st.metric("Average CO₂ per Build", f"{data['average_co2']:.3f} kg")
    
    with col3:
        st.metric("Total Builds", len(data['emissions']))
    
    with col4:
        green_count: int = data['badge_counts'].get('Green', 0)
        st.metric("Green Builds", green_count)

def create_badge_breakdown_chart(badge_data: Dict[str, int]) -> None:
    """
    Create and display pie chart for build status breakdown
    
    Args:
        badge_data: Dictionary with badge counts
    """
    st.subheader("Build Status Breakdown")
    badge_colors: Dict[str, str] = {
        'Green': '#00ff00', 
        'Yellow': '#ffff00', 
        'Red': '#ff0000'
    }
    
    fig_pie = px.pie(
        values=list(badge_data.values()),
        names=list(badge_data.keys()),
        color=list(badge_data.keys()),
        color_discrete_map=badge_colors
    )
    fig_pie.update_layout(height=400)
    st.plotly_chart(fig_pie, use_container_width=True)

def create_emissions_trend_chart(filtered_df: pd.DataFrame) -> None:
    """
    Create and display line chart for CO2 emissions over time
    
    Args:
        filtered_df: Filtered DataFrame with emission data
    """
    if filtered_df.empty:
        return
        
    st.subheader("CO₂ Emissions Over Time")
    daily_emissions: pd.DataFrame = filtered_df.groupby('date')['co2'].sum().reset_index()
    
    fig_line = px.line(
        daily_emissions,
        x='date',
        y='co2',
        title="Daily CO₂ Emissions",
        labels={'co2': 'CO₂ (kg)', 'date': 'Date'}
    )
    fig_line.update_layout(height=400)
    st.plotly_chart(fig_line, use_container_width=True)

def create_machine_type_chart(filtered_df: pd.DataFrame) -> None:
    """
    Create and display bar chart for emissions by machine type
    
    Args:
        filtered_df: Filtered DataFrame with emission data
    """
    if filtered_df.empty:
        return
        
    st.subheader("Emissions by Machine Type")
    machine_emissions: pd.DataFrame = filtered_df.groupby('machine_type')['co2'].sum().reset_index()
    
    fig_bar = px.bar(
        machine_emissions,
        x='machine_type',
        y='co2',
        title="CO₂ Emissions by Machine Type",
        labels={'co2': 'CO₂ (kg)', 'machine_type': 'Machine Type'}
    )
    fig_bar.update_layout(height=400)
    st.plotly_chart(fig_bar, use_container_width=True)

def display_recent_builds(filtered_df: pd.DataFrame) -> None:
    """
    Display table of recent builds
    
    Args:
        filtered_df: Filtered DataFrame with emission data
    """
    st.subheader("Recent Builds")
    if not filtered_df.empty:
        recent_builds: pd.DataFrame = filtered_df.sort_values('timestamp', ascending=False).head(10)
        st.dataframe(
            recent_builds[['repo', 'co2', 'duration', 'machine_type', 'badge', 'timestamp']],
            use_container_width=True
        )
    else:
        st.info("No build data available.")

def main() -> None:
    """
    Main function that orchestrates the dashboard
    """
    # Fetch data from backend
    data: Optional[Dict[str, Any]] = fetch_data()
    
    if data is None:
        st.warning("Unable to connect to backend. Please ensure the Flask server is running.")
        return
    
    # Process data
    df: pd.DataFrame = create_emissions_dataframe(data)
    
    # Setup sidebar filters
    st.sidebar.header("Filters")
    
    if not df.empty:
        min_date: datetime = df['date'].min()
        max_date: datetime = df['date'].max()
        date_range: Tuple[datetime, datetime] = st.sidebar.date_input(
            "Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        filtered_df: pd.DataFrame = filter_data_by_date_range(df, date_range)
    else:
        filtered_df: pd.DataFrame = df
    
    # Display dashboard components
    display_metrics(data)
    create_badge_breakdown_chart(data['badge_counts'])
    create_emissions_trend_chart(filtered_df)
    create_machine_type_chart(filtered_df)
    display_recent_builds(filtered_df)
    
    # Refresh functionality
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

if __name__ == "__main__":
    main() 