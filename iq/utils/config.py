"""
Configuration Management - Handle application settings
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class AIConfig:
    """AI analysis configuration"""
    trend_weight: float = 0.25
    volatility_weight: float = 0.20
    momentum_weight: float = 0.15
    historical_winrate_weight: float = 0.20
    session_weight: float = 0.10
    news_weight: float = 0.10
    confidence_threshold: float = 0.60


@dataclass
class UIConfig:
    """User interface configuration"""
    theme: str = "dark"
    color_theme: str = "blue"
    window_width: int = 1200
    window_height: int = 800
    auto_refresh_interval: int = 30  # seconds
    show_tooltips: bool = True
    confirm_exit: bool = True


@dataclass
class AnalysisConfig:
    """Analysis configuration"""
    default_date_range_days: int = 30
    min_trades_for_analysis: int = 10
    risk_free_rate: float = 0.02
    confidence_level: float = 0.95
    enable_advanced_metrics: bool = True


@dataclass
class AppConfig:
    """Main application configuration"""
    ai: AIConfig
    ui: UIConfig
    analysis: AnalysisConfig
    data_directory: str = "data"
    export_directory: str = "exports"
    log_level: str = "INFO"
    enable_debug: bool = False


class Config:
    """Configuration manager for IQ Analyzer Pro"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "config/app_config.json"
        self.config = self.load_config()
    
    def load_config(self) -> AppConfig:
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                
                # Create config objects from loaded data
                ai_config = AIConfig(**data.get('ai', {}))
                ui_config = UIConfig(**data.get('ui', {}))
                analysis_config = AnalysisConfig(**data.get('analysis', {}))
                
                return AppConfig(
                    ai=ai_config,
                    ui=ui_config,
                    analysis=analysis_config,
                    data_directory=data.get('data_directory', 'data'),
                    export_directory=data.get('export_directory', 'exports'),
                    log_level=data.get('log_level', 'INFO'),
                    enable_debug=data.get('enable_debug', False)
                )
            except Exception as e:
                print(f"Error loading config: {e}. Using defaults.")
                return self.get_default_config()
        else:
            return self.get_default_config()
    
    def get_default_config(self) -> AppConfig:
        """Get default configuration"""
        return AppConfig(
            ai=AIConfig(),
            ui=UIConfig(),
            analysis=AnalysisConfig(),
            data_directory="data",
            export_directory="exports",
            log_level="INFO",
            enable_debug=False
        )
    
    def save_config(self):
        """Save configuration to file"""
        try:
            # Ensure config directory exists
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            # Convert config to dictionary
            config_dict = {
                'ai': asdict(self.config.ai),
                'ui': asdict(self.config.ui),
                'analysis': asdict(self.config.analysis),
                'data_directory': self.config.data_directory,
                'export_directory': self.config.export_directory,
                'log_level': self.config.log_level,
                'enable_debug': self.config.enable_debug
            }
            
            # Save to file
            with open(self.config_file, 'w') as f:
                json.dump(config_dict, f, indent=2)
            
            print(f"Configuration saved to {self.config_file}")
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def update_ai_config(self, **kwargs):
        """Update AI configuration"""
        for key, value in kwargs.items():
            if hasattr(self.config.ai, key):
                setattr(self.config.ai, key, value)
        self.save_config()
    
    def update_ui_config(self, **kwargs):
        """Update UI configuration"""
        for key, value in kwargs.items():
            if hasattr(self.config.ui, key):
                setattr(self.config.ui, key, value)
        self.save_config()
    
    def update_analysis_config(self, **kwargs):
        """Update analysis configuration"""
        for key, value in kwargs.items():
            if hasattr(self.config.analysis, key):
                setattr(self.config.analysis, key, value)
        self.save_config()
    
    def get_ai_weights(self) -> Dict[str, float]:
        """Get AI scoring weights"""
        return {
            'trend_weight': self.config.ai.trend_weight,
            'volatility_weight': self.config.ai.volatility_weight,
            'momentum_weight': self.config.ai.momentum_weight,
            'historical_winrate_weight': self.config.ai.historical_winrate_weight,
            'session_weight': self.config.ai.session_weight,
            'news_weight': self.config.ai.news_weight
        }
    
    def set_ai_weights(self, weights: Dict[str, float]):
        """Set AI scoring weights"""
        for key, value in weights.items():
            if hasattr(self.config.ai, key):
                setattr(self.config.ai, key, value)
        self.save_config()
    
    def ensure_directories(self):
        """Ensure required directories exist"""
        directories = [
            self.config.data_directory,
            self.config.export_directory,
            "config"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self.config = self.get_default_config()
        self.save_config()
    
    def export_config(self, export_path: str):
        """Export configuration to specified path"""
        try:
            config_dict = {
                'ai': asdict(self.config.ai),
                'ui': asdict(self.config.ui),
                'analysis': asdict(self.config.analysis),
                'data_directory': self.config.data_directory,
                'export_directory': self.config.export_directory,
                'log_level': self.config.log_level,
                'enable_debug': self.config.enable_debug
            }
            
            with open(export_path, 'w') as f:
                json.dump(config_dict, f, indent=2)
            
            print(f"Configuration exported to {export_path}")
        except Exception as e:
            print(f"Error exporting config: {e}")
    
    def import_config(self, import_path: str):
        """Import configuration from specified path"""
        try:
            with open(import_path, 'r') as f:
                data = json.load(f)
            
            # Update current config
            ai_config = AIConfig(**data.get('ai', {}))
            ui_config = UIConfig(**data.get('ui', {}))
            analysis_config = AnalysisConfig(**data.get('analysis', {}))
            
            self.config = AppConfig(
                ai=ai_config,
                ui=ui_config,
                analysis=analysis_config,
                data_directory=data.get('data_directory', 'data'),
                export_directory=data.get('export_directory', 'exports'),
                log_level=data.get('log_level', 'INFO'),
                enable_debug=data.get('enable_debug', False)
            )
            
            self.save_config()
            print(f"Configuration imported from {import_path}")
        except Exception as e:
            print(f"Error importing config: {e}")


# Global configuration instance
config = Config()
