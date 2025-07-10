"""
Data Science Project Template

A comprehensive template for data science projects with visualization,
analysis, and reporting capabilities.
"""

from __future__ import annotations

import logging
import warnings
from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

__version__ = "0.1.0"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("data_analysis.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

def setup_environment() -> None:
    """Configure environment for data science work."""
    # Set matplotlib style
    plt.style.use('seaborn-v0_8')
    sns.set_palette("husl")
    
    # Configure pandas display options
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', 50)
    
    logger.info("Environment configured for data science")

def create_sample_data(n_samples: int = 1000, save_path: str = "data/sample_data.csv") -> pd.DataFrame:
    """Create sample dataset for demonstration."""
    data_dir = Path(save_path).parent
    data_dir.mkdir(exist_ok=True)
    
    # Check if sample data already exists
    sample_file = Path(save_path)
    if sample_file.exists():
        logger.info(f"Loading existing sample data from {sample_file}")
        return pd.read_csv(sample_file)
    
    # Generate synthetic data
    np.random.seed(42)
    
    data = {
        'age': np.random.normal(35, 12, n_samples).astype(int),
        'income': np.random.exponential(50000, n_samples),
        'education_years': np.random.normal(14, 3, n_samples).astype(int),
        'satisfaction_score': np.random.beta(2, 1.5, n_samples) * 10,
        'category': np.random.choice(['A', 'B', 'C', 'D'], n_samples, p=[0.3, 0.25, 0.25, 0.2]),
        'has_feature': np.random.choice([True, False], n_samples, p=[0.4, 0.6])
    }
    
    df = pd.DataFrame(data)
    
    # Add some correlations and clean the data
    df['age'] = np.clip(df['age'], 18, 80)
    df['education_years'] = np.clip(df['education_years'], 8, 20)
    df['income'] = df['income'] * (1 + df['education_years'] / 20)
    
    df.to_csv(sample_file, index=False)
    logger.info(f"Created sample data and saved to {sample_file}")
    
    return df

def analyze_data(df: pd.DataFrame) -> dict:
    """Perform comprehensive data analysis."""
    logger.info("Performing basic analysis...")
    
    analysis = {
        'shape': df.shape,
        'columns': list(df.columns),
        'dtypes': df.dtypes.to_dict(),
        'missing_values': df.isnull().sum().to_dict(),
        'numeric_summary': df.describe().to_dict(),
        'categorical_summary': {}
    }
    
    # Analyze categorical columns
    categorical_cols = df.select_dtypes(include=['object', 'bool']).columns
    for col in categorical_cols:
        analysis['categorical_summary'][col] = df[col].value_counts().to_dict()
    
    return analysis

def create_visualizations(df: pd.DataFrame, output_dir: str = "output") -> list[str]:
    """Create comprehensive visualizations."""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    created_files = []
    
    try:
        # 1. Distribution plots
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Distribution Analysis', fontsize=16)
        
        # Age distribution
        axes[0, 0].hist(df['age'], bins=30, alpha=0.7, color='skyblue', edgecolor='black')
        axes[0, 0].set_title('Age Distribution')
        axes[0, 0].set_xlabel('Age')
        axes[0, 0].set_ylabel('Frequency')
        
        # Income distribution (log scale)
        axes[0, 1].hist(np.log(df['income']), bins=30, alpha=0.7, color='lightgreen', edgecolor='black')
        axes[0, 1].set_title('Income Distribution (Log Scale)')
        axes[0, 1].set_xlabel('Log(Income)')
        axes[0, 1].set_ylabel('Frequency')
        
        # Education years
        axes[1, 0].hist(df['education_years'], bins=15, alpha=0.7, color='coral', edgecolor='black')
        axes[1, 0].set_title('Education Years Distribution')
        axes[1, 0].set_xlabel('Years of Education')
        axes[1, 0].set_ylabel('Frequency')
        
        # Satisfaction score
        axes[1, 1].hist(df['satisfaction_score'], bins=20, alpha=0.7, color='gold', edgecolor='black')
        axes[1, 1].set_title('Satisfaction Score Distribution')
        axes[1, 1].set_xlabel('Satisfaction Score')
        axes[1, 1].set_ylabel('Frequency')
        
        plt.tight_layout()
        dist_file = output_path / "distributions.png"
        plt.savefig(dist_file, dpi=300, bbox_inches='tight')
        plt.close()
        created_files.append(str(dist_file))
        
        # 2. Correlation heatmap
        plt.figure(figsize=(10, 8))
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        correlation_matrix = df[numeric_cols].corr()
        
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
                   square=True, linewidths=0.5)
        plt.title('Correlation Matrix of Numeric Variables')
        plt.tight_layout()
        
        corr_file = output_path / "correlation_heatmap.png"
        plt.savefig(corr_file, dpi=300, bbox_inches='tight')
        plt.close()
        created_files.append(str(corr_file))
        
        # 3. Category analysis
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        
        # Category distribution
        category_counts = df['category'].value_counts()
        axes[0].pie(category_counts.values, labels=category_counts.index, autopct='%1.1f%%',
                   startangle=90, colors=sns.color_palette("husl", len(category_counts)))
        axes[0].set_title('Category Distribution')
        
        # Income by category
        df.boxplot(column='income', by='category', ax=axes[1])
        axes[1].set_title('Income Distribution by Category')
        axes[1].set_xlabel('Category')
        axes[1].set_ylabel('Income')
        
        plt.suptitle('')  # Remove the automatic title
        plt.tight_layout()
        
        cat_file = output_path / "category_analysis.png"
        plt.savefig(cat_file, dpi=300, bbox_inches='tight')
        plt.close()
        created_files.append(str(cat_file))
        
    except Exception as e:
        logger.warning(f"Some visualizations failed: {e}")
    
    return created_files

