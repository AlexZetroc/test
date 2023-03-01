import openai
import streamlit as st
import concurrent.futures
import pyperclip


#set the GPT-3 api key
openai.api_key = st.secrets['pass']

st.header("Improvado chat")

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
    st.info(final_response)
    
    # Add a copy button to copy the output answer
    if st.button("Copy Answer"):
        pyperclip.copy(final_response)
        st.write("Output answer has been copied to clipboard.")
