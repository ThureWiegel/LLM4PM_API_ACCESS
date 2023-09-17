import json

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


totalProcessTime = ""
totalExtractionTime = ""
totalMatchingTime = ""

mycursor = mydb.cursor()

tst = time.time()
for count, file in enumerate(os.listdir(processedDir)):
    pst = time.time()

    currentFile = str(open(processedDir + '/' + file, 'r', encoding='utf-8').read())

    classifierResult = (APIrequests.gpt_classifier(str(open(processedDir + '/' + file, 'r', encoding='utf-8').read())))
    tokensUsed += classifierResult[2]

    time.sleep(0.5)

    while classifierResult[0] in ["", None] or classifierResult[1] in ["", None]:
        classifierResult = (
            APIrequests.gpt_classifier(currentFile))
        tokensUsed += classifierResult[2]
        time.sleep(0.5)

    # extract info from eamils already in DB
    mycursor.execute("SELECT id, company, object from llm4pm.emaildata")

    sqlresult = mycursor.fetchall()

    time.sleep(0.5)

    match = bool(0)
    matchID = None

    fileMatchingStart = time.time()

    for x in sqlresult:

        time.sleep(0.5)

        # matching of company and object with entries in database
        comparison = APIrequests.gpt_entryComparer(x[1], x[2], classifierResult[0], classifierResult[1])
        comparisonResult = str2bool(comparison[0])
        tokensUsed += comparison[1]

        if not comparisonResult:  # FALSE, no match found
            continue

        else:  # TRUE, match found
            match = True
            matchID = x[0]
            break

    fileMatchingEnd = time.time()
    totalMatchingTime += (str((fileMatchingEnd - fileMatchingStart)) + "\n")

    extractionStart = time.time()
    # when no existing entry is found, store email information in DB (subject company/object and extracted info)
    if not match:
        # Extract new info without context
        extractedInfo = APIrequests.gpt_extractorNew(currentFile)
        tokensUsed += extractedInfo[1]

        sql = "INSERT INTO llm4pm.emaildata (company, object, extractedInfo) VALUES (%s, %s, %s)"
        val = (classifierResult[0], classifierResult[1], extractedInfo[0])
        mycursor.execute(sql, val)
        mydb.commit()
        # print("inserted email: " + file)
        # print("NEW")

    # when an existing entry is found, update the extracted info
    if match:
        # get existing extracted info for use as context
        mycursor.execute("SELECT extractedInfo from llm4pm.emaildata WHERE id = " + str(matchID))
        contextInfo = mycursor.fetchone()

        # Extract new info with context
        extractedInfo = APIrequests.gpt_extractorAdd(currentFile, contextInfo)

        # Extract new info without context
        # extractedInfo = APIrequests.gpt_extractorNew(currentFile)

        # update existing entry with new extracted info (overwrites context information)
        # filteredInfo = json.dumps(extractedInfo[0])
        # sql = "UPDATE llm4pm.emaildata set extractedInfo = %s WHERE id = %s"
        # val = (filteredInfo, matchID)

        # insert extracted information in new row, for evaluation purposes
        sql = "INSERT INTO llm4pm.emaildata (company, object, extractedInfo) VALUES (%s, %s, %s)"
        val = (classifierResult[0], classifierResult[1], extractedInfo[0])

        mycursor.execute(sql, val)
        mydb.commit()

        # print("ADD")
        tokensUsed += extractedInfo[1]

    extractionEnd = time.time()
    totalExtractionTime += (str((extractionEnd - extractionStart)) + "\n")

    pet = time.time()
    totalProcessTime += (str((pet - pst)) + "\n")

tet = time.time()
print("Total tokens used: " + str(tokensUsed))
print("total time")
print(str(tet - tst))
print("total process time")
print(totalProcessTime)
print("total matching time")
print(totalMatchingTime)
print("total extraction time")
print(totalExtractionTime)
