import os
from unittest import result
import requests
import json
from typing import List
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# from Ipython.Display import Markdown, Display, update_display
from openai import OpenAI
from urllib3 import response

load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")

# if openai_key and openai_key[:8] == "sk-proj-":
#     print("OpenAi key valid and available")
# else:
#     prnt("Error: OpenAi key unavailable or invalid!")

MODEl = "gpt-4o-mini"
openai = OpenAI()


# A class to retreive data from website
class Website:
    """A utility class that represent a website that we have scrapped"""

    url: str
    body: str
    title: str
    links: List[str]
    text: str

    def __init__(self, url: str) -> None:
        self.url = url
        response = requests.get(url)
        self.body = response.content
        soup = BeautifulSoup(self.body, "html.parser")
        self.title = soup.title.string if soup.title else "No title found"
        if soup.body:
            for irrelevant in soup.body(["script", "img", "style", "input"]):
                irrelevant.decompose()

            self.text = soup.body.get_text(separator="\n", strip=True)
        else:
            self.text = ""
        links = [links.get("href") for links in soup.find_all("a")]
        self.links = [link for link in links if link]

    def get_content(self):

        print(f"Webpage Title:\n{self.title}\nWebpage Contents:\n{self.text}\n\n")
        return f"Webpage Title:\n{self.title}\nWebpage Contents:\n{self.text}\n\n"


website = Website("https://alifscript.com/")
print(website.links)

# LLM LOGIC
link_system_prompt = "You are provided with a list of links found in a webpage.\
You are able to decide which of the links is relevant to include in a brocure about the company, \
such as an About page, or Company page or Careers/jobs page\n"

link_system_prompt += "You should respond in a Json as in this example:"
link_system_prompt += """
{
 links:[   {"type":"about page", "url":"https://full.url/goes/here/about"}
    {"type":"Careers page", "url":"https://full.url/Careers"}
]
}
"""


def get_links_user_prompts(website):
    user_prompt = f"Here is the list of links on the website {website.url} "
    user_prompt += "Please decide which links are releveant web links for a brochure about the company, reply with full https url: Do not include privacy, Terms of service, email links.\n"
    user_prompt += "Links (some might be relative links):\n"
    user_prompt += "\n".join(website.links)
    return user_prompt


def get_links(url):
    website = Website(url)
    response = openai.chat.completions.create(
        model=MODEl,
        messages=[
            {"role": "system", "content": link_system_prompt},
            {"role": "user", "content": get_links_user_prompts(website)},
        ],
        response_format={"type": "json_object"},
    )

    result = response.choices[0].message.content
    return json.loads(result)
