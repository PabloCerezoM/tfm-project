import gradio as gr
from langgraph_agent import process_command

def chat_interface(message):
    return process_command(message)

iface = gr.Interface(
    fn=chat_interface,
    inputs=gr.Textbox(lines=2, placeholder="Escribe un comando: Añade IA, Muéstrame noticias..."),
    outputs="text",
    title="Agente de Noticias Personalizado"
)

def launch():
    iface.launch()
