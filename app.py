import requests
from bs4 import BeautifulSoup 
import random
from flask import Flask, jsonify
import time

app = Flask(__name__)

# Cache settings
cache_duration = 300  # 5 minutes
cached_result = None
last_cache_time = 0

user_agents = [ 
	'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36', 
	'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36', 
	'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36', 
	'Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148', 
	'Mozilla/5.0 (Linux; Android 11; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.72 Mobile Safari/537.36' 
] 
url = 'https://www.brvm.org/fr/cours-actions/0'

def get_stocks_data():
    global cached_result, last_cache_time
    current_time = time.time()
    if cached_result and (current_time - last_cache_time) < cache_duration:
        return cached_result
    
    # Proceed with scraping
    user_agent = random.choice(user_agents) 
    headers = {'User-Agent': user_agent} 
    response = requests.get(url, headers=headers, verify=False) 

    soup = BeautifulSoup(response.text, 'html.parser')

    # Récupérer la date de mise à jour
    date_section = soup.find('section', id='block-tools-date-maj')
    if date_section:
        date_text = date_section.get_text(strip=True)
        # Extraire la partie après "Dernière mise à jour : "
        if "Dernière mise à jour :" in date_text:
            full_date = date_text.split("Dernière mise à jour :")[1].strip()
            # Parser la date: "Jeudi, 15 janvier, 2026 - 14:30"
            parts = full_date.split(' - ')
            if len(parts) == 2:
                date_time = parts[0]  # "Jeudi, 15 janvier, 2026"
                time_part = parts[1]  # "14:30"
                date_parts = date_time.split(', ')
                if len(date_parts) >= 3:
                    date_str = date_parts[1] + ' ' + date_parts[2]  # "15 janvier 2026"
                    day, month_name, year = date_str.split()
                    month_dict = {
                        "janvier": "01", "février": "02", "mars": "03", "avril": "04",
                        "mai": "05", "juin": "06", "juillet": "07", "août": "08",
                        "septembre": "09", "octobre": "10", "novembre": "11", "décembre": "12"
                    }
                    month = month_dict.get(month_name.lower(), "01")
                    datemaj = f"{day}/{month}/{year} {time_part}"
                else:
                    datemaj = ""
            else:
                datemaj = ""
        else:
            datemaj = ""
    else:
        datemaj = ""

    # Cibler la section block-system-main pour récupérer la table des stocks
    section = soup.find('section', id='block-system-main')
    if section:
        table = section.find('table', class_='table')
    else:
        table = None

    if table:
        rows = table.find_all('tr')[1:]  # Skip header row
        data = []
        for row in rows:
            cols = []
            for td in row.find_all('td'):
                # Pour la variation, extraire le texte des spans
                spans = td.find_all('span')
                if spans:
                    text = ' '.join(span.get_text(strip=True) for span in spans if span.get_text(strip=True))
                else:
                    text = td.get_text(strip=True)
                cols.append(text)
            
            if len(cols) >= 7:
                data.append({
                    'symbol': cols[0],
                    'nom': cols[1],
                    'volume': int(cols[2].replace(' ', '')) if cols[2] else 0,
                    'coursveille': float(cols[3].replace(' ', '').replace(',', '.')) if cols[3] else 0.0,
                    'coursouverture': float(cols[4].replace(' ', '').replace(',', '.')) if cols[4] else 0.0,
                    'courscloture': float(cols[5].replace(' ', '').replace(',', '.')) if cols[5] else 0.0,
                    'variation': float(cols[6].replace(',', '.')) if cols[6] else 0.0
                })
    else:
        data = []

    result = {"datemaj": datemaj, "stocks": data}
    cached_result = result
    last_cache_time = current_time
    return result

@app.route('/stocks')
def stocks():
    return jsonify(get_stocks_data())

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)

