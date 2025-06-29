from newspaper import Article

from agents.state_types import State
from services.memory import load_interests, add_interest, remove_interest
from services.news import fetch_news

def summarize_article_stream(llm, url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        text = article.text
        if not text:
            yield None
            return
        prompt = [
            {"role": "system", "content": "Summarize the following news article in 3-4 sentences:"},
            {"role": "user", "content": text},
        ]
        summary = ""
        for chunk in llm.stream(prompt):
            summary += chunk.content
            yield summary
    except Exception:
        yield None


def tool_store_interest_node(state: State) -> State:
    interest = state.get("interest")
    if interest:
        add_interest(interest)
        state["result"] = f"Interest '{interest}' added. Current interests: {load_interests()}"
    else:
        state["result"] = "No interest detected to add."
    return state

def is_news_about_interest(llm, article, interests):
    interests_str = ', '.join(interests)
    prompt = [
        {"role": "system", "content": f"You are an assistant that determines if a news article is related to any of the following user interests: {interests_str}.\nRespond ONLY with 'yes' or 'no', and if 'yes', indicate which interest(s)."},
        {"role": "user", "content": f"NEWS:\nTitle: {article['title']}\nContent: {article['content']}"}
    ]
    res = llm.invoke(prompt)
    content = res.content.lower()
    if "yes" in content:
        return True, content
    return False, content

def tool_fetch_news_node_stream(llm):
    def node(state: State):
        interests = load_interests()
        news = fetch_news(page_size=5, language="en")
        details = []
        found_any = False

        for n in news:
            match, _ = is_news_about_interest(llm, n, interests)
            if match and n["url"]:
                found_any = True
                title_link = f"**[{n['title']}]({n['url']})**\n"
                # Streaming summary
                summary_stream = summarize_article_stream(llm, n["url"])
                summary_accum = ""
                for partial in summary_stream:
                    if partial is None:
                        yield title_link + "(Could not summarize this article)\n"
                        break
                    summary_accum = partial
                    yield title_link + summary_accum + "\n"
                yield "---\n"
        if not found_any:
            yield "There is no news for your current interests."
    return node


def tool_list_interests_node(state: State) -> State:
    interests = load_interests()
    if interests:
        state["result"] = "Your current interests: " + ", ".join(interests)
    else:
        state["result"] = "You have no interests stored."
    return state

def tool_remove_interest_node(state: State) -> State:
    interest = state.get("interest")
    if interest:
        removed = remove_interest(interest)
        if removed:
            state["result"] = f"Interest '{interest}' removed. Current interests: {load_interests()}"
        else:
            state["result"] = f"Interest '{interest}' not found in your current interests."
    else:
        state["result"] = "No interest detected to remove."
    return state