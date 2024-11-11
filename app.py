from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search():
    zip_code = request.json.get("zip")  # Fetch the ZIP code from JSON payload
    if not zip_code:
        return jsonify({"error": "ZIP code is missing"}), 400

    ewg_url = f"https://www.ewg.org/tapwater/search-results.php?zip5={zip_code}&searchtype=zip"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }

    try:
        response = requests.get(ewg_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        # Scrape data points
        results = {}
        featured_utility = soup.find("div", class_="featured-utility")
        
        # Featured utility data
        if featured_utility:
            results['featured'] = {
                'name': featured_utility.find("p").text.strip(),
                'city': featured_utility.find("div", class_="utility-info").find("p").text.strip(),
                'served': featured_utility.find_all("div", class_="utility-info")[2].find("p").text.strip()
            }

        # Additional utilities data
        results['utilities'] = []
        for row in soup.select("table.search-results-table tbody tr"):
            utility = {
                'name': row.find("a").text,
                'city': row.find_all("td")[1].text.strip(),
                'population_served': row.find_all("td")[2].text.strip()
            }
            results['utilities'].append(utility)

        return jsonify(results)

    except requests.exceptions.HTTPError as http_err:
        return jsonify({"error": f"HTTP error occurred: {http_err}"}), 403
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
