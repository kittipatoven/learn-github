"""
AI Analysis Tab - AI-powered pair analysis and ranking
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
from typing import Optional

from ui.widgets.stats_cards import StatsCards


class AITab:
    """AI analysis and pair ranking tab"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.current_trades = []
        self.ai_results = []
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the AI analysis tab UI"""
        # Configure parent grid
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_rowconfigure(1, weight=1)
        
        # Create control panel
        self.create_control_panel()
        
        # Create results area
        self.create_results_area()
    
    def create_control_panel(self):
        """Create AI analysis control panel"""
        control_frame = ctk.CTkFrame(self.parent)
        control_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        control_frame.grid_columnconfigure(1, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            control_frame,
            text="🤖 AI Pair Analysis",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # AI Model Settings
        settings_frame = ctk.CTkFrame(control_frame)
        settings_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
        settings_frame.grid_columnconfigure(1, weight=1)
        
        # Trend weight
        ctk.CTkLabel(settings_frame, text="Trend Weight:").grid(row=0, column=0, padx=5, pady=5)
        self.trend_weight_var = tk.DoubleVar(value=25)
        self.trend_weight_slider = ctk.CTkSlider(
            settings_frame, 
            from_=0, 
            to=100,
            variable=self.trend_weight_var,
            number_of_steps=100
        )
        self.trend_weight_slider.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.trend_weight_label = ctk.CTkLabel(settings_frame, text="25%")
        self.trend_weight_label.grid(row=0, column=2, padx=5, pady=5)
        
        # Volatility weight
        ctk.CTkLabel(settings_frame, text="Volatility Weight:").grid(row=1, column=0, padx=5, pady=5)
        self.volatility_weight_var = tk.DoubleVar(value=20)
        self.volatility_weight_slider = ctk.CTkSlider(
            settings_frame, 
            from_=0, 
            to=100,
            variable=self.volatility_weight_var,
            number_of_steps=100
        )
        self.volatility_weight_slider.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.volatility_weight_label = ctk.CTkLabel(settings_frame, text="20%")
        self.volatility_weight_label.grid(row=1, column=2, padx=5, pady=5)
        
        # Momentum weight
        ctk.CTkLabel(settings_frame, text="Momentum Weight:").grid(row=2, column=0, padx=5, pady=5)
        self.momentum_weight_var = tk.DoubleVar(value=15)
        self.momentum_weight_slider = ctk.CTkSlider(
            settings_frame, 
            from_=0, 
            to=100,
            variable=self.momentum_weight_var,
            number_of_steps=100
        )
        self.momentum_weight_slider.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.momentum_weight_label = ctk.CTkLabel(settings_frame, text="15%")
        self.momentum_weight_label.grid(row=2, column=2, padx=5, pady=5)
        
        # Historical weight
        ctk.CTkLabel(settings_frame, text="Historical Weight:").grid(row=3, column=0, padx=5, pady=5)
        self.historical_weight_var = tk.DoubleVar(value=20)
        self.historical_weight_slider = ctk.CTkSlider(
            settings_frame, 
            from_=0, 
            to=100,
            variable=self.historical_weight_var,
            number_of_steps=100
        )
        self.historical_weight_slider.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        self.historical_weight_label = ctk.CTkLabel(settings_frame, text="20%")
        self.historical_weight_label.grid(row=3, column=2, padx=5, pady=5)
        
        # Bind slider events
        self.trend_weight_slider.configure(command=self.update_weight_labels)
        self.volatility_weight_slider.configure(command=self.update_weight_labels)
        self.momentum_weight_slider.configure(command=self.update_weight_labels)
        self.historical_weight_slider.configure(command=self.update_weight_labels)
        
        # Analysis buttons
        button_frame = ctk.CTkFrame(control_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=10)
        
        self.analyze_button = ctk.CTkButton(
            button_frame,
            text="🧠 Run AI Analysis",
            command=self.run_ai_analysis,
            width=150
        )
        self.analyze_button.grid(row=0, column=0, padx=5, pady=5)
        
        self.export_button = ctk.CTkButton(
            button_frame,
            text="📤 Export AI Results",
            command=self.export_ai_results,
            width=150
        )
        self.export_button.grid(row=0, column=1, padx=5, pady=5)
        
        self.reset_weights_button = ctk.CTkButton(
            button_frame,
            text="🔄 Reset Weights",
            command=self.reset_weights,
            width=120
        )
        self.reset_weights_button.grid(row=0, column=2, padx=5, pady=5)
        
        # Status
        self.status_label = ctk.CTkLabel(
            control_frame,
            text="Ready for AI analysis",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.grid(row=3, column=0, columnspan=3, pady=5)
    
    def create_results_area(self):
        """Create AI results display area"""
        # Create notebook for different result views
        self.results_notebook = ttk.Notebook(self.parent)
        self.results_notebook.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # Rankings tab
        self.rankings_frame = ctk.CTkFrame(self.results_notebook)
        self.results_notebook.add(self.rankings_frame, text="Rankings")
        self.create_rankings_tab()
        
        # Score breakdown tab
        self.breakdown_frame = ctk.CTkFrame(self.results_notebook)
        self.results_notebook.add(self.breakdown_frame, text="Score Breakdown")
        self.create_breakdown_tab()
        
        # AI insights tab
        self.insights_frame = ctk.CTkFrame(self.results_notebook)
        self.results_notebook.add(self.insights_frame, text="AI Insights")
        self.create_insights_tab()
        
        # Recommendations tab
        self.recommendations_frame = ctk.CTkFrame(self.results_notebook)
        self.results_notebook.add(self.recommendations_frame, text="Recommendations")
        self.create_recommendations_tab()
    
    def create_rankings_tab(self):
        """Create rankings tab"""
        # Configure grid
        self.rankings_frame.grid_columnconfigure(0, weight=1)
        self.rankings_frame.grid_rowconfigure(0, weight=1)
        
        # Create treeview for rankings
        self.rankings_tree_frame = ctk.CTkFrame(self.rankings_frame)
        self.rankings_tree_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.rankings_tree_frame.grid_columnconfigure(0, weight=1)
        self.rankings_tree_frame.grid_rowconfigure(0, weight=1)
        
        # Create treeview
        columns = ('Rank', 'Pair', 'Score', 'Confidence', 'Recommendation', 'Trend', 'Volatility', 'Momentum', 'Historical')
        self.rankings_tree = ttk.Treeview(
            self.rankings_tree_frame, 
            columns=columns, 
            show='headings', 
            height=15
        )
        
        # Configure columns
        column_widths = {'Rank': 50, 'Pair': 80, 'Score': 60, 'Confidence': 80, 'Recommendation': 100, 
                        'Trend': 60, 'Volatility': 70, 'Momentum': 70, 'Historical': 70}
        
        for col in columns:
            self.rankings_tree.heading(col, text=col)
            self.rankings_tree.column(col, width=column_widths.get(col, 100))
        
        # Add scrollbar
        rankings_scrollbar = ttk.Scrollbar(
            self.rankings_tree_frame, 
            orient="vertical", 
            command=self.rankings_tree.yview
        )
        self.rankings_tree.configure(yscrollcommand=rankings_scrollbar.set)
        
        self.rankings_tree.grid(row=0, column=0, sticky="nsew")
        rankings_scrollbar.grid(row=0, column=1, sticky="ns")
    
    def create_breakdown_tab(self):
        """Create score breakdown tab"""
        # Configure grid
        self.breakdown_frame.grid_columnconfigure(0, weight=1)
        self.breakdown_frame.grid_rowconfigure(0, weight=1)
        
        # Create matplotlib figure for score breakdown
        self.breakdown_fig, self.breakdown_axes = plt.subplots(2, 2, figsize=(12, 8))
        self.breakdown_fig.tight_layout(pad=3.0)
        
        # Embed in tkinter
        self.breakdown_canvas = FigureCanvasTkAgg(
            self.breakdown_fig, 
            master=self.breakdown_frame
        )
        self.breakdown_canvas.get_tk_widget().grid(
            row=0, column=0, sticky="nsew", padx=10, pady=10
        )
    
    def create_insights_tab(self):
        """Create AI insights tab"""
        # Configure grid
        self.insights_frame.grid_columnconfigure(0, weight=1)
        self.insights_frame.grid_rowconfigure(0, weight=1)
        
        # Create scrollable frame
        self.insights_scroll = ctk.CTkScrollableFrame(self.insights_frame)
        self.insights_scroll.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Insights will be added dynamically
        self.insight_labels = {}
    
    def create_recommendations_tab(self):
        """Create recommendations tab"""
        # Configure grid
        self.recommendations_frame.grid_columnconfigure(0, weight=1)
        self.recommendations_frame.grid_rowconfigure(0, weight=1)
        
        # Create scrollable frame
        self.recommendations_scroll = ctk.CTkScrollableFrame(self.recommendations_frame)
        self.recommendations_scroll.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Recommendations will be added dynamically
        self.recommendation_labels = {}
    
    def update_weight_labels(self, value):
        """Update weight labels when sliders change"""
        self.trend_weight_label.configure(text=f"{float(self.trend_weight_var.get()):.0f}%")
        self.volatility_weight_label.configure(text=f"{float(self.volatility_weight_var.get()):.0f}%")
        self.momentum_weight_label.configure(text=f"{float(self.momentum_weight_var.get()):.0f}%")
        self.historical_weight_label.configure(text=f"{float(self.historical_weight_var.get()):.0f}%")
    
    def reset_weights(self):
        """Reset weights to default values"""
        self.trend_weight_var.set("25")
        self.volatility_weight_var.set("20")
        self.momentum_weight_var.set("15")
        self.historical_weight_var.set("20")
        self.update_weight_labels(None)
    
    def run_ai_analysis(self):
        """Run AI pair analysis"""
        if not self.app.current_trades:
            messagebox.showwarning("Warning", "No trade data available")
            return
        
        # Update AI engine weights
        from ..core.ai_engine import ScoringWeights
        weights = ScoringWeights(
            trend_weight=float(self.trend_weight_var.get()) / 100,
            volatility_weight=float(self.volatility_weight_var.get()) / 100,
            momentum_weight=float(self.momentum_weight_var.get()) / 100,
            historical_winrate_weight=float(self.historical_weight_var.get()) / 100
        )
        self.app.ai_engine.update_weights(weights)
        
        # Run AI analysis
        self.status_label.configure(text="Running AI analysis...")
        self.analyze_button.configure(state="disabled")
        
        self.app.run_ai_analysis()
    
    def on_trades_loaded(self, trades: list):
        """Handle trades loaded event"""
        self.current_trades = trades
        self.status_label.configure(text=f"Loaded {len(trades)} trades - Ready for AI analysis")
        self.analyze_button.configure(state="normal")
    
    def on_ai_analysis_complete(self, results: list):
        """Handle AI analysis complete event"""
        self.ai_results = results
        self.status_label.configure(text="AI analysis complete")
        self.analyze_button.configure(state="normal")
        
        # Update all tabs
        self.update_rankings_tab()
        self.update_breakdown_tab()
        self.update_insights_tab()
        self.update_recommendations_tab()
    
    def update_rankings_tab(self):
        """Update rankings tab with AI results"""
        if not self.ai_results:
            return
        
        # Clear existing data
        for item in self.rankings_tree.get_children():
            self.rankings_tree.delete(item)
        
        # Add AI results
        for result in self.ai_results:
            values = (
                result.rank,
                result.pair,
                f"{result.overall_score:.2f}",
                f"{result.confidence:.2f}",
                result.recommendation,
                f"{result.trend_score:.1f}",
                f"{result.volatility_score:.1f}",
                f"{result.momentum_score:.1f}",
                f"{result.historical_winrate:.1f}"
            )
            
            # Color code based on recommendation
            if result.recommendation in ["STRONG BUY", "BUY"]:
                tag = 'buy'
            elif result.recommendation == "AVOID":
                tag = 'avoid'
            else:
                tag = 'neutral'
            
            self.rankings_tree.insert('', 'end', values=values, tags=(tag,))
        
        # Configure tags
        self.rankings_tree.tag_configure('buy', background='lightgreen')
        self.rankings_tree.tag_configure('avoid', background='lightcoral')
        self.rankings_tree.tag_configure('neutral', background='lightyellow')
    
    def update_breakdown_tab(self):
        """Update breakdown tab with score visualization"""
        if not self.ai_results:
            return
        
        # Clear existing plots
        for ax in self.breakdown_axes.flat:
            ax.clear()
        
        # Extract data for plotting
        pairs = [result.pair for result in self.ai_results[:10]]  # Top 10
        overall_scores = [result.overall_score for result in self.ai_results[:10]]
        trend_scores = [result.trend_score for result in self.ai_results[:10]]
        volatility_scores = [result.volatility_score for result in self.ai_results[:10]]
        momentum_scores = [result.momentum_score for result in self.ai_results[:10]]
        historical_scores = [result.historical_winrate for result in self.ai_results[:10]]
        
        # Plot 1: Overall scores
        self.breakdown_axes[0, 0].barh(pairs, overall_scores, color='steelblue', alpha=0.7)
        self.breakdown_axes[0, 0].set_title('Overall AI Scores')
        self.breakdown_axes[0, 0].set_xlabel('Score')
        self.breakdown_axes[0, 0].grid(True, alpha=0.3)
        
        # Plot 2: Component scores comparison
        x = range(len(pairs))
        width = 0.2
        
        self.breakdown_axes[0, 1].bar(x, trend_scores, width, label='Trend', alpha=0.7)
        self.breakdown_axes[0, 1].bar([i + width for i in x], volatility_scores, width, label='Volatility', alpha=0.7)
        self.breakdown_axes[0, 1].bar([i + 2*width for i in x], momentum_scores, width, label='Momentum', alpha=0.7)
        self.breakdown_axes[0, 1].bar([i + 3*width for i in x], historical_scores, width, label='Historical', alpha=0.7)
        
        self.breakdown_axes[0, 1].set_title('Component Scores Comparison')
        self.breakdown_axes[0, 1].set_xlabel('Pairs')
        self.breakdown_axes[0, 1].set_ylabel('Score')
        self.breakdown_axes[0, 1].set_xticks([i + 1.5*width for i in x])
        self.breakdown_axes[0, 1].set_xticklabels(pairs, rotation=45, ha='right')
        self.breakdown_axes[0, 1].legend()
        self.breakdown_axes[0, 1].grid(True, alpha=0.3)
        
        # Plot 3: Confidence levels
        confidences = [result.confidence for result in self.ai_results[:10]]
        colors = ['green' if conf >= 70 else 'orange' if conf >= 50 else 'red' for conf in confidences]
        
        self.breakdown_axes[1, 0].bar(pairs, confidences, color=colors, alpha=0.7)
        self.breakdown_axes[1, 0].set_title('AI Confidence Levels')
        self.breakdown_axes[1, 0].set_ylabel('Confidence')
        self.breakdown_axes[1, 0].tick_params(axis='x', rotation=45)
        self.breakdown_axes[1, 0].grid(True, alpha=0.3)
        
        # Plot 4: Score distribution
        all_scores = [result.overall_score for result in self.ai_results]
        self.breakdown_axes[1, 1].hist(all_scores, bins=10, color='skyblue', alpha=0.7, edgecolor='black')
        self.breakdown_axes[1, 1].set_title('Score Distribution')
        self.breakdown_axes[1, 1].set_xlabel('Score')
        self.breakdown_axes[1, 1].set_ylabel('Frequency')
        self.breakdown_axes[1, 1].grid(True, alpha=0.3)
        
        # Adjust layout and refresh
        self.breakdown_fig.tight_layout()
        self.breakdown_canvas.draw()
    
    def update_insights_tab(self):
        """Update insights tab with AI insights"""
        if not self.ai_results:
            return
        
        # Clear existing insights
        for widget in self.insights_scroll.winfo_children():
            widget.destroy()
        
        # Generate insights
        insights = self.generate_ai_insights()
        
        # Add insights to UI
        row = 0
        for insight in insights:
            insight_frame = ctk.CTkFrame(self.insights_scroll)
            insight_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=5)
            insight_frame.grid_columnconfigure(0, weight=1)
            
            insight_label = ctk.CTkLabel(
                insight_frame,
                text=insight,
                font=ctk.CTkFont(size=12),
                justify="left"
            )
            insight_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
            
            row += 1
    
    def update_recommendations_tab(self):
        """Update recommendations tab with AI recommendations"""
        if not self.ai_results:
            return
        
        # Clear existing recommendations
        for widget in self.recommendations_scroll.winfo_children():
            widget.destroy()
        
        # Add recommendations for top pairs
        row = 0
        for result in self.ai_results[:5]:  # Top 5 recommendations
            rec_frame = ctk.CTkFrame(self.recommendations_scroll)
            rec_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=5)
            rec_frame.grid_columnconfigure(0, weight=1)
            
            # Recommendation header
            header_label = ctk.CTkLabel(
                rec_frame,
                text=f"{result.rank}. {result.pair} - {result.recommendation}",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            header_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
            
            # Recommendation details
            details_text = f"""
