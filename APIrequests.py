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
                           f"From just the subject line, extract the company talked about and the topic talked about."
                           f"Limit you analysis to just the text of subject line, do not read the body of the email."
                           f"The subject line you have to analyse is usually formatted like this:"
                           f"'Subject:' subject line text"
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


def gpt_extractor(message, context):
    function = [
        {
            "name": "email_summarizer",
            "description": "give a summary of each relevant point and technical aspect talked about in the email",
            "parameters": {
                "type": "object",
                "properties": {
                    "summarization": {
                        "type": "string",
                        "description": "a bullet point list of the main talking points and technical specifications from the email."
                                       "split into general talking points and technical specifications."
                    }
                }
            }
        }
    ]

    contextMessages = [
        {
            "role": "assistant",
            "content": f"{context}"
        },
        {
            "role": "system",
            "content": "You are a email summarizer."
        },
        {
            "role": "user",
            "content": f"You are an email summarizer. Here is an email:"
                       f"{message}."
                       f"Return all main talking points from the emails body as a bullet point list."
                       f"Preface every talking point with the person saying/addressed by the talking point."
                       f"Disregard formalities and signatures."
                       f"Group general talking points and technical information."
                       f"Return just the list."
                       f"Follow this bullet point list schema:"
                       f""
                       f"Talking points:"
                       f"- person x says ..."
                       f"- person x says ..."
                       f"- etc."
                       f"Technical Specifications:"
                       f"- Specification x"
                       f"- Specification y"
                       f"- etc."
                       f""
                       f"If you do not have context about previous summarizations, return just the information as bullet point list."
                       f"If you do have context for previous summarizations, does the summarized talking points and technical specifications fit the previous context?"
                       f"If it does fit previous context, return the information using the given schema."
                       f"If it does not fit previous context add or update to the information following the given schema."
                       f"Add information if it is new and does not fit the previous context."
                       f"Update information that was mentioned in previous context."
                       f"Make sure to exactly follow this schema to return the information:"
                       f""
                       f"Talking points:"
                       f"- person x says ..."
                       f"- person x says ..."
                       f"- etc"
                       f"Technical Specifications:"
                       f"- Specification x"
                       f"- Specification y" 
                       f"- etc."
                       f""
                       f"Again just return just the information, no other text."
        },
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=contextMessages,
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
