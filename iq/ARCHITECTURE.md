# IQ Analyzer Pro - System Architecture

## Current Problems Analysis

### Issues in Original Architecture:
1. **Monolithic Structure**: All logic mixed in single files
2. **UI Coupling**: Business logic tightly coupled with GUI
3. **Simplistic AI**: Basic scoring without normalization
4. **Limited Analytics**: Basic statistics only
5. **No Separation**: Data parsing, analysis, and presentation mixed
6. **Hard to Test**: No modular structure for unit testing
7. **Not Scalable**: Difficult to extend to web or mobile

## Improved Architecture

### Project Structure:
```
iq_analyzer_pro/
├── core/
│   ├── __init__.py
│   ├── trade_parser.py          # Parse IQ Option trade data
│   ├── trade_analyzer.py        # Statistical analysis
│   ├── ai_engine.py            # AI scoring engine
│   ├── data_models.py          # Data structures and models
│   └── metrics_calculator.py   # Calculate trading metrics
├── ui/
│   ├── __init__.py
│   ├── main_app.py             # Main GUI application
│   ├── components/
│   │   ├── __init__.py
│   │   ├── login_tab.py
│   │   ├── analysis_tab.py
│   │   ├── ai_tab.py
│   │   └── dashboard_tab.py
│   └── widgets/
│       ├── __init__.py
│       ├── stats_cards.py
│       └── progress_dialog.py
├── services/
│   ├── __init__.py
│   ├── iq_api.py               # IQ Option API integration
│   ├── news_api.py             # News data integration
│   └── data_storage.py         # Data persistence
├── utils/
│   ├── __init__.py
│   ├── config.py               # Configuration management
│   ├── logger.py               # Logging utilities
│   └── helpers.py              # Helper functions
├── tests/
│   ├── __init__.py
│   ├── test_trade_parser.py
│   ├── test_ai_engine.py
│   └── test_trade_analyzer.py
├── config/
│   ├── default_config.json
│   └── ai_weights.json
├── main.py                     # Application entry point
└── requirements.txt
```

## Data Flow Architecture

```
Input Sources → Data Processing → Analysis Engine → Presentation Layer

1. Input Sources:
   - IQ Option API
   - Trade History Files
   - News APIs
   - User Configuration

2. Data Processing:
   - Trade Parser (core/trade_parser.py)
   - Data Validation
   - Data Cleaning
   - Feature Engineering

3. Analysis Engine:
   - Statistical Analysis (core/trade_analyzer.py)
   - AI Scoring (core/ai_engine.py)
   - Metrics Calculation (core/metrics_calculator.py)

4. Presentation Layer:
   - GUI Components (ui/)
   - Dashboard
   - Reports
   - Export Functions
```

## Core Components Responsibility

### 1. Trade Parser (core/trade_parser.py)
- Parse IQ Option trade history
- Data validation and cleaning
- Feature extraction
- Data type conversion

### 2. Trade Analyzer (core/trade_analyzer.py)
- Calculate trading statistics
- Performance metrics
- Risk analysis
- Time-based analysis

### 3. AI Engine (core/ai_engine.py)
- Pair scoring algorithm
- Multi-factor analysis
- Normalized scoring
- Confidence calculation

### 4. Main App (ui/main_app.py)
- GUI orchestration
- Tab management
- Event handling
- State management

## Improved AI Scoring Model

### New Scoring Factors:
1. **Trend Score** (25%): Technical trend analysis
2. **Volatility Score** (20%): Normalized volatility
3. **Momentum Score** (15%): Price momentum
4. **Historical Winrate** (20%): Historical performance
5. **Session Score** (10%): Trading session optimization
6. **News Impact** (10%): News sentiment penalty/bonus

### Score Normalization:
- All scores normalized to 0-100 scale
- Weighted combination for final score
- Confidence interval calculation
- Ranking with statistical significance

## Key Improvements

### 1. Modular Design
- Separation of concerns
- Testable components
- Reusable modules
- Clear interfaces

### 2. Enhanced Analytics
- Time-based analysis (hourly, daily, weekly)
- Risk-reward analysis
- Equity curve calculation
- Drawdown analysis

### 3. Professional UI
- Tab-based interface
- Real-time progress indicators
- Interactive charts
- Export capabilities

### 4. Extensibility
- Plugin architecture for AI models
- Configurable scoring weights
- Multiple data sources
- API for external integration

## Compatibility Layer

Maintains backward compatibility with existing functions:
- `run_func` → Trade analysis workflow
- `dashboard_func` → Dashboard launch
- `ai_func` → AI pair analysis

## Future Scalability

Architecture supports:
- Web version deployment
- Mobile app development
- Real-time data streaming
- Machine learning model integration
- Multi-broker support
