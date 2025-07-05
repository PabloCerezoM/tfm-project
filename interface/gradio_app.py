import gradio as gr
from agents.agent_graph import process_command, process_command_stream
from services.memory import load_interests

def chat_interface(message):
    result = process_command(message)
    return result["output"]

# Modificada para devolver también los nodos visitados
def chat_interface_stream(message):
    last_partial = ""
    last_nodos = ""
    for partial, visited in process_command_stream(message):
        # Formatea los nodos en una sola línea, separados por flechas
        if visited:
            nodos = ' → '.join(str(n) for n in visited)
        else:
            nodos = ''
        last_partial = partial if partial else last_partial
        last_nodos = nodos if nodos else last_nodos
        yield nodos + " ⏳", partial
    # Al finalizar, asegúrate de mostrar el último contenido válido
    yield last_nodos, last_partial

# Nueva función para mostrar intereses
def mostrar_intereses():
    intereses = load_interests()
    if intereses:
        return ", ".join(intereses)
    else:
        return "No hay intereses guardados."

with gr.Blocks() as demo:
    gr.Markdown("# Personalized News Agent")
    chat_in = gr.Textbox(lines=2, placeholder="Type a command: Add AI, Show me news...")
    with gr.Row():
        with gr.Column():
            gr.Markdown("**Progreso del grafo:**")
            nodos_out = gr.Markdown(label="Nodos visitados")
        with gr.Column():
            gr.Markdown("**Respuesta del agente:**")
            chat_out = gr.Markdown(label="Agent Response")
    intereses_out = gr.Textbox(label="Show interests", interactive=False)
    with gr.Row():
        send_btn = gr.Button("Send")
        intereses_btn = gr.Button("Show intereses")

    send_btn.click(chat_interface_stream, inputs=chat_in, outputs=[nodos_out, chat_out])
    intereses_btn.click(mostrar_intereses, outputs=intereses_out)

def launch():
    demo.launch()


