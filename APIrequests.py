import openai
import json

API_KEY = open("API KEY", "r").read()
openai.api_key = API_KEY


def gpt_classifier(message):
    function = [
        {
            "name": "classify_Email",
            "description": "gets the company and topic mentioned in the email's subject line",
            "parameters": {
                "type": "object",
                "properties": {
                    "company": {
                        "type": "string",
                        "description": "the company mentioned in the emails subject line"
                    },
                    "topic": {
                        "type": "string",
                        "description": "the topic mentioned in the emails subject line"
                    }
                }
            }
        }
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a email analyser. You are given an email and reliably filter out information within it."
            },
            {
                "role": "user",
                "content": f"Here is an email: {message}"
                           f"From the subject line, extract the company talked about and the topic talked about."
                           f"Limit you analysis to just the subject line, do not read the body of the email."
                           f"Provide just the answers, no other text"
            }
        ],
        functions=function,
        function_call={"name": "classify_Email"}
    )

    result = response['choices'][0]['message']['function_call']['arguments']
    json_result = json.loads(result)

    tokens = response['usage']['total_tokens']

    # print(json_result)

    return json_result["company"], json_result["topic"], tokens


def gpt_extractor(message):
    function = [
        {
            "name": "email_summarizer",
            "description": "give a summary of each relevant point talked about in the email",
            "parameters": {
                "type": "object",
                "properties": {
                    "summarization": {
                        "type": "string",
                        "description": "summarization"
                                       "formatted like this: "
                                       "1. talking point 1"
                                       "2. talking point 2"
                                       "3. talking point 3"
                                       "..."
                                       "If no talking points are found, return 'none'"
                                       "disregard talking points that is not relevant to the subject company and subject object"
                                       "disregard talking points that directly regard the email itself"
                    }
                }
            }
        }
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a email analyser. You are given an email and reliably filter out information within it."
            },
            {
                "role": "user",
                "content": f"Here is an email: {message}. Please summarize each talking point in the email separately"
            }
        ],
        functions=function,
        function_call={"name": "email_summarizer"}
    )

    result = response['choices'][0]['message']['function_call']['arguments']
    # print(response)
    json_result = json.loads(result, strict=False)

    # print(json_result)

    tokens = response['usage']['total_tokens']

    # print(json_result)

    return json_result["summarization"], tokens


def gpt_entryComparer(company1, object1, company2, object2):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You compare two different email subject lines and return whether they belong to the same email chain or not"
            },
            {
                "role": "user",
                "content": f"Below are the email subject company and object from two emails:"
                           f"Email 1: {company1} - {object1}"
                           f"Email 2: {company2} - {object2}"
                           f"Do these emails regard the sam company and product?"
                           f"Return just TRUE or FALSE as your answer"
            }
        ],
    )

    result = response['choices'][0]['message']['content']

    tokens = response['usage']['total_tokens']

    return result, tokens
