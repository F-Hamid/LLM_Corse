import os
import openai
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from IPython.display import Markdown, display
from openai import OpenAI


load_dotenv()


api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("NO API KEY! please check your .env file")
else:
    print("API KEY AVAILABLE")

openai = OpenAI()


class Website:
    """A uitilty class to represent a website that we scrapped"""

    url: str
    title: str
    text: str

    def __init__(self, url) -> None:
        """Create this website object from a given url using BeautifulSoup library"""
        self.url = url
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        self.title = soup.title.string if soup.title else "No title found"
        for irrelevant in soup.body(["script", "img", "style", "input"]):
            irrelevant.decompose()

        self.text = soup.body.get_text(separator="\n", strip=True)


system_prompt = "You are an assistant that analyze the content of a website.\ and provide a short summary, ignoring text that maybe navigation related. \ respond in markdown"


def user_prompt_for(website):
    user_prompt = f"You're looking at website titled {website.title}"
    user_prompt += " \n The content of the website is as follows; \
    please provide a short summary of the prices provided by website in markdown; \
    if it includes news or suggestions, summarize those too. \n\n"
    user_prompt += website.text
    return user_prompt


def message_for(website):
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt_for(website)},
    ]


# portfolio=Website("https://alifscript.com/")


def summarize(url):
    website = Website(url)
    resepnse = openai.chat.completions.create(
        model="gpt-4o-mini", messages=message_for(website)
    )
    return resepnse.choices[0].message.content


def display_summary(item):
    url = f"https://www.ebay.com/sch/i.html?_nkw={item.replace(' ', '+')}"
    summary = summarize(url)
    print(summary)
    display(Markdown(summary))


display_summary("ipad 11th gen")
