import APIrequests
import os
import mysql.connector
import time

processedDir = 'D:/Coding Projects/Python/LLM4PM/processed'
tokensUsed = 0

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="llm4pm"
)


def str2bool(v):
    return v.lower() in ("true", "1")


mycursor = mydb.cursor()

for count, file in enumerate(os.listdir(processedDir)):

    classifierResult = (APIrequests.gpt_classifier(str(open(processedDir + '/' + file, 'r', encoding='utf-8').read())))
    # print("c: " + classifierResult[1])
    # print("p: " + classifierResult[2])

    mycursor.execute("SELECT id, company, object from llm4pm.emaildata")

    sqlresult = mycursor.fetchall()

    # extractedInfo = APIrequests.gpt_extractor(str(open(processedDir + '/' + file, 'r', encoding='utf-8').read()))
    extractedInfo = [""]

    match = bool(0)

    for x in sqlresult:
        time.sleep(0.5)
        comparisonResult = str2bool(APIrequests.gpt_entryComparer(x[1], x[2], classifierResult[0], classifierResult[1])[0])

        if not comparisonResult: # FALSE
            continue
        else:   # TRUE
            print("match found: " + file)
            # print("id: " + str(x[0]))
            match = True

    if not match:
        sql = "INSERT INTO llm4pm.emaildata (company, object, extractedInfo) VALUES (%s, %s, %s)"
        val = (classifierResult[0], classifierResult[1], extractedInfo[0])
        mycursor.execute(sql, val)
        mydb.commit()
        print("inserted email: " + file)
        # use gpt_extractor and store in extractedinfo db field

    #if match:


