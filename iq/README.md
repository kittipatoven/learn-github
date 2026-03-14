# IQ Analyzer Pro - Advanced Trading Analysis Platform

🧠 **AI-Powered Trading Analysis & Journal Platform**

A comprehensive desktop application for analyzing IQ Option trading performance with advanced AI insights, professional dashboards, and detailed statistics.

## 🌟 Key Features

### 📊 Advanced Analysis
- **Comprehensive Trade Statistics**: Win rate, profit factor, drawdown analysis
- **Time-Based Analytics**: Hourly, daily, weekly performance patterns
- **Risk Metrics**: Sharpe ratio, Sortino ratio, Value at Risk (VaR)
- **Equity Curve Analysis**: Drawdown periods, recovery times
- **Asset Performance**: Detailed breakdown by trading pairs

### 🤖 AI-Powered Insights
- **Multi-Factor Pair Scoring**: Trend, volatility, momentum, historical performance
- **Session Optimization**: Best trading times for each pair
- **News Impact Analysis**: Sentiment-based scoring adjustments
- **Confidence Scoring**: Reliability metrics for AI recommendations
- **Customizable Weights**: Conservative, balanced, aggressive strategies

### 📈 Professional Dashboard
- **Real-Time Updates**: Auto-refresh with live data
- **Interactive Charts**: Equity curves, profit distribution, performance metrics
- **Risk Analysis Dashboard**: Drawdown monitoring, risk indicators
- **AI Insights Panel**: Automated trading recommendations
- **Export Capabilities**: Save reports as PDF/PNG/CSV

### 🎨 Modern Interface
- **Tab-Based Layout**: Organized workflow with dedicated sections
- **Dark/Light Themes**: Customizable appearance
- **Progress Indicators**: Real-time analysis progress
- **Responsive Design**: Adapts to different screen sizes

## 🚀 Quick Start

### Installation

1. **Clone or download** the project to your local directory
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the application**:
   ```bash
   python main.py
   ```

### For Legacy Compatibility

If you're upgrading from the original system, use:
```bash
python app.py
```

This maintains full backward compatibility with existing code.

## 📁 Project Structure

```
iq_analyzer_pro/
├── 📂 core/                    # Business logic
│   ├── data_models.py         # Data structures & models
│   ├── trade_parser.py        # Parse & validate trade data
│   ├── trade_analyzer.py      # Statistical analysis engine
│   ├── ai_engine.py           # AI scoring & analysis
│   └── metrics_calculator.py  # Advanced risk metrics
├── 📂 ui/                      # User interface
│   ├── main_app.py            # Main GUI application
│   ├── components/            # Tab components
│   │   ├── login_tab.py       # Login & data loading
│   │   ├── analysis_tab.py    # Trade analysis
│   │   ├── ai_tab.py          # AI pair analysis
│   │   └── dashboard_tab.py   # Interactive dashboard
│   └── widgets/               # Reusable UI components
│       ├── stats_cards.py     # Statistics display cards
│       └── progress_dialog.py # Progress dialogs
├── 📂 utils/                   # Utilities
│   ├── config.py              # Configuration management
│   ├── logger.py              # Logging system
│   └── helpers.py             # Helper functions
├── 📂 config/                  # Configuration files
│   ├── default_config.json    # Default settings
│   └── ai_weights.json        # AI strategy presets
├── 📂 tests/                   # Unit tests (optional)
├── main.py                    # Application entry point
├── app.py                     # Legacy compatibility
├── ai_pair_analyzer.py        # Legacy AI compatibility
└── requirements.txt           # Dependencies
```

## 📊 Usage Guide

### 1. Loading Trade Data

**Supported Formats:**
- JSON files
- CSV files  
- Excel files (.xlsx, .xls)

**Data Structure:**
```json
{
  "trades": [
    {
      "id": "TRADE_001",
      "timestamp": "2024-01-15 10:30:00",
      "asset": "EUR/USD",
      "trade_type": "CALL",
      "amount": 100.0,
      "payout": 185.0,
      "result": "WIN",
      "profit": 85.0
    }
  ]
}
```

### 2. Running Analysis

1. **Load your trade data** using the Login tab
2. **Set date range** for focused analysis
3. **Click "Run Analysis"** to generate comprehensive statistics
4. **View results** in the Analysis tab with multiple views:
   - Overview with key metrics
   - Detailed statistics by hour/asset
   - Interactive charts and visualizations
   - Complete trade history

### 3. AI Pair Analysis

1. **Configure AI weights** using sliders (or use presets)
2. **Click "Run AI Analysis"** to score trading pairs
3. **Review rankings** with confidence scores and recommendations
4. **Analyze breakdown** of scoring factors
5. **Export AI insights** for further analysis

### 4. Dashboard Monitoring

- **Real-time metrics** with auto-refresh option
- **Interactive charts** showing performance trends
- **Risk indicators** and drawdown monitoring
- **AI recommendations** integration
- **Export dashboard** as image or report

## 🧠 AI Scoring System

The AI engine uses a sophisticated multi-factor scoring model:

### Scoring Components

