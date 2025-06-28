import gradio as gr
from agents.agent_core import process_command

def chat_interface(message):
    result = process_command(message)
    return result["result"]

iface = gr.Interface(
    fn=chat_interface,
    inputs=gr.Textbox(lines=2, placeholder="Escribe un comando: Añade IA, Muéstrame noticias..."),
    outputs="text",
    title="Agente de Noticias Personalizado"
)

def launch():
    iface.launch()
