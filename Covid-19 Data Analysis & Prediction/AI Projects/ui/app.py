import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import timedelta
import requests

def load_data(file):
    df = pd.read_csv(file)
    
    date_pattern_cols = [col for col in df.columns if any(char in str(col) for char in ['/', '-']) and any(char.isdigit() for char in str(col))]
    
    if date_pattern_cols and 'date' not in df.columns.str.lower():
        non_date_cols = [col for col in df.columns if col not in date_pattern_cols]
        df_melted = df.melt(id_vars=non_date_cols, value_vars=date_pattern_cols, 
                           var_name='date_str', value_name='cases')
        df_melted['cases'] = pd.to_numeric(df_melted['cases'], errors='coerce').fillna(0)
        df_melted['date'] = pd.to_datetime(df_melted['date_str'], errors='coerce')
        df = df_melted.groupby('date', as_index=False).agg({'cases': 'sum'})
        df = df.dropna(subset=['date']).reset_index(drop=True)
        df = df.sort_values('date').reset_index(drop=True)
        
        if len(df) > 1 and df['cases'].iloc[-1] > df['cases'].iloc[0] * 10:
            df['cases'] = df['cases'].diff().fillna(df['cases'].iloc[0]).clip(lower=0)
        
        df['deaths'] = 0
        df['recovered'] = 0
        
    else:
        df.columns = df.columns.str.lower().str.strip()
        required_cols = ['date', 'cases']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            raise ValueError(f"Missing required columns: {', '.join(missing_cols)}. Found columns: {', '.join(df.columns.tolist()[:10])}...")
        
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        if df['date'].isna().all():
            raise ValueError("Could not parse date column. Please ensure dates are in format YYYY-MM-DD")
        
        df['cases'] = pd.to_numeric(df['cases'], errors='coerce')
        if df['cases'].isna().all():
            raise ValueError("Could not parse cases column. Please ensure it contains numbers")
        
        if 'deaths' not in df.columns:
            df['deaths'] = 0
        else:
            df['deaths'] = pd.to_numeric(df['deaths'], errors='coerce').fillna(0)
        
        if 'recovered' not in df.columns:
            df['recovered'] = 0
        else:
            df['recovered'] = pd.to_numeric(df['recovered'], errors='coerce').fillna(0)
        
        df = df.dropna(subset=['date', 'cases']).reset_index(drop=True)
    
    if len(df) == 0:
        raise ValueError("No valid data rows found after cleaning")
    
    df['cases'] = df['cases'].astype(int)
    df['deaths'] = df['deaths'].astype(int)
    df['recovered'] = df['recovered'].astype(int)
    
    return df

def create_sample_data():
    try:
        url = "https://disease.sh/v3/covid-19/historical/all?lastdays=all"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        cases_dict = data.get('cases', {})
        deaths_dict = data.get('deaths', {})
        recovered_dict = data.get('recovered', {})
        
        df = pd.DataFrame(list(cases_dict.items()), columns=['date', 'cases'])
        df['date'] = pd.to_datetime(df['date'])
        
        if deaths_dict:
            deaths_df = pd.DataFrame(list(deaths_dict.items()), columns=['date', 'deaths'])
            deaths_df['date'] = pd.to_datetime(deaths_df['date'])
            df = df.merge(deaths_df, on='date', how='left')
            df['deaths'] = df['deaths'].fillna(0).astype(int)
        else:
            df['deaths'] = 0
        
        if recovered_dict:
            recovered_df = pd.DataFrame(list(recovered_dict.items()), columns=['date', 'recovered'])
            recovered_df['date'] = pd.to_datetime(recovered_df['date'])
            df = df.merge(recovered_df, on='date', how='left')
            df['recovered'] = df['recovered'].fillna(0).astype(int)
        else:
            df['recovered'] = 0
        
        df = df.sort_values('date').reset_index(drop=True)
        df['cases'] = df['cases'].diff().fillna(df['cases'].iloc[0]).astype(int)
        df['cases'] = df['cases'].clip(lower=0)
        
        if 'deaths' in df.columns:
            df['deaths'] = df['deaths'].diff().fillna(df['deaths'].iloc[0]).astype(int)
            df['deaths'] = df['deaths'].clip(lower=0)
        
        if 'recovered' in df.columns:
            df['recovered'] = df['recovered'].diff().fillna(df['recovered'].iloc[0]).astype(int)
            df['recovered'] = df['recovered'].clip(lower=0)
        
        return df
    except Exception as e:
        st.error(f"Couldn't fetch live data: {str(e)}. Using fallback data.")
        dates = pd.date_range(start='2020-01-01', end='2023-12-31', freq='D')
        cases = np.random.randint(100, 1000, len(dates)) + np.sin(np.arange(len(dates)) * 0.1) * 200
        deaths = cases * 0.02 + np.random.randint(0, 10, len(dates))
        recovered = cases * 0.8 + np.random.randint(0, 50, len(dates))
        
        df = pd.DataFrame({
            'date': dates,
            'cases': cases.astype(int),
            'deaths': deaths.astype(int),
            'recovered': recovered.astype(int)
        })
        return df

def predict_cases(df, days=7):
    if len(df) < 7:
        return None
    
    last_week_avg = df['cases'].tail(7).mean()
    predictions = []
    
    for i in range(days):
        pred = last_week_avg * (1 + 0.05 * np.sin(i * 0.1))
        predictions.append(int(pred))
    
    future_dates = pd.date_range(start=df['date'].max() + timedelta(days=1), periods=days, freq='D')
    return pd.DataFrame({
        'date': future_dates,
        'predicted_cases': predictions
    })