Score: {result.overall_score:.2f}/100 | Confidence: {result.confidence:.2f}%

Key Factors:
• Trend Analysis: {result.trend_score:.1f}/100
• Volatility: {result.volatility_score:.1f}/100  
• Momentum: {result.momentum_score:.1f}/100
• Historical Performance: {result.historical_winrate:.1f}/100

AI Assessment: {self.get_ai_assessment(result)}
            """
            
            details_label = ctk.CTkLabel(
                rec_frame,
                text=details_text.strip(),
                font=ctk.CTkFont(size=11),
                justify="left"
            )
            details_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
            
            row += 1
    
    def generate_ai_insights(self) -> list:
        """Generate AI insights from results"""
        if not self.ai_results:
            return []
        
        insights = []
        
        # Overall insights
        avg_score = sum(result.overall_score for result in self.ai_results) / len(self.ai_results)
        high_confidence = [r for r in self.ai_results if r.confidence >= 70]
        
        insights.append(f"🔍 AI Analysis Insights")
        insights.append(f"Average AI Score: {avg_score:.2f}/100")
        insights.append(f"High Confidence Pairs: {len(high_confidence)}/{len(self.ai_results)}")
        
        # Top performers
        top_pair = self.ai_results[0]
        insights.append(f"🏆 Top Recommendation: {top_pair.pair} ({top_pair.recommendation})")
        
        # Risk analysis
        avoid_pairs = [r for r in self.ai_results if r.recommendation == "AVOID"]
        if avoid_pairs:
            insights.append(f"⚠️ Pairs to Avoid: {len(avoid_pairs)} ({', '.join([p.pair for p in avoid_pairs[:3]])})")
        
        # Trend analysis
        strong_trends = [r for r in self.ai_results if r.trend_score >= 70]
        if strong_trends:
            insights.append(f"📈 Strong Trending Pairs: {len(strong_trends)}")
        
        # Volatility insights
        optimal_volatility = [r for r in self.ai_results if 60 <= r.volatility_score <= 80]
        insights.append(f"🌊 Optimal Volatility Pairs: {len(optimal_volatility)}")
        
        return insights
    
    def get_ai_assessment(self, result) -> str:
        """Get AI assessment for a pair"""
        if result.overall_score >= 80 and result.confidence >= 70:
            return "Excellent opportunity with high confidence"
        elif result.overall_score >= 70:
            return "Good opportunity with moderate confidence"
        elif result.overall_score >= 60:
            return "Decent opportunity, consider with caution"
        elif result.overall_score <= 40:
            return "High risk, recommended to avoid"
        else:
            return "Neutral approach advised"
    
    def export_ai_results(self):
        """Export AI analysis results"""
        if not self.ai_results:
            messagebox.showwarning("Warning", "No AI results to export")
            return
        
        # Export to CSV
        df = pd.DataFrame([result.to_dict() for result in self.ai_results])
        
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            df.to_csv(file_path, index=False)
            messagebox.showinfo("Success", f"AI results exported to {file_path}")
    
    def refresh_data(self):
        """Refresh displayed data"""
        if self.app.current_trades:
            self.on_trades_loaded(self.app.current_trades)
        
        if self.ai_results:
            self.on_ai_analysis_complete(self.ai_results)
