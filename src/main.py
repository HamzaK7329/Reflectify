import tkinter as tk
from tkinter import messagebox, Toplevel, Label
import csv
import os
import datetime
import matplotlib.pyplot as plt
import requests
from collections import defaultdict, Counter
import re

# OpenWeatherMap API setup (replace with your actual API key)
WEATHER_API_KEY = 'd3eb81334288359dba4db5610c996049'
CITY_NAME = 'Dubai'
WEATHER_API_URL = 'http://api.openweathermap.org/data/2.5/weather'

DATA_FILE = 'mood_data.csv'  # CSV file to store daily inputs

# Emotion-related words we want to track
emotion_words = [
    "happy", "sad", "excited", "bored", "tired", "fun", "bad", "good", "lazy",
    "energized", "nervous", "anxious", "relaxed", "angry", "frustrated", "content",
    "joyful", "grateful", "stressed", "calm", "hopeful", "annoyed", "upset"
]

# Function to get weather data
def get_weather():
    params = {'q': CITY_NAME, 'appid': WEATHER_API_KEY, 'units': 'metric'}
    response = requests.get(WEATHER_API_URL, params=params)
    if response.status_code == 200:
        weather_data = response.json()
        return weather_data['weather'][0]['description']  # Example: 'clear sky'
    return 'N/A'

# Function to save mood data to CSV
def save_mood(mood_score, reflection):
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    weather = get_weather()

    with open(DATA_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([today, mood_score, weather, reflection])

    messagebox.showinfo("Success", "Mood saved successfully!")

# Function to generate mood trend visualization and save it as an image
def generate_mood_plot(data):
    dates = [entry['Date'] for entry in data]
    mood_scores = [int(entry['Mood Score']) for entry in data]

    plt.figure(figsize=(10, 5))
    plt.plot(dates, mood_scores, marker='o', linestyle='-', color='b')
    plt.title('Mood Trends Over the Past Week')
    plt.xlabel('Date')
    plt.ylabel('Mood Score (1-10)')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('mood_trend.png')  # Save plot as image for GUI display
    plt.close()  # Close the plot to avoid display in CLI

# Function to load data from CSV
def load_data():
    weekly_data = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                weekly_data.append(row)
    return weekly_data[-7:]  # Only last 7 days of data

# Function to calculate the average mood score for each weather type
def calculate_weather_correlation(data):
    weather_mood = defaultdict(list)

    # Collect mood scores for each weather condition
    for entry in data:
        weather = entry['Weather']
        mood_score = int(entry['Mood Score'])
        weather_mood[weather].append(mood_score)

    # Calculate average mood for each weather type
    weather_correlation = {weather: sum(moods) / len(moods) for weather, moods in weather_mood.items()}
    
    return weather_correlation

# Function to analyze reflections and count emotion-related words
def analyze_reflections(data):
    all_reflections = " ".join([entry['Open-Ended Response'].lower() for entry in data])
    
    # Count occurrences of specific emotion words
    word_count = Counter()
    words = re.findall(r'\b\w+\b', all_reflections)  # Find all words in reflections
    
    for word in words:
        if word in emotion_words:  # Only count words from our emotion list
            word_count[word] += 1

    most_common_words = word_count.most_common(10)  # Get top 10 most common emotion words
    return most_common_words

# Function to display the summary in a pop-up window
def show_summary():
    weekly_data = load_data()

    if weekly_data:
        # Create a new pop-up window for the summary
        summary_window = Toplevel()
        summary_window.title("Weekly Summary")

        # Generate mood plot and show it in the summary window
        generate_mood_plot(weekly_data)
        img_label = Label(summary_window)
        img_label.grid(row=0, column=0, columnspan=2, padx=20, pady=10)
        mood_image = tk.PhotoImage(file='mood_trend.png')
        img_label.config(image=mood_image)
        img_label.image = mood_image  # Keep a reference to avoid garbage collection

        # Weather and Mood Correlation
        weather_label = Label(summary_window, text="Weather and Mood Correlation:", font=("Helvetica", 12, "bold"))
        weather_label.grid(row=1, column=0, sticky='w', padx=10)
        row = 2
        weather_correlation = calculate_weather_correlation(weekly_data)
        for weather, avg_mood in weather_correlation.items():
            weather_text = f"{weather.capitalize()}: Average Mood = {avg_mood:.2f}"
            Label(summary_window, text=weather_text).grid(row=row, column=0, sticky='w', padx=20)
            row += 1

        # Reflection Analysis
        reflection_label = Label(summary_window, text="Most Common Emotion Words in Reflections:", font=("Helvetica", 12, "bold"))
        reflection_label.grid(row=row, column=0, sticky='w', padx=10, pady=10)
        row += 1
        reflection_analysis = analyze_reflections(weekly_data)
        for word, count in reflection_analysis:
            reflection_text = f"'{word}' appeared {count} times"
            Label(summary_window, text=reflection_text).grid(row=row, column=0, sticky='w', padx=20)
            row += 1

    else:
        messagebox.showinfo("Info", "No data available for the last week.")

# GUI Setup using Tkinter
class MoodTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MoodMapper - Daily Mood Tracker")
        self.root.geometry('500x400')  # Set initial window size

        # Main heading
        tk.Label(root, text="MoodMapper", font=("Helvetica", 18, "bold")).grid(row=0, column=0, columnspan=2, pady=20)

        # Mood input with radio buttons
        tk.Label(root, text="How's your mood today (1-10)?", font=("Helvetica", 12)).grid(row=1, column=0, padx=20, pady=10, sticky='w')
        self.mood_score = tk.IntVar()  # Variable to store selected mood score
        mood_frame = tk.Frame(root)
        mood_frame.grid(row=1, column=1, padx=20, pady=10)
        for i in range(1, 11):  # Create radio buttons for 1-10 mood scores
            tk.Radiobutton(mood_frame, text=str(i), variable=self.mood_score, value=i).pack(side=tk.LEFT, padx=5)

        # Reflection input (text box)
        tk.Label(root, text="Any thoughts or reflections?", font=("Helvetica", 12)).grid(row=2, column=0, padx=20, pady=10, sticky='w')
        self.reflection_input = tk.Text(root, height=4, width=30, font=("Helvetica", 10))
        self.reflection_input.grid(row=2, column=1, padx=20, pady=10)

        # Save button (using default button styling)
        self.save_button = tk.Button(root, text="Save Mood", command=self.save_mood, font=("Helvetica", 12))
        self.save_button.grid(row=3, column=0, padx=20, pady=20, sticky='w')

        # Weekly Summary button (using default button styling)
        self.summary_button = tk.Button(root, text="Show Weekly Summary", command=show_summary, font=("Helvetica", 12))
        self.summary_button.grid(row=3, column=1, padx=20, pady=20, sticky='e')

    # Save mood function
    def save_mood(self):
        mood_score = self.mood_score.get()
        reflection = self.reflection_input.get("1.0", tk.END).strip()

        if not mood_score:
            messagebox.showerror("Error", "Please select a mood score.")
            return

        save_mood(mood_score, reflection)
        self.reflection_input.delete("1.0", tk.END)
        self.mood_score.set(0)

# Create the root window and run the app
if __name__ == '__main__':
    root = tk.Tk()
    
    # Check if CSV file exists, otherwise create it with headers
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Date', 'Mood Score', 'Weather', 'Open-Ended Response'])

    app = MoodTrackerApp(root)
    root.mainloop()
