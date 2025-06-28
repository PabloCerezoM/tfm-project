from services.news import fetch_news

def test_fetch_news():
    articulos = fetch_news(language="en", page_size=5)
    for n in articulos:
        print(n["title"])

if __name__ == "__main__":
    test_fetch_news()
