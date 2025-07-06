from newspaper import Article

url = "https://elpais.com/clima-y-medio-ambiente/2025-06-28/la-primera-ola-de-calor-arranca-con-el-75-de-los-municipios-en-niveles-de-riesgo-para-la-salud.html"
article = Article(url)
article.download()
article.parse()
print(article.title)      # El título real
print(article.text)       # El cuerpo limpio de la noticia
