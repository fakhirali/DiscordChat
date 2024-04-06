# this is a fast api llm server
from llama_cpp import Llama
from fastapi import FastAPI, Body
from typing import List

app = FastAPI()

model = Llama(model_path='models/mistral-7b-instruct-v0.2.Q4_K_M.gguf', n_ctx=4096,
              n_gpu_layers=-1,
              verbose=True,
              chat_format='mistral-instruct')


@app.post("/chat")
async def chat(chat_messages: List[dict] = Body(...)):
    # This function now directly accepts messages and bot_name from the request body.
    # Placeholder for processing messages and generating responses.
    print(chat_messages)
    response = model.create_chat_completion(chat_messages)
    return {
        "response": response['choices'][0]['message']['content'],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
