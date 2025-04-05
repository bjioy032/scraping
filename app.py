import os
from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

app = Flask(__name__)

# Create a directory to save the scraped data if it doesn't exist
if not os.path.exists('scraped_data'):
    os.makedirs('scraped_data')

# Route to display the HTML form
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle scraping when the form is submitted
@app.route('/scrape', methods=['POST'])
def scrape():
    url = request.form['url']
    if not url:
        return render_template('index.html', message="Please provide a valid URL.", message_type="error")

    try:
        # Send a GET request to fetch the page content
        response = requests.get(url)
        if response.status_code != 200:
            return render_template('index.html', message="Failed to retrieve the webpage.", message_type="error")

        # Parse the page content with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Generate a unique filename based on the domain or URL
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.replace('.', '_')  # Replace dots with underscores for valid filenames
        filename = os.path.join('scraped_data', f"{domain}.txt")

        # Open a text file to write the scraped data
        with open(filename, 'w', encoding='utf-8') as file:
            # Extract headings
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            for heading in headings:
                file.write(f"Heading: {heading.text.strip()}\n\n")

            # Extract dates
            dates = soup.find_all('time')
            for date in dates:
                file.write(f"Date: {date.text.strip()}\n\n")

            # Extract content
            content = soup.find_all(['p', 'div'])
            for paragraph in content:
                file.write(f"Content: {paragraph.text.strip()}\n\n")

        return render_template('index.html', message=f"Data has been scraped and written to '{filename}'.", message_type="success")

    except Exception as e:
        return render_template('index.html', message=f"An error occurred: {e}", message_type="error")

if __name__ == '__main__':
    app.run(debug=True)
