# Covid-19 Data Analysis & Prediction

A web app I built to analyze Covid-19 data and make predictions. It's pretty straightforward - you can either use live data from an API or upload your own CSV file, and it automatically shows you graphs, stats, and predictions.

## What This Does

I made this tool to help visualize Covid-19 case trends and see what might happen in the future. Once you load data (either from the API or your own file), it automatically:

- Shows you a graph of daily cases over time
- Calculates basic stats like total cases, averages, and peaks
- Breaks down the data by year and quarter
- Predicts cases for the next 30 days

Everything happens automatically - no need to click through multiple buttons or wait around. Just load the data and watch it work!

## Getting Started

### Installation

First, make sure you have Python installed. Then install the required packages:

```bash
pip install -r requirements.txt
```

### Running the App

Just run this command:

```bash
streamlit run ui/app.py
```

The app will open in your browser automatically. Usually at `http://localhost:8501`.

## How to Use

### Option 1: Use Live Data

Click the "Load live data from API" button. It fetches real Covid-19 data from the disease.sh API, which has global case data. This is great if you just want to see how it works or analyze current trends.

### Option 2: Upload Your Own Data

Upload a CSV file with your data. The app supports two formats:

**Format 1: Standard format (long format)**
Your CSV should have these columns:
- `date` - Date in format YYYY-MM-DD (or any date format pandas can read)
- `cases` - Number of daily cases
- `deaths` - Number of daily deaths (optional)
- `recovered` - Number of daily recovered (optional)

Example:
```
date,cases,deaths,recovered
2020-01-01,100,2,80
2020-01-02,150,3,120
```

**Format 2: Wide format (like Johns Hopkins data)**
If you have data where dates are column headers (like "1/21/20", "1/22/20", etc.), that works too! The app automatically detects this format and converts it. Just make sure your file has location columns (like province/state, country/region) and date columns.

### What Happens Next

Once data is loaded, the app automatically:

1. **Shows daily cases graph** - A line chart of cases over time
2. **Displays quick stats** - Total cases, average daily cases, and peak cases
3. **Year-wise analysis** - Bar chart and table showing cases broken down by year
4. **Quarter-wise analysis** - Bar chart and table showing cases by quarter (Q1, Q2, Q3, Q4)
5. **30-day predictions** - A forecast of what cases might look like in the next month

All of this happens automatically with nice loading indicators, so you know what's happening.

## Features

- **Live API integration** - Fetch real-time Covid-19 data with one click
- **Flexible CSV support** - Works with both standard and wide-format CSV files
- **Automatic analysis** - No buttons to click, everything runs automatically
- **Year and quarter breakdowns** - See trends by year and quarter
- **30-day predictions** - Get a forecast of future cases
- **Clean, simple interface** - Easy to use, no clutter

## Technical Details

The prediction model uses a simple moving average approach - it looks at the last week of data and projects forward. It's not super sophisticated, but it works well for basic trend analysis and learning purposes.

For the API data, I'm using the disease.sh API which provides global Covid-19 statistics. The app automatically converts cumulative data to daily new cases for better visualization.

## Notes

This is a learning project I built to practice data analysis and visualization. The prediction model is pretty basic (just moving averages), so don't use it for serious medical or policy decisions. But it's great for:
- Learning about data analysis
- Visualizing Covid-19 trends
- Understanding time series data
- Getting started with Streamlit

If you want to improve it, you could add more sophisticated prediction models, better error handling, or support for more data sources. Feel free to fork it and make it your own!

---

**Author:** Mirza Noor Hamza

