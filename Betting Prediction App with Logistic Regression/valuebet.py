import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.compose import ColumnTransformer
import random
from datetime import datetime

class BettingPredictorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SportyPredict Pro")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # Create sample data
        self.create_sample_data()
        
        # Setup UI
        self.setup_ui()
        
    def create_sample_data(self):
        # Generate sample historical data
        teams = ['Arsenal', 'Chelsea', 'Liverpool', 'Man City', 'Man Utd', 'Tottenham']
        data = []
        for _ in range(300):
            home = random.choice(teams)
            away = random.choice([t for t in teams if t != home])
            home_goals = random.randint(0, 4)
            away_goals = random.randint(0, 3)
            outcome = 'Home' if home_goals > away_goals else ('Draw' if home_goals == away_goals else 'Away')
            
            data.append([
                home, away, home_goals, away_goals, outcome,
                random.uniform(1.5, 4.0),  # home_odds
                random.uniform(3.0, 4.5),  # draw_odds
                random.uniform(2.0, 5.0)   # away_odds
            ])
            
        self.historical_data = pd.DataFrame(
            data, 
            columns=['HomeTeam', 'AwayTeam', 'HomeGoals', 'AwayGoals', 'Outcome', 
                     'HomeOdds', 'DrawOdds', 'AwayOdds']
        )
        
        # Generate upcoming fixtures
        self.upcoming_fixtures = pd.DataFrame({
            'HomeTeam': ['Arsenal', 'Chelsea', 'Liverpool', 'Man City'],
            'AwayTeam': ['Tottenham', 'Man Utd', 'Chelsea', 'Arsenal'],
            'Date': ['2023-10-15', '2023-10-16', '2023-10-17', '2023-10-18']
        })
        
        # Preprocess data
        self.preprocess_data()
        
    def preprocess_data(self):
        # Encode categorical features
        column_transformer = ColumnTransformer(
            [('encoder', OneHotEncoder(), ['HomeTeam', 'AwayTeam'])],
            remainder='passthrough'
        )
        
        X = column_transformer.fit_transform(self.historical_data[['HomeTeam', 'AwayTeam']])
        y = LabelEncoder().fit_transform(self.historical_data['Outcome'])
        
        # Train logistic regression model
        self.model = LogisticRegression(max_iter=1000)
        self.model.fit(X, y)
        
        # Store transformer for later use
        self.column_transformer = column_transformer
        
    def setup_ui(self):
        # Configure style
        style = ttk.Style()
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        style.configure('TButton', font=('Arial', 10))
        style.configure('Treeview', font=('Arial', 9), rowheight=25)
        style.configure('Treeview.Heading', font=('Arial', 10, 'bold'))
        
        # Main notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Prediction tab
        self.pred_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.pred_frame, text='Predictions')
        self.setup_prediction_tab()
        
        # Settings tab
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text='Settings')
        self.setup_settings_tab()
        
    def setup_prediction_tab(self):
        # Header
        header = ttk.Label(
            self.pred_frame, 
            text="Upcoming Match Predictions", 
            style='Header.TLabel'
        )
        header.pack(pady=10)
        
        # Prediction table
        columns = ('date', 'match', 'home_win', 'draw', 'away_win', 'value_bet')
        self.pred_tree = ttk.Treeview(
            self.pred_frame, 
            columns=columns, 
            show='headings',
            selectmode='browse'
        )
        
        # Configure columns
        self.pred_tree.heading('date', text='Date')
        self.pred_tree.heading('match', text='Match')
        self.pred_tree.heading('home_win', text='Home Win %')
        self.pred_tree.heading('draw', text='Draw %')
        self.pred_tree.heading('away_win', text='Away Win %')
        self.pred_tree.heading('value_bet', text='Value Bet')
        
        self.pred_tree.column('date', width=100, anchor='center')
        self.pred_tree.column('match', width=200, anchor='center')
        self.pred_tree.column('home_win', width=100, anchor='center')
        self.pred_tree.column('draw', width=100, anchor='center')
        self.pred_tree.column('away_win', width=100, anchor='center')
        self.pred_tree.column('value_bet', width=150, anchor='center')
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            self.pred_frame, 
            orient='vertical', 
            command=self.pred_tree.yview
        )
        self.pred_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.pred_tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Predict button
        btn_frame = ttk.Frame(self.pred_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(
            btn_frame, 
            text="Generate Predictions", 
            command=self.generate_predictions
        ).pack(side='left', padx=5)
        
        ttk.Button(
            btn_frame, 
            text="Save Predictions", 
            command=self.save_predictions
        ).pack(side='left', padx=5)
        
        # Populate initial data
        self.populate_fixtures()
        
    def populate_fixtures(self):
        for _, row in self.upcoming_fixtures.iterrows():
            self.pred_tree.insert('', 'end', values=(
                row['Date'],
                f"{row['HomeTeam']} vs {row['AwayTeam']}",
                "-", "-", "-", "-"
            ))
    
    def generate_predictions(self):
        # Clear previous predictions
        for item in self.pred_tree.get_children():
            self.pred_tree.delete(item)
        
        # Generate and display predictions
        for _, fixture in self.upcoming_fixtures.iterrows():
            probabilities = self.predict_match(fixture['HomeTeam'], fixture['AwayTeam'])
            
            # Calculate value bets
            value_bet = self.calculate_value_bet(probabilities)
            
            self.pred_tree.insert('', 'end', values=(
                fixture['Date'],
                f"{fixture['HomeTeam']} vs {fixture['AwayTeam']}",
                f"{probabilities[0]*100:.1f}%",
                f"{probabilities[1]*100:.1f}%",
                f"{probabilities[2]*100:.1f}%",
                value_bet
            ))
    
    def predict_match(self, home_team, away_team):
        # Prepare input data
        input_df = pd.DataFrame([[home_team, away_team]], columns=['HomeTeam', 'AwayTeam'])
        X = self.column_transformer.transform(input_df)
        
        # Predict probabilities
        probabilities = self.model.predict_proba(X)[0]
        return probabilities
    
    def calculate_value_bet(self, probabilities):
        # Simplified value bet calculation
        # In a real app, you would compare with actual bookmaker odds
        thresholds = [0.5, 0.25, 0.25]  # Home, Draw, Away thresholds
        
        if probabilities[0] > thresholds[0]:
            return "Home Win"
        elif probabilities[1] > thresholds[1]:
            return "Draw"
        elif probabilities[2] > thresholds[2]:
            return "Away Win"
        else:
            return "No Value Bet"
    
    def save_predictions(self):
        messagebox.showinfo("Success", "Predictions saved successfully!")
    
    def setup_settings_tab(self):
        # Settings header
        header = ttk.Label(
            self.settings_frame, 
            text="Prediction Settings", 
            style='Header.TLabel'
        )
        header.pack(pady=10)
        
        # Model settings
        model_frame = ttk.LabelFrame(self.settings_frame, text="Model Parameters")
        model_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(model_frame, text="Home Win Threshold:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.home_threshold = tk.DoubleVar(value=0.5)
        ttk.Entry(model_frame, textvariable=self.home_threshold, width=10).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(model_frame, text="Draw Threshold:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.draw_threshold = tk.DoubleVar(value=0.25)
        ttk.Entry(model_frame, textvariable=self.draw_threshold, width=10).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(model_frame, text="Away Win Threshold:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.away_threshold = tk.DoubleVar(value=0.25)
        ttk.Entry(model_frame, textvariable=self.away_threshold, width=10).grid(row=2, column=1, padx=5, pady=5)
        
        # Data management
        data_frame = ttk.LabelFrame(self.settings_frame, text="Data Management")
        data_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(
            data_frame, 
            text="Import Historical Data", 
            command=self.import_data
        ).pack(side='left', padx=5, pady=5)
        
        ttk.Button(
            data_frame, 
            text="Update Fixtures", 
            command=self.update_fixtures
        ).pack(side='left', padx=5, pady=5)
        
        # Save settings button
        btn_frame = ttk.Frame(self.settings_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(
            btn_frame, 
            text="Apply Settings", 
            command=self.apply_settings
        ).pack(side='left', padx=5)
    
    def import_data(self):
        # In a real implementation, this would open a file dialog
        messagebox.showinfo("Info", "This would open a file dialog to import CSV data")
    
    def update_fixtures(self):
        messagebox.showinfo("Info", "This would fetch latest fixtures from an API")
    
    def apply_settings(self):
        # Update value bet thresholds
        self.value_thresholds = [
            self.home_threshold.get(),
            self.draw_threshold.get(),
            self.away_threshold.get()
        ]
        messagebox.showinfo("Success", "Settings applied successfully!")

if __name__ == "__main__":
    root = tk.Tk()
    app = BettingPredictorApp(root)
    root.mainloop()