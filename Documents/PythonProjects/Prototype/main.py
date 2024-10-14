from flask import Flask, render_template, request, redirect, url_for
from emotion_words import emotion_words
from recommendations import recommendations
import csv
import os
import datetime
import matplotlib
matplotlib.use('Agg')  # Use Agg backend for rendering to files
import matplotlib.pyplot as plt
from collections import defaultdict, Counter
import re
import random

app = Flask(__name__)

# File to store mood data
DATA_FILE = 'mood_data.csv'

# Route for the homepage (mood input form)
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        mood_score = request.form['mood_score']
        reflection = request.form['reflection']
        weather = 'clear sky'  # Replace with actual weather fetching logic if needed

        # Save data to CSV
        with open(DATA_FILE, 'a', newline='') as file:
            writer = csv.writer(file)
            today = datetime.datetime.now().strftime('%Y-%m-%d')
            writer.writerow([today, mood_score, weather, reflection])

        return redirect(url_for('summary'))

    return render_template('index.html')

# Function to load the last 7 days of data
def load_data():
    weekly_data = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                weekly_data.append(row)
    return weekly_data[-7:]  # Only return the last 7 entries

# Route for the summary page (displays mood trends and reflection analysis)
@app.route('/summary')
def summary():
    weekly_data = load_data()

    # Generate mood plot
    generate_mood_plot(weekly_data)

    # Analyze reflection words
    reflection_analysis = analyze_reflections(weekly_data)

    # Weather and mood correlation
    weather_correlation = calculate_weather_correlation(weekly_data)

    return render_template('summary.html', reflection_analysis=reflection_analysis, weather_correlation=weather_correlation, recommendation=random.choice(recommendations))

# Function to generate the mood trend plot
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
    plt.savefig('static/mood_trend.png')
    plt.close()

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

# Function to calculate the average mood score for each weather type
def calculate_weather_correlation(data):
    weather_mood = defaultdict(list)

    for entry in data:
        weather = entry['Weather']
        mood_score = int(entry['Mood Score'])
        weather_mood[weather].append(mood_score)

    weather_correlation = {weather: round(sum(moods) / len(moods), 2) for weather, moods in weather_mood.items()}
    return weather_correlation

if __name__ == '__main__':
    # Initialize CSV file if it doesn't exist
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Date', 'Mood Score', 'Weather', 'Open-Ended Response'])
    
    app.run(debug=True)
