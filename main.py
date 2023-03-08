import openai
import streamlit as st
import concurrent.futures
import pandas as pd
import gspread



#set the GPT-3 api key
openai.api_key = st.secrets['pass']

#Credentials for gspread google sheets
credentials = {
  "type": "service_account",
  "project_id": "test-sales-logs",
  "private_key_id": "e847b5e46ffe629b2c9ac936ea8da525a96c7eb9",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEuwIBADANBgkqhkiG9w0BAQEFAASCBKUwggShAgEAAoIBAQCxEB4IkCsYxn4I\nQEuHYwmw2ceWSi8wJiNFjw4cRFFBAEGR8fldy8WvhLkG4YBJR59KC8iTThzsF0s6\niWsDsRHV9lY9kGJraTArrA566NolqQey94XlpYRlfkjk+onEVY/OglTNkTlxdwty\ns2IPhtdKqSTcSCQoUFzUP9stUXz34SVqPrCuvmh93WByKfNQx7zy/PWmkBK1Nfdk\n8ghSay7gEHQULvsSlaVBIdzHJwGpjuec7IKHPa7vey8rs8sMr117bEAfqerMwy1q\nzquYjpBPI+QmUBrExFolH/o/yEBM853SLMo34ZJIlwqG5ucgqVpqq8BkbVS1TPf3\nVyPRD7CFAgMBAAECgf9faXZfQIP4r2O6wbeLFqzIkviG3Yx2cn0PPpQCWprUxagp\nVpSWUCtDXLTxWd9UBARFImEy/4sWR0Po7aPjZi3DEYfnWAzkIT3HF5aCvnc1VAbF\nQ0+9YzO047Gw5R2kod0Cquu62kbaBAw0AsKuTm41DT0pQ4NrnEjP48xEeP5rLUGJ\nPwXkzTFch8htIr4jOFyZxmH02oAnpq3M9ZMGPQkaEKUr11uN2Lo7pxtc0JHtTuGS\niRfK4DMlMZk+d33YV0HcdcGb91SMRe9Kz9QS4B3wcSS9WIkEAMyUF/VjqDgqIUyf\ndT7y1xSbB7Nh0vR7P16WpbQjp9HJcXSBHsdr2iECgYEA5sORJN93+jarUo2KKn5W\n6mAqtyRfR0IY8irvwjAV2ohClgxuSF8N61So+aEaod4xdxzWZk9+YicmaG1yprYS\n8h4l0SJdMwkUSZSg+SbappIlXivexNKmN9knEXfk2bmRD9wE/Ky4yu4udmz0h4NT\n3OKtu2t7JuTWgdBv0sBLtaUCgYEAxG0lUUeTGRNIzC/uzcoQ4cB/UsVNLKzS6dnn\nOgJkEHDbDHMKOYeiTDG6afCn0zyy4aTkWQjDHlmOIVOFRkbG6V2dQADgdF/uM/no\ncH/MnJrU/JgzZoiMJvhibrRfuDAyR4fRYhVwK8HA/jow19tPpJ7hLVweVFXGRf/6\njfMb2WECgYBRZ6X5GvgJBWYUfifCa8UfcwM+jg8qZQ/Fxg3ENBBRggXzRrlUwGt5\nm+jr/sAVX/uVKFAd0WclGuh6qDlsxAgU7zup9fRov4gvmMXcfq9dWWrjOJiiWCkY\nxHr6t4+8mrCoppX/yLJ7q+AqGK9+an6YCkL9PaI5Czr8mloIP5u1nQKBgQCUJQ2E\nI8tZmiXJek1NgB0DZr+gmZX/H8li/ilaovr9O2C6HvmTMizB8q95vzuUIa94Z3ih\nfe5LMZf0op1dx3u1/hjfcMnYe5GYOd+JGZokctI4QEJkDpBFxAfZHskijZceQ90z\ncJ/NILCCDTlRU+LZccq6/0MQsDB+EvXRoY1bgQKBgGBR8bky5+tuNxvjH4ahFvEN\nbwdaawGi2bkeaKGa2cYXo00oQpknqz5k85+khSgcLzNsjdCLzletK7XZmszpcurQ\nThOpeGvGRYs8cTJ1bBcS7mhUrRl0iszHyQEwa3wNrgUScKEbi99mNUh0ustIXAjR\ncNXHBVz3ljU8aQdLj5hV\n-----END PRIVATE KEY-----\n",
  "client_email": "test-sales-logs@test-sales-logs.iam.gserviceaccount.com",
  "client_id": "101754412301200293061",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/test-sales-logs%40test-sales-logs.iam.gserviceaccount.com"
}
gc = gspread.service_account_from_dict(credentials)


#establish connection
database = gc.open("sales_test")

#select a worksheet
wks = database.worksheet("Sheet1")

st.header("Improvado sales app")

company = st.text_input("Enter company name or call ID")
call_text = st.text_area("Enter your text to process",max_chars=None)
question_text = st.text_area("Enter your question")
temp = st.slider("temperature", 0.0,1.0,0.2)

# Split the input text every 12000 characters
text_parts = [call_text[i:i+12000] for i in range(0, len(call_text), 12000)]

if (st.button("Submit")):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Use the executor to submit all the requests at the same time
        future_responses = [executor.submit(openai.Completion.create,
            engine = "text-davinci-003",
            prompt = part + question_text,
            max_tokens = 500,
            temperature = temp) for part in text_parts]

        # wait for all the futures to complete
        responses = [future.result() for future in concurrent.futures.as_completed(future_responses)]
    response = "".join([r["choices"][0]["text"] for r in responses])
    # ask the same question to the final response
    final_response = openai.Completion.create(
        engine = "text-davinci-003",
        prompt = response + question_text,
        max_tokens = 500,
        temperature = temp
    )
    final_response = final_response["choices"][0]["text"]
    while len(final_response) > 12000:
        # Split the final_response every 12000 characters
        final_parts = [final_response[i:i+12000] for i in range(0, len(final_response), 12000)]
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Use the executor to submit all the requests at the same time
            future_final_responses = [executor.submit(openai.Completion.create,
                engine = "text-davinci-003",
                prompt = part + question_text,
                max_tokens = 500,
                temperature = temp) for part in final_parts]

            # wait for all the futures to complete
            final_responses = [future.result() for future in concurrent.futures.as_completed(future_final_responses)]
        final_response = "".join([r["choices"][0]["text"] for r in final_responses])
        
    # Write the question and final response into a CSV file
    data = {'Question': [question_text], 'Response': [final_response]}
    df = pd.DataFrame(data)
    df.to_csv('logs.csv', mode='a', header=False, index=False)
    
    st.info(final_response)
    wks.append_row([company,question_text,final_response])
