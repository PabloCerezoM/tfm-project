import gradio as gr
from agents.agent_graph import process_command, process_command_stream
from services.memory import load_interests

def chat_interface(message):
    result = process_command(message)
    return result["output"]

# Modificada para devolver también los nodos visitados y titulares
# El nuevo output será: nodos, respuesta, titulares filtrados
def chat_interface_stream(message):
    last_partial = ""
    last_nodos = ""
    last_news = ""
    for partial, visited, news_info in process_command_stream(message):
        # Formatea los nodos en una sola línea, separados por flechas
        if visited:
            nodos = ' → '.join(str(n) for n in visited)
        else:
            nodos = ''
        last_partial = partial if partial else last_partial
        last_nodos = nodos if nodos else last_nodos
        last_news = news_info if news_info else last_news
        yield nodos + " ⏳", partial, news_info
    # Al finalizar, asegúrate de mostrar el último contenido válido
    yield last_nodos, last_partial, last_news

# Nueva función para mostrar intereses
def mostrar_intereses():
    intereses = load_interests()
    if intereses:
        return ", ".join(intereses)
    else:
        return "No hay intereses guardados."

with gr.Blocks() as demo:
    gr.Markdown("# Personalized News Agent")
    with gr.Row():
        with gr.Column():
            with gr.Accordion("Visited nodes", open=False):
                nodos_out = gr.Markdown(label="Nodes visited")
        with gr.Column():
            with gr.Accordion("News filter", open=False):
                gr.Markdown()
                news_out = gr.Markdown(label="News Headlines")
        with gr.Column():
            gr.Markdown("**Agent Response:**")
            chat_out = gr.Markdown(label="Agent Response")
    chat_in = gr.Textbox(lines=1, placeholder="Type a command: Add something to my interests, Show me news...", label='What do you want?')
    send_btn = gr.Button("Send", variant='primary')

    send_btn.click(chat_interface_stream, inputs=chat_in, outputs=[nodos_out, chat_out, news_out])

def launch():
    demo.launch(server_name="0.0.0.0")


