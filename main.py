from APIrequests import gpt3_chat
import os

processedDir = 'D:/Coding Projects/Python/LLM4PM/processed'
tokensUsed = 0

prompt = "give me all people, companies and products discussed in the email, format them like this: {property}:{name}. " \
         "Properties include: sender, receiver, product, company, other" \
         "Each entry as individual lines, no empty lines."

for count, file in enumerate(os.listdir(processedDir)):

    # for each file , call the gpt3_chat function and give a string as input
    # the string should be "give me the line number at which each individual email begins" + the contents of the file
    # the output should be a string that is the line number at which each individual email begins
    # print the output
    result = (gpt3_chat(prompt + "\n\n" + str(open(processedDir + '/' + file, 'r',encoding='utf-8').read())))

    tokensUsed += result[1]

    print(str(count+1) + "/" + str(len(os.listdir(processedDir))) + " - " + str(file) + " - " + str(result[1]) + "/" + str(tokensUsed))
    print(result[0] + "\n")

print("Total tokens used: " + str(tokensUsed))
print("price: " + str(tokensUsed/1000 * 0.0015) + " USD")
print("average tokens: " + str(tokensUsed/len(os.listdir(processedDir))))
