import gradio as gr
from agents.agent_graph import process_command

def chat_interface(message):
    # process_command puede devolver un generador (streaming) o un dict normal (casos no-streaming)
    result_or_gen = process_command(message)

    # Si es un generador (fetch_news), vamos generando la respuesta principal
    if hasattr(result_or_gen, '__iter__') and not isinstance(result_or_gen, dict):
        partial = ""
        # El diagrama sólo se muestra al final, después de consumir todo el streaming
        final_visited = []
        for out in result_or_gen:
            # out puede ser solo el texto, o un dict si quieres devolver también 'visited_nodes'
            if isinstance(out, dict):
                text = out.get("output", "")
                visited = out.get("visited_nodes", [])
            else:
                text = out
                visited = []
            partial = text  # mostramos el texto parcial
            final_visited = visited or final_visited  # nos quedamos con el último visited si lo hay
            yield partial, ""  # Solo la respuesta principal en streaming, grafo vacío temporalmente
        # Al final del streaming, mostramos el diagrama de nodos completo
        nodes_list = [
            "parse_command",
            "store_interest",
            "fetch_news",
            "final_output"
        ]
        diagram = ""
        for node in nodes_list:
            if node in final_visited:
                diagram += f"**➡️ {node}**\n\n"
            else:
                diagram += f"{node}\n\n"
        yield partial, diagram
    else:
        # Para acciones no streaming (añadir, borrar, etc.)
        result = result_or_gen
        visited = result.get("visited_nodes", [])
        nodes_list = [
            "parse_command",
            "store_interest",
            "fetch_news",
            "final_output"
        ]
        diagram = ""
        for node in nodes_list:
            if node in visited:
                diagram += f"**➡️ {node}**\n\n"
            else:
                diagram += f"{node}\n\n"
        yield result["output"], diagram


iface = gr.Interface(
    fn=chat_interface,
    inputs=gr.Textbox(lines=2, placeholder="Type a command: Add AI, Show me news..."),
    outputs=[
        gr.Markdown(label="Agent Response"),
        gr.Markdown(label="Graph Node Path")
    ],
    title="Personalized News Agent"
)

def launch():
    iface.launch()


