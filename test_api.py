from news_api import fetch_news
articulos = fetch_news(language="en", page_size=15)
for n in articulos:
    print(n["title"])
