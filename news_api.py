import os
import requests
from dotenv import load_dotenv

load_dotenv()
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")

def fetch_news(page_size=15, language="en"):
    """
    Devuelve titulares generales recientes (sin filtrar por tema).
    """
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "language": language,
        "pageSize": page_size,
        "apiKey": NEWS_API_KEY,
    }
    resp = requests.get(url, params=params)
    data = resp.json()
    if data.get("status") != "ok":
        print("[DEBUG] Error en la API de noticias:", data)
        return []
    news = []
    for a in data.get("articles", []):
        news.append({
            "title": a.get("title", ""),
            "content": a.get("description", "") or "",
            "url": a.get("url", ""),
            "source": a.get("source", {}).get("name", ""),
        })
    return news