def generate_report(df: pd.DataFrame, analysis: dict, output_file: str = "output/analysis_report.md") -> str:
    """Generate a comprehensive analysis report."""
    report_path = Path(output_file)
    report_path.parent.mkdir(exist_ok=True)
    
    with open(report_path, 'w') as f:
        f.write("# Data Analysis Report\n\n")
        f.write(f"Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Dataset Overview\n\n")
        f.write(f"- **Shape**: {analysis['shape'][0]} rows, {analysis['shape'][1]} columns\n")
        f.write(f"- **Columns**: {', '.join(analysis['columns'])}\n\n")
        
        f.write("## Data Quality\n\n")
        missing_values = analysis['missing_values']
        if sum(missing_values.values()) == 0:
            f.write("No missing values found!\n\n")
        else:
            f.write("Missing values per column:\n")
            for col, missing in missing_values.items():
                if missing > 0:
                    f.write(f"- {col}: {missing} ({missing/analysis['shape'][0]*100:.1f}%)\n")
            f.write("\n")
        
        f.write("## Numeric Variables Summary\n\n")
        for col, stats in analysis['numeric_summary'].items():
            f.write(f"### {col}\n")
            f.write(f"- Mean: {stats['mean']:.2f}\n")
            f.write(f"- Median: {stats['50%']:.2f}\n")
            f.write(f"- Std: {stats['std']:.2f}\n")
            f.write(f"- Range: {stats['min']:.2f} - {stats['max']:.2f}\n\n")
        
        f.write("## Categorical Variables Summary\n\n")
        for col, counts in analysis['categorical_summary'].items():
            f.write(f"### {col}\n")
            for value, count in counts.items():
                percentage = count / analysis['shape'][0] * 100
                f.write(f"- {value}: {count} ({percentage:.1f}%)\n")
            f.write("\n")
        
        f.write("## Key Insights\n\n")
        f.write("Based on the analysis, here are some key findings:\n\n")
        
        # Calculate some insights
        avg_age = analysis['numeric_summary']['age']['mean']
        avg_income = analysis['numeric_summary']['income']['mean']
        
        f.write(f"1. **Demographics**: Average age is {avg_age:.1f} years\n")
        f.write(f"2. **Economics**: Average income is ${avg_income:,.0f}\n")
        f.write(f"3. **Education**: Most people have {df['education_years'].mode().iloc[0]} years of education\n")
        f.write(f"4. **Satisfaction**: Average satisfaction score is {analysis['numeric_summary']['satisfaction_score']['mean']:.1f}/10\n")
        
    logger.info(f"Analysis report saved to {report_path}")
    return str(report_path)

def main() -> None:
    """Main analysis workflow."""
    print(f"Data Science Template (version {__version__})")
    print("=" * 50)
    
    # Setup environment
    setup_environment()
    
    # Load or create data
    df = create_sample_data(n_samples=1000)
    print(f"Loaded dataset with shape: {df.shape}")
    
    # Perform analysis
    analysis_results = analyze_data(df)
    
    # Create visualizations
    try:
        created_plots = create_visualizations(df)
        print(f"Analysis complete!")
        print(f"Created {len(created_plots)} visualization files")
    except ImportError:
        print("Visualizations skipped (matplotlib might not be available)")
        created_plots = []
    
    # Generate report
    report_file = generate_report(df, analysis_results)
    
    print("Analysis complete! Check the generated files:")
    print(f"  - Report: {report_file}")
    for plot_file in created_plots:
        print(f"  - Plot: {plot_file}")
    
    print("Next steps:")
    print("  1. Review the analysis report")
    print("  2. Examine the generated visualizations")
    print("  3. Customize the analysis for your specific data")
    print("  4. Add your own data sources and analysis methods")

if __name__ == "__main__":
    main()
