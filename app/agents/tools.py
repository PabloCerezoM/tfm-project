from newspaper import Article
from typing import Generator
from concurrent.futures import ThreadPoolExecutor
from langgraph.config import get_stream_writer
from agents.state_types import State
from services.memory import load_interests, add_interest, remove_interest
from services.news import fetch_news


# ===============================================================================
# NEWS FETCHING NODE
# ===============================================================================

def is_news_about_interest(llm, article, interests):
    """Check if a news article is related to any of the user's interests."""
    interests_str = ', '.join(interests)
    prompt = [
        {
            "role": "system", 
            "content": f"You are an assistant that determines if a news article is related to any of the following user interests: {interests_str}.\nRespond ONLY with 'yes' or 'no', and if 'yes', indicate which interest(s)."
        },
        {
            "role": "user", 
            "content": f"NEWS:\nTitle: {article['title']}\nContent: {article['content']}"
        }
    ]
    res = llm.invoke(prompt)
    content = res.content.lower()
    if "yes" in content:
        return True, content
    return False, content


def fetch_news_node(state: State) -> State:
    """Fetch news articles from the news service."""
    news = fetch_news(page_size=10, language="en")
    state["news"] = news
    return state


# ===============================================================================
# NEWS FILTERING NODE
# ===============================================================================

def build_tools_filter_news_node(llm):
    """Build a node that filters news based on user interests."""
    def node(state: State) -> State:
        interests = load_interests()
        
        def check_match(n):
            match, _ = is_news_about_interest(llm, n, interests)
            return (n, match)
        
        with ThreadPoolExecutor() as executor:
            news = list(executor.map(check_match, state.get("news", [])))
        
        filtered_news = [n for n, match in news if (match and n["url"])]
        state["news"] = filtered_news
        return state

    return node


# ===============================================================================
# CONTENT SCRAPING AND PROCESSING NODES
# ===============================================================================

def download_article(url):
    """Download and parse article content from URL."""
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        print(f"[DEBUG] Error downloading article: {e}")
        return None


def scrape_content_node(state: State) -> State:
    """Scrape full content for each news article."""
    with ThreadPoolExecutor() as executor:
        state["news"] = list(executor.map(
            lambda n: {**n, "content": download_article(n["url"])},
            state.get("news", [])
        ))
    return state


# ===============================================================================
# ARTICLE SUMMARIZATION NODES
# ===============================================================================

def summarize_article_stream(llm, text) -> Generator[str, None, None]:
    """Generate streaming summary of an article."""
    try:
        prompt = [
            {
                "role": "user",
                "content": f"Summarize the following news article in 2-3 sentences, and only output the summary:\n{text}"
            },
        ]
        stream = llm.stream(prompt)
        for chunk in stream:
            token = getattr(chunk, 'content', None)
            # print(f"[DEBUG] Token recibido del LLM: {token}")
            yield token
    except Exception as e:
        print(f"[DEBUG] Error en summarize_article_stream: {e}")
        yield None


def build_summarize_node(llm):
    """Build a node that summarizes articles with streaming output."""
    def node(state: State):
        writer = get_stream_writer()
        for news_idx, n in enumerate(state.get("news", [])):
            if not n.get("content"):
                print(f"[DEBUG] No content for news item {news_idx}: {n['title']}")
                continue

            summary = ""
            for token in summarize_article_stream(llm, n["content"]):
                if token is None:
                    continue
                writer({"partial_summaries": (news_idx, token)})
                summary += token
            n["summary"] = summary

        return state

    return node


# ===============================================================================
# INTEREST MANAGEMENT NODES
# ===============================================================================

def tool_store_interest_node(state: State) -> State:
    """Add a new interest to the user's interest list."""
    interest = state.get("interest")
    if interest:
        add_interest(interest)
        state["result"] = f"Interest '{interest}' added. Current interests: {load_interests()}"
    else:
        state["result"] = "No interest detected to add."
    return state


def tool_list_interests_node(state: State) -> State:
    """List all current user interests."""
    interests = load_interests()
    if interests:
        state["result"] = "Your current interests: " + ", ".join(interests)
    else:
        state["result"] = "You have no interests stored."
    return state


def tool_remove_interest_node(state: State) -> State:
    """Remove an interest from the user's interest list."""
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