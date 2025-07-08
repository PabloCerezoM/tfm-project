import gradio as gr
from agents.agent_graph import process_command_stream
from services.memory import load_interests

# Streaming interface for news processing
def chat_interface_stream(message):
    last_partial = ""
    last_nodos = ""
    last_filter_info = ""
    last_summaries = ""
    print(message)
    for partial, visited, news_info, summaries_info in process_command_stream(message):
        # Format nodes as a single line separated by arrows
        if visited:
            nodos = ' → '.join(str(n) for n in visited)
        else:
            nodos = ''
            
        # Handle filter information - accept any non-empty news_info
        if news_info:
            last_filter_info = news_info
        
        # Handle summaries with token-by-token streaming
        if summaries_info:
            last_summaries = summaries_info
        
        last_partial = partial if partial else last_partial
        last_nodos = nodos if nodos else last_nodos
        
        yield nodos + " ⏳", partial, last_filter_info, last_summaries
    
    # At the end, make sure to show the last valid content
    yield last_nodos, last_partial, last_filter_info, last_summaries

with gr.Blocks() as demo:
    gr.Markdown("# Personalized News Agent")
    with gr.Row():
        with gr.Column():
            with gr.Accordion("Visited nodes", open=False):
                nodos_out = gr.Markdown(label="Nodes visited")
        with gr.Column():
            with gr.Accordion("News filter results", open=False):
                filter_out = gr.Markdown(label="All News with Match Status")
        with gr.Column():
            gr.Markdown("**System information:**")
            chat_out = gr.Markdown(label="System information")
    
    # Nueva fila para los resúmenes
    with gr.Row():
        with gr.Column():
            with gr.Accordion("Article summaries", open=True):
                summaries_out = gr.Markdown(label="Summarized Articles")
    
    chat_in = gr.Textbox(lines=1, placeholder="Type a command: Add something to my interests, Show me news...", label='What do you want?')
    send_btn = gr.Button("Send", variant='primary')

    send_btn.click(chat_interface_stream, inputs=chat_in, outputs=[nodos_out, chat_out, filter_out, summaries_out])

def launch():
    demo.launch(server_name="0.0.0.0")


