import openai

API_KEY = open("API KEY", "r").read()
openai.api_key = API_KEY


def gpt3_chat(message):

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": message},
        ]
    )

    result = response['choices'][0]['message']['content'].strip()

    return result
