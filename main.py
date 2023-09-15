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

    currentFile = str(open(processedDir + '/' + file, 'r', encoding='utf-8').read())

    classifierResult = (APIrequests.gpt_classifier(str(open(processedDir + '/' + file, 'r', encoding='utf-8').read())))

    time.sleep(0.5)

    # classifierResult[0] == "" or classifierResult[1] == "" or classifierResult[0] is None or classifierResult[
    #     1] is None:

    while classifierResult[0] in ["", None] or classifierResult[1] in ["", None]:
        classifierResult = (
            APIrequests.gpt_classifier(currentFile))
        time.sleep(0.5)

    # extract info from eamils already in DB
    mycursor.execute("SELECT id, company, object from llm4pm.emaildata")

    sqlresult = mycursor.fetchall()

    time.sleep(0.5)

    match = bool(0)
    matchID = None

    for x in sqlresult:

        time.sleep(0.5)

        comparisonResult = str2bool(
            APIrequests.gpt_entryComparer(x[1], x[2], classifierResult[0], classifierResult[1])[0])

        if not comparisonResult:  # FALSE, no match found
            continue

        else:  # TRUE, match found
            match = True
            matchID = x[0]
            continue

    # when no existing entry is found, store email information in DB (subject company/object and extracted info)
    if not match:
        # Extract new info without context
        extractedInfo = APIrequests.gpt_extractorNew(currentFile)

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
        contextInfo = mycursor.fetchone()
        #
        # # Extract new info with context and update existing entry
        # extractedInfo = APIrequests.gpt_extractorAdd(currentFile, contextInfo)
        #
        # sql = "UPDATE llm4pm.emaildata set extractedInfo = %s WHERE id = %s"
        # val = (extractedInfo[0], matchID)
        # mycursor.execute(sql, val)
        # mydb.commit

        extractedInfo = APIrequests.gpt_extractorNew(currentFile)

        sql = "INSERT INTO llm4pm.emaildata (company, object, extractedInfo) VALUES (%s, %s, %s)"
        val = (classifierResult[0], classifierResult[1], extractedInfo[0])
        mycursor.execute(sql, val)
        mydb.commit()
