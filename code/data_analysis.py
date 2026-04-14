# -*- coding: utf-8 -*-


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
import warnings
warnings.filterwarnings('ignore')


# Set up matplotlib for better display
plt.rcParams['font.sans-serif'] = ['Arial']
plt.rcParams['axes.unicode_minus'] = False

# ==================== 1. Load Data ====================
def load_data(file_path):
    """
    Read CSV file and convert date format
    """
    df = pd.read_csv(file_path)
    
    # Convert date column to yyyy-mm-dd format
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
    
    # Ensure numeric columns are proper numeric types
    if 'sentiment' in df.columns:
        df['sentiment'] = pd.to_numeric(df['sentiment'], errors='coerce')
    if 'return' in df.columns:
        df['return'] = pd.to_numeric(df['return'], errors='coerce')
    
    print(f"Data loaded: {len(df)} rows")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"Number of stocks: {df['symbol'].nunique() if 'symbol' in df.columns else 'No symbol column'}")
    
    return df

# ==================== 2. Aggregate by Time Window ====================
def aggregate_by_timeframe(df, window_days, date_col='date', symbol_col='symbol'):
    """
    Aggregate data by time window, calculate average sentiment and cumulative return within each window
    
    Parameters:
    - df: DataFrame
    - window_days: Window size in days (e.g., 5 means 5-day windows)
    - date_col: Date column name
    - symbol_col: Stock ticker column name (if exists)
    
    Returns:
    - df_window: Aggregated DataFrame with window_start, window_end, sentiment_mean, return_sum
    """
    df = df.copy()
    df['date'] = pd.to_datetime(df[date_col])
    df = df.sort_values('date')
    
    # Create time window labels
    df['window'] = (df['date'] - df['date'].min()).dt.days // window_days
    
    # Group by window and stock ticker
    if symbol_col in df.columns:
        grouped = df.groupby(['window', symbol_col]).agg({
            'sentiment': 'mean',
            'return': 'sum',  # Cumulative return within window
            'date': ['min', 'max']
        }).reset_index()
    else:
        grouped = df.groupby(['window']).agg({
            'sentiment': 'mean',
            'return': 'sum',
            'date': ['min', 'max']
        }).reset_index()
    
    # Simplify column names
    if symbol_col in df.columns:
        grouped.columns = ['window', 'symbol', 'sentiment_mean', 'return_sum', 'window_start', 'window_end']
    else:
        grouped.columns = ['window', 'sentiment_mean', 'return_sum', 'window_start', 'window_end']
    
    # Convert date format
    grouped['window_start'] = pd.to_datetime(grouped['window_start']).dt.strftime('%Y-%m-%d')
    grouped['window_end'] = pd.to_datetime(grouped['window_end']).dt.strftime('%Y-%m-%d')
    
    return grouped

# ==================== 3. Calculate Correlation ====================
def calculate_correlation(df_aggregated, symbol_col='symbol'):
    """
    Calculate correlation between sentiment_mean and return_sum
    
    Returns: (correlation, p_value, number of data points used)
    """
    # Remove missing values
    df_clean = df_aggregated.dropna(subset=['sentiment_mean', 'return_sum'])
    
    if len(df_clean) < 3:
        return np.nan, np.nan, len(df_clean)
    
    corr, p_val = pearsonr(df_clean['sentiment_mean'], df_clean['return_sum'])
    return corr, p_val, len(df_clean)

