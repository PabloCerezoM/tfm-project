from services.memory import load_interests, add_interest
from services.news import fetch_news

def tool_store_interest(input_dict):
    """Adds an interest to the user's memory."""
    interest = input_dict["interest"]
    add_interest(interest)
    return {"result": f"Interés '{interest}' añadido. Intereses actuales: {load_interests()}"}

def is_news_about_interest(llm, noticia, intereses):
    intereses_str = ', '.join(intereses)
    prompt = [
        {"role": "system", "content": f"Eres un asistente que determina si una noticia está relacionada con alguno de los siguientes intereses de usuario: {intereses_str}.\nResponde SOLO 'sí' o 'no', y si 'sí', indica con qué interés(s)."},
        {"role": "user", "content": f"NOTICIA:\nTítulo: {noticia['title']}\nContenido: {noticia['content']}"}
    ]
    res = llm.invoke(prompt)
    content = res.content.lower()
    if "yes" in content or "sí" in content or "si" in content:
        return True, content
    return False, content

def tool_fetch_news(input_dict, llm):
    """
    Fetches news articles and filters them based on the user's interests.
    Returns a list of relevant news articles.
    """
    interests = load_interests()
    news = fetch_news(page_size=15, language="en")
    filtered = []
    details = []
    for n in news:
        match, info = is_news_about_interest(llm, n, interests)
        if match:
            filtered.append(n)
            details.append(f"- {n['title']} ({info.strip()})")
    if filtered:
        result = "Relevant news:\n" + "\n".join(details)
    else:
        result = "There's no relevant news for your current interests."
    return {"result": result}
