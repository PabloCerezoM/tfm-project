from memory import load_interests, add_interest
from news_api import fetch_news

def tool_store_interest(input_dict):
    """Adds an interest to the user's memory."""
    interest = input_dict["interest"]
    add_interest(interest)
    return {"result": f"Interest '{interest}' added. Current interests: {load_interests()}"}

def is_news_about_interest(llm, noticia, intereses):
    intereses_str = ', '.join(intereses)
    prompt = [
        {"role": "system", "content": f"You are an assistant that determines whether a news item is related to any of the following user interests: {intereses_str}.\nRespond ONLY 'yes' or 'no', and if 'yes', indicate which interest(s)."},
        {"role": "user", "content": f"NEWS:\nTitle: {noticia['title']}\nContent: {noticia['content']}"}
    ]
    res = llm.invoke(prompt)
    content = res.content.lower()
    if "yes" in content or "sí" in content or "si" in content:
        return True, content
    return False, content

def tool_fetch_news(input_dict, llm):
    """Filters and returns relevant news according to the user's interests using the LLM."""
    interests = load_interests()
    news = fetch_news(page_size=15, language="en")  # Recent general headlines
    print("[DEBUG] News received from the API BEFORE filtering:")
    for i, n in enumerate(news, 1):
        print(f"News #{i}:\n  Title: {n['title']}\n  Content: {n['content']}\n  Source: {n['source']}\n  URL: {n['url']}\n---")
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
        result = "There is no news for your current interests."
    return {"result": result}
