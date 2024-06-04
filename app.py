import os
from flask import Flask, request, Response, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import replicate
import openai
from langchain_chroma import Chroma
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from rouge_score import rouge_scorer
import json
import time

# Loading keys
load_dotenv()
replicate_api_key = os.getenv("REPLICATE_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

# Loading vector DB
embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
persist_directory = "./chroma_db"
db = Chroma(persist_directory=persist_directory, embedding_function=embedding_function)

# Initializing clients
replicate_client = replicate.Client(api_token=replicate_api_key)
openai.api_key = openai_api_key

# Function to query Chroma DB
def query_chroma_db(prompt, db, top_k=5):
    docs = db.similarity_search(prompt)
    results = [doc.page_content for doc in docs]
    return results

# Function to query GPT-4
def query_gpt4(combined_prompt):
    system_prompt = """
    You are a helpful assistant. You are only allowed to use the relevant information provided below from the search results to answer the user's query. Do not use any other knowledge or assumptions. If the provided information is insufficient, explain why and indicate the lack of information.
    """
    completion = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": combined_prompt}
        ]
    )
    print("- gpt4 done!")
    return completion.choices[0].message.content

# Function to query GPT-3.5-turbo
def query_gpt3_5_turbo(combined_prompt):
    system_prompt = """
    You are a helpful assistant. You are only allowed to use the relevant information provided below from the search results to answer the user's query. Do not use any other knowledge or assumptions. If the provided information is insufficient, explain why and indicate the lack of information.
    """
    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": combined_prompt}
        ]
    )
    print("- gpt3 done!")
    return completion.choices[0].message.content

# Function to query LLAMA Chat
def query_llama_chat (combined_prompt):
    response = ""
    for event in replicate.stream(
        "meta/llama-2-70b-chat",
        input={
            "top_k": 0,
            "top_p": 1,
            "prompt": combined_prompt,
            "temperature": 0.5,
            "system_prompt": "You are a helpful, respectful, and honest assistant. Always answer as helpfully as possible, while being safe. Your answers should only reference the provided relevant information and should not include any other knowledge or assumptions. If the provided information is insufficient, explain why and indicate the lack of information.",
            "length_penalty": 1,
            "max_new_tokens": 500,
            "min_new_tokens": -1,
            "prompt_template": "<s>[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n{prompt} [/INST]",
            "presence_penalty": 0
        },
    ):
        response += str(event)
    print("- llama chat done!")
    return response

# Function to query LLAMA Falcon
def query_llama_falcon(combined_prompt):

    engineered_prompt = f"""
    You are a helpful assistant. Given the information below, construct your response referencing only the provided information and not using any other knowledge.

    {combined_prompt}

    Please ensure your response only uses the above information.
    """

    output = replicate.run(
        "joehoover/falcon-40b-instruct:7d58d6bddc53c23fa451c403b2b5373b1e0fa094e4e0d1b98c3d02931aa07173",
        input= {
        "prompt": engineered_prompt,
        "temperature": 1,
        "seed": -1,
        "debug": False,
        "top_p": 1,
        "max_length": 500,
        "length_penalty": 1,
        "repetition_penalty": 1,
        "no_repeat_ngram_size": 0
        }
    )
    print("- llama falcon done!")
    
    
    
    output_string = "".join(str(item) for item in output)
    return output_string

# Evaluation
def compute_rouge(reference, hypothesis):
    scorer = rouge_scorer.RougeScorer(['rouge2'], use_stemmer=True)
    scores = scorer.score(reference, hypothesis)
    return scores

# App endpoint
app = Flask(__name__)
CORS(app)

combined_prompt_global = ""
search_results_global = []

@app.route('/evaluate', methods=['POST'])
def evaluate():
    global combined_prompt_global, search_results_global

    data = request.get_json()

    initial_prompt = data['prompt']
    search_results_global = query_chroma_db(initial_prompt, db)
    combined_prompt_global = f"User prompt: {initial_prompt}\n\nRelevant Information from Search Results:\n"
    for result in search_results_global:
        combined_prompt_global += result + "\n"

    return jsonify({"status": "processing"}), 200

@app.route('/evaluate-stream', methods=['GET'])
def evaluate_stream():
    def generate():
        results = {}
        reference = " ".join(search_results_global)
        rouge_scores = {}

        results["GPT-4"] = query_gpt4(combined_prompt_global)
        rouge_scores["GPT-4"] = compute_rouge(reference, results["GPT-4"])
        yield f"data: {json.dumps({'model': "GPT-4", 'response': results['GPT-4'], 'scores': rouge_scores['GPT-4']['rouge2']})}\n\n"
        time.sleep(1)  

        results['GPT-3.5-turbo'] = query_gpt3_5_turbo(combined_prompt_global)
        rouge_scores['GPT-3.5-turbo'] = compute_rouge(reference, results['GPT-3.5-turbo'])
        yield f"data: {json.dumps({'model': 'GPT-3.5-turbo', 'response': results['GPT-3.5-turbo'], 'scores': rouge_scores['GPT-3.5-turbo']['rouge2']})}\n\n"
        time.sleep(1)  

        results['Llama-2-70b-chat'] = query_llama_chat(combined_prompt_global)
        rouge_scores['Llama-2-70b-chat'] = compute_rouge(reference, results['Llama-2-70b-chat'])
        yield f"data: {json.dumps({'model': 'Llama-2-70b-chat', 'response': results['Llama-2-70b-chat'], 'scores': rouge_scores['Llama-2-70b-chat']['rouge2']})}\n\n"
        time.sleep(1)

        results['Falcon-40b-instruct'] = query_llama_falcon(combined_prompt_global)
        rouge_scores['Falcon-40b-instruct'] = compute_rouge(reference, results['Falcon-40b-instruct'])
        yield f"data: {json.dumps({'model': 'Falcon-40b-instruct', 'response': results['Falcon-40b-instruct'], 'scores': rouge_scores['Falcon-40b-instruct']['rouge2']})}\n\n"
        time.sleep(1)  

    return Response(generate(), mimetype='text/event-stream')


if __name__ == '__main__':
    app.run(debug=True)
