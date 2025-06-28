def parse_command(message, llm=None):
    """
    Interpreta el mensaje del usuario y determina la acción y los parámetros.
    Si se provee un LLM, se usa para mayor robustez.
    """
    if llm:
        system_prompt = (
            "You are an assistant that interprets user commands about interests and news.\n"
            "If the message is to add an interest, reply as follows:\n"
            '{"action": "store_interest", "interest": "<INTEREST>"}\n'
            "If the message is to show news, reply as follows:\n"
            '{"action": "fetch_news"}\n'
            "Example: input = 'Add IA' -> output = {'action': 'store_interest', 'interest': 'IA'}"
        )
        prompt = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ]
        try:
            result = llm.invoke(prompt)
            # Normaliza la salida a un dict seguro
            import ast
            out = result.content.strip()
            if out.startswith("{") and out.endswith("}"):
                return ast.literal_eval(out)
        except Exception:
            pass  # Si falla, prueba heurística básica abajo

    # Parseo básico si no hay LLM o si falla
    message_lower = message.lower()
    if "añade" in message_lower or "add" in message_lower:
        words = message.split()
        interest = words[-1] if len(words) > 1 else "IA"
        return {"action": "store_interest", "interest": interest}
    elif "muestra" in message_lower or "show" in message_lower or "noticias" in message_lower or "news" in message_lower:
        return {"action": "fetch_news"}
    else:
        return {"action": "unknown"}
