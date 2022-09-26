import os
import requests
from dotenv import load_dotenv

load_dotenv()


def error_handler(owner, query_url):
    user_url = "https://api.github.com/users/" + owner + "/repos"

    if requests.get(user_url).status_code != 200:
        raise Exception("User Not Found.")

    if requests.get(query_url).status_code != 200:
        raise Exception("Repo Not Found.")


def get_pull_requests(owner, repo, start_date, end_date):

    access_token = os.getenv("Autho")
    query_url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    error_handler(owner, query_url)
    response = requests.get(query_url, auth = (owner, access_token))

    response = response.json()

    list_of_repos = [
        {
            "id": i["id"],
            "user:": i["user"]["login"],
            "title": i["title"],
            "state": i["state"],
            "created_at": i["created_at"],
        }
        for i in response
        if start_date <= (i["created_at"] or i["updated_at"] or i["closed_at"] or i["merged_at"]) <= end_date
    ]
    return list_of_repos

print(get_pull_requests("Umuzi-org", "ACN-syllabus", "2022-03-01", "2022-03-10"))