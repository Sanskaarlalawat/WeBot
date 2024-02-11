import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai

st.title("Chat with AI")
st.write("Ask anything you want")

# Set your OpenAI API key
openai.api_key = "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"

messages = [{"role": "system", "content": "You are a helpful and kind AI Assistant."}]

def scrape_website(url, selector):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        extracted_info = soup.select_one(selector).text
        return extracted_info
    except (requests.exceptions.RequestException, AttributeError, ValueError) as e:
        st.error(f"An error occurred while scraping the website: {str(e)}")
        st.error(f"URL: {url}")
        return f"An error occurred while scraping the website: {str(e)}"

def extract_features(url, feature):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        if feature == "title":
            extracted_feature = soup.title.string
        elif feature == "meta_description":
            meta_tag = soup.find("meta", attrs={"name": "description"})
            extracted_feature = meta_tag["content"] if meta_tag else "No meta description found."
        elif feature == "header":
            extracted_feature = soup.h1.text
        else:
            extracted_feature = "Invalid feature requested."
        return extracted_feature
    except (requests.exceptions.RequestException, AttributeError, ValueError) as e:
        st.error(f"An error occurred while extracting the feature: {str(e)}")
        st.error(f"URL: {url}")
        return f"An error occurred while extracting the feature: {str(e)}"

def analyze_text(text):
    return f"Text analysis results: {text}"

@st.cache
def chatbot(input):
    if input:
        messages.append({"role": "user", "content": input})

        if input.startswith("http://") or input.startswith("https://"):
            messages.append({"role": "assistant", "content": "Please provide a feature to extract (title, meta_description, header)."})
        elif "feature" not in messages[-1]:
            messages[-1]["feature"] = input
            messages.append({"role": "assistant", "content": "Processing the feature request..."})
        else:
            extracted_feature = extract_features(messages[-2]["content"], messages[-1]["content"])
            analyzed_result = analyze_text(extracted_feature)
            messages.append({"role": "assistant", "content": analyzed_result})
            return analyzed_result
        try:
            chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
            reply = chat.choices[0].message.content
            messages.append({"role": "assistant", "content": reply})
            return reply
        except openai.error.APIError as e:
            st.error(f"OpenAI API Error: {str(e)}")
            return "An error occurred while processing the request. Please try again later."

user_input = st.text_area("Input URL & Extract the information or Chat to AI")
if user_input:
    reply = chatbot(user_input)
    st.text(reply)