| Factor | Weight | Description |
|--------|--------|-------------|
| **Trend Analysis** | 25% | Technical trend direction & strength |
| **Volatility** | 20% | Normalized volatility levels |
| **Momentum** | 15% | Price momentum & acceleration |
| **Historical Winrate** | 20% | Past performance data |
| **Session Optimization** | 10% | Best trading times |
| **News Impact** | 10% | Sentiment analysis |

### Strategy Presets

- **Conservative**: Focus on stability & historical performance
- **Balanced**: Equal weight across all factors
- **Aggressive**: Emphasis on momentum & current trends  
- **Scalping**: High volatility & short-term momentum

## 📈 Advanced Metrics

### Risk Analysis
- **Maximum Drawdown**: Peak-to-trough decline
- **Sharpe Ratio**: Risk-adjusted returns
- **Sortino Ratio**: Downside risk-adjusted returns
- **Value at Risk (VaR)**: Potential loss at confidence level
- **Conditional VaR**: Expected loss beyond VaR

### Performance Metrics
- **Profit Factor**: Gross profit / gross loss
- **Win Rate**: Percentage of winning trades
- **Average Win/Loss**: Mean profitable/unprofitable trades
- **Consecutive Wins/Losses**: Maximum streak analysis
- **Recovery Time**: Time to recover from drawdowns

## 🔧 Configuration

### AI Settings
Edit `config/ai_weights.json` to customize scoring strategies:

```json
{
  "custom_strategy": {
    "trend_weight": 0.30,
    "volatility_weight": 0.20,
    "momentum_weight": 0.15,
    "historical_winrate_weight": 0.25,
    "session_weight": 0.05,
    "news_weight": 0.05
  }
}
```

### UI Settings
Configure appearance and behavior in `config/default_config.json`:

```json
{
  "ui": {
    "theme": "dark",
    "color_theme": "blue",
    "window_width": 1200,
    "window_height": 800,
    "auto_refresh_interval": 30
  }
}
```

## 🔄 Legacy Compatibility

The system maintains full backward compatibility:

```python
# Original code still works
from app import start_gui, get_last_df
from ai_pair_analyzer import analyze_best_pairs

def run_analysis():
    # Your existing analysis logic
    pass

def launch_dashboard():
    # Your existing dashboard logic  
    pass

def run_ai():
    # Your existing AI logic
    pass

# Start GUI with original functions
start_gui(run_func=run_analysis, 
          dashboard_func=launch_dashboard, 
          ai_func=run_ai)
```

## 🧪 Testing

Run the test suite (if implemented):

```bash
python -m pytest tests/
```

## 📝 Data Requirements

### Minimum Fields for Trade Analysis
- `id`: Unique trade identifier
- `timestamp`: Trade execution time
- `asset`: Trading pair (e.g., "EUR/USD")
- `trade_type`: "CALL" or "PUT"
- `amount`: Trade amount
- `payout`: Potential payout
- `result`: "WIN", "LOSS", or "DRAW"
- `profit`: Actual profit/loss

### Optional Fields
- `duration`: Trade duration in seconds
- `open_price`: Entry price
- `close_price`: Exit price
- `strike_price`: Strike price

## 🚀 Future Roadmap

### Phase 2 Features
- [ ] **Real-time Data Integration**: Live market data feeds
- [ ] **Web Version**: Browser-based interface
- [ ] **Mobile App**: iOS/Android applications
- [ ] **Multi-Broker Support**: Integration with other platforms
- [ ] **Advanced ML Models**: Deep learning for predictions

### Phase 3 Features
- [ ] **Social Trading**: Share and copy strategies
- [ ] **Backtesting Engine**: Historical strategy testing
- [ ] **Alert System**: Real-time trading notifications
- [ ] **Portfolio Management**: Multi-account tracking
- [ ] **API Access**: Programmatic trading integration

## 🐛 Troubleshooting

### Common Issues

**Q: Application won't start**
- Check Python version (3.8+ recommended)
- Verify all dependencies installed: `pip install -r requirements.txt`
- Check system permissions for installation directory

**Q: Trade data not loading**
- Verify file format (JSON, CSV, Excel supported)
- Check required fields are present
- Ensure proper date formatting (YYYY-MM-DD HH:MM:SS)

**Q: AI analysis returns empty results**
- Ensure sufficient trade history (minimum 10 trades recommended)
- Check market data format and structure
- Verify AI weights are properly configured

**Q: Charts not displaying**
- Install matplotlib: `pip install matplotlib`
- Check system display settings
- Try running in administrator mode

### Performance Optimization

- **Large datasets**: Use date range filtering for faster analysis
- **Memory usage**: Close unused tabs and clear old data
- **Processing speed**: Enable/disable advanced metrics based on needs

## 📞 Support

### Documentation
- Check this README for common issues
- Review code comments for detailed explanations
- Examine configuration files for customization options

### Community
- Report issues via GitHub (if repository is public)
- Share feedback and feature requests
- Contribute to code improvements

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **CustomTkinter**: Modern GUI framework
- **Pandas**: Data analysis library
- **Matplotlib**: Visualization library
- **NumPy**: Numerical computing
- **IQ Option**: Trading platform inspiration

---

**IQ Analyzer Pro** - Transform your trading analysis with AI-powered insights! 🚀
