from flask import Flask, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote

app = Flask(__name__)
CORS(app)

DGFT_URL = "https://dgft.gov.in/CP/?opt=notification"
FIEO_URL = "https://fieo.org/view_detail.php?lang=0&id=0,22&evetype=-1"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def clean_filename(filename):
    filename = unquote(filename)
    return filename.split("/")[-1].replace(".pdf", "").replace("_", " ").replace("-", " ").strip()

def fetch_dgft_notifications():
    resp = requests.get(DGFT_URL, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(resp.content, 'html.parser')
    table = soup.find('table')
    pdfs = []

    if not table:
        return []

    for tr in table.find_all('tr')[1:]:
        cols = [td.get_text(strip=True) for td in tr.find_all('td')]
        link = tr.find('a', href=True)
        if not link or len(cols) < 5:
            continue

        number = cols[1]
        description = cols[3]
        date = cols[4]
        href = link['href']
        full_url = href if href.startswith('http') else f"https://dgft.gov.in{href}"
        title_from_url = clean_filename(href)

        pdfs.append({
            'number': number,
            'title': title_from_url,
            'description': description,
            'date': date,
            'url': full_url
        })

    return pdfs

@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    try:
        return jsonify(fetch_dgft_notifications())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
