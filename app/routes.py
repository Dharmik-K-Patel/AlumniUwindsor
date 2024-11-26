from flask import Blueprint, render_template, redirect, url_for, flash, request
import pandas as pd
import numpy as np
import os
import time
from .scraper import scrape_and_store_obituaries
from flask import jsonify
from flask import send_file

main = Blueprint('main', __name__)
csv_file = "data.csv"
# In-memory log for scraping updates
scraping_updates = []
stop_flag_file = "stop_flag.txt"

@main.route('/')
def home():
    return render_template('home.html', updates=scraping_updates)

@main.route('/scrape')
def scrape():
    try:
        scrape_and_store_obituaries()
        # Log the update
        scraping_updates.append(f"Scraping of {len(scraping_updates) + 1} data.csv file completed")
        flash("Scraping completed successfully! Data saved to CSV.", "success")
    except Exception as e:
        print(e)
        flash("An error occurred during scraping.", "danger")
    return redirect(url_for('main.home'))

@main.route('/results', methods=['GET'])
def results():
    # Check if the CSV file exists
    if not os.path.exists(csv_file):
        flash("No data available. Please scrape the data first.", "warning")
        return redirect(url_for('main.home'))

    # Load data from CSV
    df = pd.read_csv(csv_file)

    # Replace NaN values with "N/A"
    df.fillna("N/A", inplace=True)

    # Retrieve filter parameters
    first_name = request.args.get('first_name')
    last_name = request.args.get('last_name')
    # date = request.args.get('date')
    keywords = request.args.getlist('keywords')  # Get multiple keyword values as a list
    family_filter = request.args.get('family_mentions')  # New filter for Family Mentions

    # Apply filters
    if first_name:
        df = df[df['First Name'].str.contains(first_name, na=False, case=False)]
    if last_name:
        df = df[df['Last Name'].str.contains(last_name, na=False, case=False)]
    # if date:
    #     df = df[df['Date of Death'] == date]
    if keywords:
        df = df[df['Keyword Mention'].isin(keywords)]
    if family_filter:
        df = df[df['Family Mentions'].str.contains(family_filter, na=False, case=False)]

    # Convert data to list of dictionaries for rendering
    obituaries = df.to_dict(orient="records")

    return render_template('results.html', obituaries=obituaries)

# Get the last modification timestamp of the CSV file
def get_csv_update_status():
    file_path = "data.csv"
    if os.path.exists(file_path):
        # Get the modification time
        last_modified = os.path.getmtime(file_path)
        return f"Scraping of data.csv completed at {time.ctime(last_modified)}"
    return "No scraping has been done yet."

@main.route('/get-updates')
def get_updates():
    status = get_csv_update_status()
    return jsonify({"update": status})

# Set the stop flag
@main.route('/stop-scraper', methods=['POST'])
def stop_scraper():
    with open(stop_flag_file, "w") as f:
        f.write("STOP")
    return jsonify({"status": "Scraper stopping initiated."}), 200

# Check if the stop flag is set
def is_scraper_stopped():
    return os.path.exists(stop_flag_file)

@main.route('/download-csv')
def download_csv():
    file_path = os.path.join(os.getcwd(), "data.csv")
    try:
        return send_file(file_path, as_attachment=True, download_name="data.csv")
    except FileNotFoundError:
        flash("No data.csv file found. Please scrape data first.", "warning")
        return redirect(url_for('main.home'))