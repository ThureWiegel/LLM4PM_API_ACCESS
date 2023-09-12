import APIrequests
import os

processedDir = 'D:/Coding Projects/Python/LLM4PM/processed'
tokensUsed = 0

for count, file in enumerate(os.listdir(processedDir)):
    # calls the classifier function from APIrequests.py with the email as the argument
    result = (APIrequests.gpt_classifier(str(open(processedDir + '/' + file, 'r', encoding='utf-8').read())))

    # tokensUsed += result[3]

    print(result[0])
    print(result[1])
    print(result[2])
    print()




print("\nTotal tokens used: " + str(tokensUsed))
print("price: " + str(tokensUsed / 1000 * 0.0015) + " USD")
print("average tokens: " + str(tokensUsed / len(os.listdir(processedDir))))
