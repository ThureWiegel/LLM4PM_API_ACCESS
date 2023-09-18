- To run the program, a mysql connection has to be created. The login information has to be provided to the
    mysql.connector function.

- An OpenAI API key has to be provided as a API_KEY file in the projects root folder.

- The program is configured to insert new db entries for each email.
- To overwrite existing emails and continuously update the context database, <br> 
    lines 107 to 108 need their # removed. <br>
    lines 111 to 112 have to be commented.