# ==================== 4. Plot Scatter with Fitted Line ====================
def plot_scatter(df_aggregated, window_days, title=None, save_path=None):
    """
    Plot sentiment vs returns scatter plot with fitted line
    """
    df_clean = df_aggregated.dropna(subset=['sentiment_mean', 'return_sum'])
    
    if len(df_clean) < 3:
        print(f"Insufficient data points ({len(df_clean)}), cannot plot")
        return
    
    # Calculate correlation
    corr, p_val, n = calculate_correlation(df_aggregated)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Scatter plot
    ax.scatter(df_clean['sentiment_mean'], df_clean['return_sum'], 
               alpha=0.6, s=80, c='steelblue', edgecolors='black')
    
    # Fitted line
    z = np.polyfit(df_clean['sentiment_mean'], df_clean['return_sum'], 1)
    p = np.poly1d(z)
    x_line = np.linspace(df_clean['sentiment_mean'].min(), df_clean['sentiment_mean'].max(), 100)
    y_line = p(x_line)
    ax.plot(x_line, y_line, 'r-', linewidth=2, label=f'Fitted line (slope: {z[0]:.4f})')
    
    # Add correlation information box
    info_text = f'Correlation: {corr:.4f}\nP-value: {p_val:.4f}\nSample size: {n}'
    ax.text(0.05, 0.95, info_text, transform=ax.transAxes, 
           verticalalignment='top', fontsize=12,
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # Set labels and title
    ax.set_xlabel('Sentiment Mean', fontsize=12)
    ax.set_ylabel('Cumulative Return within Window (%)', fontsize=12)
    
    if title:
        ax.set_title(title, fontsize=14, fontweight='bold')
    else:
        ax.set_title(f'Sentiment vs Returns (Time Window: {window_days} days)', fontsize=14, fontweight='bold')
    
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    ax.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    
    plt.show()

# ==================== 5. Multi-Window Analysis ====================
def analyze_multiple_windows(df, window_days_list):
    """
    Analyze multiple time windows, return correlation results for each window
    """
    results = []
    
    for window_days in window_days_list:
        print(f"\n{'='*50}")
        print(f"Analyzing time window: {window_days} days")
        print(f"{'='*50}")
        
        # Aggregate data
        df_agg = aggregate_by_timeframe(df, window_days)
        
        # Calculate correlation
        corr, p_val, n = calculate_correlation(df_agg)
        
        print(f"  Effective samples: {n}")
        print(f"  Correlation coefficient: {corr:.4f}" if not np.isnan(corr) else "  Correlation coefficient: No data")
        print(f"  P-value: {p_val:.4f}" if not np.isnan(p_val) else "  P-value: No data")
        
        # Plot scatter
        plot_scatter(df_agg, window_days, save_path=f"scatter_window_{window_days}d.png")
        
        results.append({
            'window_days': window_days,
            'correlation': corr,
            'p_value': p_val,
            'sample_size': n
        })
    
    return pd.DataFrame(results)

# ==================== 6. Plot Correlation Trend (List Comprehension) ====================
def plot_correlation_trend(results_df):
    """
    Plot correlation and p-value changes over time windows using list comprehension
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Filter valid data using list comprehension
    valid_results = [r for r in results_df.to_dict('records') if not np.isnan(r['correlation'])]
    
    if not valid_results:
        print("No valid data to plot")
        return
    
    windows = [r['window_days'] for r in valid_results]
    correlations = [r['correlation'] for r in valid_results]
    p_values = [r['p_value'] for r in valid_results]
    
    # Correlation trend plot
    ax1.plot(windows, correlations, marker='o', linewidth=2, markersize=8, color='steelblue')
    ax1.axhline(y=0, color='gray', linestyle='-', alpha=0.5)
    ax1.axhline(y=0.5, color='orange', linestyle='--', alpha=0.7, label='Moderate correlation (0.5)')
    ax1.axhline(y=-0.5, color='orange', linestyle='--', alpha=0.7, label='Moderate correlation (-0.5)')
    ax1.set_xlabel('Time Window Size (days)', fontsize=12)
    ax1.set_ylabel('Correlation Coefficient', fontsize=12)
    ax1.set_title('Sentiment-Return Correlation vs Window Size', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # P-value trend plot
    ax2.plot(windows, p_values, marker='s', linewidth=2, markersize=8, color='green', linestyle='--')
    ax2.axhline(y=0.05, color='red', linestyle='--', alpha=0.7, label='Significance threshold (p=0.05)')
    ax2.set_xlabel('Time Window Size (days)', fontsize=12)
    ax2.set_ylabel('P-value', fontsize=12)
    ax2.set_title('Significance Level vs Window Size', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_yscale('log')  # Use log scale for p-values
    
    plt.tight_layout()
    plt.show()

# ==================== 7. Main Function ====================
def main(csv_file_path, window_days_list):
    """
    Main function
    
    Parameters:
    - csv_file_path: Path to CSV file
    - window_days_list: List of time windows, e.g., [3, 7, 14, 30, 60]
    """
    print("="*80)
    print("Sentiment -> Returns Correlation Analysis")
    print("="*80)
    
    # 1. Load data
    print("\n[1] Loading data...")
    df = load_data(csv_file_path)
    
    # 2. Check required columns
    required_cols = ['sentiment', 'return']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        print(f"Error: Missing required columns {missing_cols}")
        print(f"Available columns: {df.columns.tolist()}")
        return None, None
    
    # 3. Multi-window analysis
    print(f"\n[2] Analyzing time windows: {window_days_list} days")
    results_df = analyze_multiple_windows(df, window_days_list)
    
    # 4. Plot trend
    print(f"\n[3] Plotting correlation trends...")
    plot_correlation_trend(results_df)
    
    # 5. Print summary
    print("\n" + "="*80)
    print("Analysis Summary")
    print("="*80)
    print(results_df.to_string(index=False))
    
    return df, results_df

# ==================== Run ====================
if __name__ == "__main__":
    # Please modify this to your CSV file path
    CSV_FILE_PATH = "D:\.anaconda\sentiment_analysis\merged_data.csv"
    
    # Define time windows to analyze (days)
    WINDOW_DAYS_LIST = [3, 7, 14, 30, 60, 90]
    
    # Run analysis
    data, results = main(CSV_FILE_PATH, WINDOW_DAYS_LIST)
