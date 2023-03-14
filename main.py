import openai
import streamlit as st
import concurrent.futures
import pandas as pd
import gspread
import clickhouse_connect


#set the GPT-3 api key
openai.api_key = st.secrets['pass']

client = clickhouse_connect.get_client(
    host = st.secrets["host"],
    port = st.secrets["port"],
    secure = st.secrets["secure"],
    user= st.secrets["user"],
    password=st.secrets["password"])
             

query_result = client.query("""
SELECT gong_call_title, gong_call_transcript_full_text     
FROM internal_analytics.stg_gong_calls
JOIN internal_analytics.stg_gong_transcripts
ON stg_gong_calls.gong_call_id = stg_gong_transcripts.gong_call_id
LIMIT 10
""")
                            
#Credentials for gspread google sheets
credentials = {
  "type": st.secrets['type'],
  "project_id": st.secrets['project_id'],
  "private_key_id": st.secrets["private_key_id"],
  "private_key": st.secrets["private_key"],
  "client_email": st.secrets["client_email"],
  "client_id": st.secrets["client_id"],
  "auth_uri": st.secrets["auth_uri"],
  "token_uri": st.secrets["token_uri"],
  "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
  "client_x509_cert_url": st.secrets["client_x509_cert_url"]
}
gc = gspread.service_account_from_dict(credentials)

#establish connection with gspread
database = gc.open("sales_test")

#select a worksheet
wks = database.worksheet("Sheet1")

url_link = 'https://forms.gle/5irQryzKNSaJkUuRA'

st.header("Improvado sales app")
st.markdown(f'<a href="{url_link}">Feel free to share feedbak about our sales application</a>', unsafe_allow_html=True)

result_dict = {row[0]: row[1] for row in query_result.result_set}
selected_title = st.selectbox("Select a title", list(result_dict.keys()))
if selected_title:
    selected_transcript = result_dict[selected_title]
    #st.selectbox("Select a transcript", [selected_transcript])
    #st.write("You selected:", selected_title, "-", selected_transcript)
    st.session_state.call_text = selected_transcript
else:
    st.session_state.call_text = st.text_area("Enter your text to process", max_chars=None)
processed_text = st.session_state.call_text



company = " "
call_text = str(selected_transcript)
question_text = st.text_area("Enter your question")
temp = st.slider("temperature", 0.0,1.0,0.2)

# Split the input text every 10000 characters
text_parts = [call_text[i:i+10000] for i in range(0, len(call_text), 10000)]

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
    while len(final_response) > 10000:
        # Split the final_response every 12000 characters
        final_parts = [final_response[i:i+10000] for i in range(0, len(final_response), 10000)]
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
