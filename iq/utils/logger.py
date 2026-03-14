"""
Logger Setup - Configure application logging
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


def setup_logger(name: str = "IQ_Analyzer_Pro", 
                log_level: str = "INFO",
                log_file: Optional[str] = None,
                console_output: bool = True) -> logging.Logger:
    """
    Setup logger for the application
    
    Args:
        name: Logger name
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        console_output: Whether to output to console
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        # Ensure log directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    else:
        # Default log file
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d")
        default_log_file = os.path.join(log_dir, f"iq_analyzer_{timestamp}.log")
        
        file_handler = logging.FileHandler(default_log_file)
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "IQ_Analyzer_Pro") -> logging.Logger:
    """Get existing logger instance"""
    return logging.getLogger(name)


def set_log_level(logger: logging.Logger, level: str):
    """Set logging level for all handlers"""
    log_level = getattr(logging, level.upper())
    logger.setLevel(log_level)
    
    for handler in logger.handlers:
        handler.setLevel(log_level)


def add_file_handler(logger: logging.Logger, log_file: str, level: str = "INFO"):
    """Add file handler to logger"""
    # Ensure log directory exists
    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(getattr(logging, level.upper()))
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)


def log_trade_analysis(logger: logging.Logger, analysis_result):
    """Log trade analysis results"""
    logger.info("=== TRADE ANALYSIS RESULTS ===")
    logger.info(f"Total Trades: {analysis_result.total_trades}")
    logger.info(f"Win Rate: {analysis_result.win_rate:.2%}")
    logger.info(f"Net Profit: ${analysis_result.net_profit:.2f}")
    logger.info(f"Profit Factor: {analysis_result.profit_factor:.2f}")
    logger.info(f"Max Drawdown: {analysis_result.max_drawdown:.2f}%")
    logger.info(f"Best Hour: {analysis_result.best_hour}:00")
    logger.info(f"Best Asset: {analysis_result.best_asset}")
    logger.info(f"Worst Asset: {analysis_result.worst_asset}")
    logger.info("=== END ANALYSIS RESULTS ===")


def log_ai_analysis(logger: logging.Logger, ai_results):
    """Log AI analysis results"""
    logger.info("=== AI ANALYSIS RESULTS ===")
    logger.info(f"Analyzed Pairs: {len(ai_results)}")
    
    for result in ai_results[:5]:  # Top 5
        logger.info(f"{result.rank}. {result.pair}: {result.recommendation} "
                   f"(Score: {result.overall_score:.2f}, Confidence: {result.confidence:.2f})")
    
    logger.info("=== END AI RESULTS ===")


def log_error_with_context(logger: logging.Logger, error: Exception, context: str = ""):
    """Log error with context information"""
    error_msg = f"Error in {context}: {str(error)}" if context else str(error)
    logger.error(error_msg, exc_info=True)


def create_performance_logger(logger_name: str = "performance") -> logging.Logger:
    """Create logger for performance monitoring"""
    perf_logger = logging.getLogger(logger_name)
    perf_logger.setLevel(logging.INFO)
    
    # Create file handler for performance logs
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d")
    log_file = os.path.join(log_dir, f"performance_{timestamp}.log")
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    
    perf_logger.addHandler(file_handler)
    
    return perf_logger


def log_performance(logger: logging.Logger, operation: str, duration: float, details: str = ""):
    """Log performance metrics"""
    message = f"{operation} completed in {duration:.2f}s"
    if details:
        message += f" - {details}"
    
    logger.info(message)
