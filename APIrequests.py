import openai
import json

API_KEY = open("API KEY", "r").read()
openai.api_key = API_KEY


def gpt_classifier(message):
    function = [
        {
            "name": "classify_Email",
            "description": "gets the datetime, subject company and subject object from the email",
            "parameters": {
                "type": "object",
                "properties": {
                    "datetime": {
                        "type": "string",
                        "description": "the datetime of the email."
                                       "format like this: 2021-01-01 00:00:00."
                                       "If no datetime is found, return 'none'"
                    },
                    "company": {
                        "type": "string",
                        "description": "If no company is found, return 'none'"
                                       "the company mentioned in the subject line, usually formatted like: XX for company YY."
                                       ""
                                       "always return company"
                    },
                    "object": {
                        "type": "string",
                        "description": "If no object is found, return 'none'."
                                       "the object mentioned in the subject line, usually formatted like: object XX for company YY."
                                       ""
                                       "always return object"
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
                "content": f"Here is an email: {message}, please return the datetime, subject company and subject object from the email."
            }
        ],
        functions=function,
    )

    result = response['choices'][0]['message']['function_call']['arguments']
    json_result = json.loads(result)

    tokens = response['usage']['total_tokens']

    # print(json_result)

    return json_result["datetime"], json_result["company"], json_result["object"], tokens


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
    )

    result = response['choices'][0]['message']['function_call']['arguments']
    # print(response)
    json_result = json.loads(result, strict=False)

    # print(json_result)

    tokens = response['usage']['total_tokens']

    # print(json_result)

    return json_result["summarization"], tokens
