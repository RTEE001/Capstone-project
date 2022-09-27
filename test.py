import requests
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()


def date_time(date):
    if date is not None:
        if len(date) > 10:
            date = date[:10]
        date = datetime.strptime(date, "%Y-%m-%d").date()
    return date


def display_pull_request(response, start_date, end_date):
    array_output = []

    for i, item in enumerate(response.json()):
        userID = response.json()[i]["id"]
        user = response.json()[i]["user"]["login"]
        statePR = response.json()[i]["state"]
        titleOfPR = response.json()[i]["title"]
        createdDate = date_time(response.json()[i]["created_at"])
        updatedDate = date_time(response.json()[i]["updated_at"])
        closedDate = date_time(response.json()[i]["closed_at"])
        mergedDate = date_time(response.json()[i]["merged_at"])

        collected_data = {
            "id": userID,
            "user": user,
            "state": statePR,
            "title": titleOfPR,
            "created_at": createdDate.strftime('%Y-%m-%d'),
        }

        if ((createdDate and (createdDate >= start_date and createdDate <= end_date))
            or (updatedDate and (updatedDate >= start_date and updatedDate <= end_date))
            or (closedDate and (closedDate >= start_date and closedDate <= end_date))
            or (mergedDate and (mergedDate >= start_date and mergedDate <= end_date))):
            array_output.append(collected_data)

    return array_output


def get_pull_requests(owner, repo_name, start_date, end_date):
    start_date = date_time(start_date)
    end_date = date_time(end_date)

    GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

    try:
        pull_request = requests.get(
            f"https://api.github.com/repos/{owner}/{repo_name}/pulls?per_page=100", 'state=all', auth=(GITHUB_TOKEN))
        return display_pull_request(pull_request, start_date, end_date)

    except requests.ConnectionError as e:
        return str(e)
    except requests.Timeout as e:
        return str(e)
    except requests.RequestException as e:
        return str(e)
    except KeyError:
        return "Error 404 User or Repo not found"



print(get_pull_requests("Um1222222", "ACN-syllabus", "2021-01-01", "2021-04-22"))

