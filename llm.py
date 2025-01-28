import ollama


def generate_response(message: str):
    for chunk in ollama.chat(
        model="deepseek-r1",
        messages=[
            {"role": "user", "content": message},
        ],
        stream=True,
    ):
        content = chunk.message.content
        yield content


if __name__ == "__main__":
    for token in generate_response("Hello, how are you?"):
        print(token)
