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

    time.sleep(0.5)

    while classifierResult[0] == "" or classifierResult[1] == "" or classifierResult[0] is None or classifierResult[
        1] is None:
        classifierResult = (
            APIrequests.gpt_classifier(str(open(processedDir + '/' + file, 'r', encoding='utf-8').read())))
        time.sleep(0.5)

    mycursor.execute("SELECT id, company, object, extractedInfo from llm4pm.emaildata")

    sqlresult = mycursor.fetchall()

    time.sleep(0.5)

    match = bool(0)
    matchID = None

    for x in sqlresult:

        time.sleep(0.5)

        comparisonResult = str2bool(
            APIrequests.gpt_entryComparer(x[1], x[2], classifierResult[0], classifierResult[1])[0])

        if not comparisonResult:  # FALSE
            continue

        else:  # TRUE
            print("match found: " + file)
            # print("id: " + str(x[0]))
            match = True
            matchID = x[0]

    # when no existing entry is found, store email information in DB (subject company/object and extracted info)
    if not match:
        # empty / null context
        context = ""
        extractedInfo = APIrequests.gpt_extractor(str(open(processedDir + '/' + file, 'r', encoding='utf-8').read()),context)
        # cleanedExtractedInfoList = extractedInfo[0].split("\n")
        # print(cleanedExtractedInfoList)
        # # join list into string
        # cleanedExtractedInfo = ""
        # for line in cleanedExtractedInfoList:
        #     cleanedExtractedInfo += line.strip()
        # print(cleanedExtractedInfo)

        sql = "INSERT INTO llm4pm.emaildata (company, object, extractedInfo) VALUES (%s, %s, %s)"
        val = (classifierResult[0], classifierResult[1], extractedInfo[0])
        mycursor.execute(sql, val)
        mydb.commit()
        print("inserted email: " + file)
        continue

    # when an existing entry is found, update the extracted info
    if match:
        # get existing extracted info for use as context
        mycursor.execute("SELECT extractedInfo from llm4pm.emaildata WHERE id = " + str(matchID))
        ContextInfo = mycursor.fetchone()

        # Extract new info with context
        extractedInfo = APIrequests.gpt_extractor(str(open(processedDir + '/' + file, 'r', encoding='utf-8').read()), ContextInfo)

        sql = "UPDATE llm4pm.emaildata set extractedInfo = %s WHERE id = %s"
        val = (extractedInfo[0], matchID)
        mycursor.execute(sql, val)
        mydb.commit()