st.title("Covid-19 Data Analysis & Prediction")

st.write("Upload your CSV file or use the demo button to load live data from the API")

if 'data' not in st.session_state:
    st.session_state.data = None

st.header("Upload Data (Optional)")
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

st.header("Or Try the Demo")
if st.button("Load live data from API"):
    with st.spinner("Loading live Covid-19 data from API..."):
        try:
            st.session_state.data = create_sample_data()
            st.success("Live data loaded!")
        except Exception as e:
            st.error(f"Couldn't load live data: {str(e)}")

if uploaded_file is not None:
    with st.spinner("Loading and analyzing your data..."):
        try:
            st.session_state.data = load_data(uploaded_file)
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
            st.session_state.data = None

if st.session_state.data is not None:
    df = st.session_state.data
    
    if 'date' not in df.columns or 'cases' not in df.columns:
        st.error("Data is missing required columns: 'date' and 'cases'. Please check your CSV file.")
        st.write("Available columns:", ', '.join(df.columns.tolist()))
    else:
        st.header("Daily Cases Over Time")
        
        with st.spinner("Generating graph..."):
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(df['date'], df['cases'], label='Daily Cases', color='blue')
            ax.set_xlabel('Date')
            ax.set_ylabel('Number of Cases')
            ax.set_title('Daily Covid-19 Cases Over Time')
            ax.legend()
            ax.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
        
        st.subheader("Quick Stats")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Cases", f"{df['cases'].sum():,}")
        with col2:
            st.metric("Average Daily Cases", f"{df['cases'].mean():.0f}")
        with col3:
            st.metric("Peak Cases", f"{df['cases'].max():,}")
        
        st.header("Year and Quarter Analysis")
        
        df['year'] = df['date'].dt.year
        df['quarter'] = df['date'].dt.quarter
        df['year_quarter'] = df['year'].astype(str) + ' Q' + df['quarter'].astype(str)
        
        st.subheader("Year-wise Cases")
        year_stats = df.groupby('year')['cases'].agg(['sum', 'mean', 'max']).reset_index()
        year_stats.columns = ['Year', 'Total Cases', 'Average Daily Cases', 'Peak Cases']
        
        with st.spinner("Generating year-wise chart..."):
            fig_year, ax_year = plt.subplots(figsize=(10, 5))
            ax_year.bar(year_stats['Year'], year_stats['Total Cases'], color='steelblue')
            ax_year.set_xlabel('Year')
            ax_year.set_ylabel('Total Cases')
            ax_year.set_title('Total Cases by Year')
            ax_year.grid(True, alpha=0.3, axis='y')
            plt.xticks(year_stats['Year'], rotation=0)
            plt.tight_layout()
            st.pyplot(fig_year)
        
        st.write("Year-wise breakdown:")
        st.write(year_stats)
        
        st.subheader("Quarter-wise Cases")
        quarter_stats = df.groupby('year_quarter')['cases'].agg(['sum', 'mean', 'max']).reset_index()
        quarter_stats.columns = ['Year-Quarter', 'Total Cases', 'Average Daily Cases', 'Peak Cases']
        quarter_stats = quarter_stats.sort_values('Year-Quarter')
        
        with st.spinner("Generating quarter-wise chart..."):
            fig_quarter, ax_quarter = plt.subplots(figsize=(12, 5))
            ax_quarter.bar(range(len(quarter_stats)), quarter_stats['Total Cases'], color='coral')
            ax_quarter.set_xlabel('Quarter')
            ax_quarter.set_ylabel('Total Cases')
            ax_quarter.set_title('Total Cases by Quarter')
            ax_quarter.set_xticks(range(len(quarter_stats)))
            ax_quarter.set_xticklabels(quarter_stats['Year-Quarter'], rotation=45, ha='right')
            ax_quarter.grid(True, alpha=0.3, axis='y')
            plt.tight_layout()
            st.pyplot(fig_quarter)
        
        st.write("Quarter-wise breakdown:")
        st.write(quarter_stats)
        
        st.subheader("Data Preview")
        st.write("First few rows of your data:")
        st.write(df[['date', 'cases', 'deaths', 'recovered']].head(10))
        
        st.header("Predictions for Next 30 Days")
        
        with st.spinner("Calculating predictions..."):
            predictions = predict_cases(df, days=30)
            
            if predictions is not None:
                fig2, ax2 = plt.subplots(figsize=(10, 5))
                ax2.plot(df['date'].tail(30), df['cases'].tail(30), label='Historical Cases', color='blue')
                ax2.plot(predictions['date'], predictions['predicted_cases'], label='Predicted Cases', color='red', linestyle='--')
                ax2.set_xlabel('Date')
                ax2.set_ylabel('Number of Cases')
                ax2.set_title('Covid-19 Cases: Historical vs Predicted (Next 30 Days)')
                ax2.legend()
                ax2.grid(True, alpha=0.3)
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig2)
                
                st.write("Prediction details:")
                st.write(predictions)
            else:
                st.warning("Not enough data to make predictions. Need at least 7 days of data.")
else:
    st.info("Waiting for data... Upload a CSV file or wait for live data to load.")

