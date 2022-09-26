import requests
from dotenv import load_dotenv
import os 

load_dotenv()

TOKEN = os.environ.get("TOKEN")

def check_user(owner):
    api_url = f"https://api.github.com/users/{owner}"
    response=requests.get(api_url, auth=({owner}, TOKEN))
    if response.status_code != 200:
        raise Exception(f"Error {response.status_code} User Not Found")

def check_repo(owner, repo_name):
    api_url = f"https://api.github.com/repos/{owner}/{repo_name}"
    response=requests.get(api_url, auth=({owner}, TOKEN))
    if response.status_code != 200:
        raise Exception("Repo Not Found")

def get_pull_requests(owner, repo_name, start_date, end_date): 
    check_user(owner)
    check_repo(owner, repo_name)
        
    response = requests.get(f"https://api.github.com/repos/{owner}/{repo_name}/pulls?state=all", 
    auth=({owner}, TOKEN))
    repo = response.json()
    repo_list = []  

    while True:

        for item in repo:
            if ((item['merged_at'] != None) and (start_date <= item['merged_at'][:10] <= end_date)) \
                or (((item['created_at'] != None)) and (start_date <= item['created_at'][:10] <= end_date)) \
                or ((item['updated_at'] != None) and (start_date <= item['updated_at'][:10] <= end_date)) \
                or ((item['closed_at'] != None) and (start_date <= item['closed_at'][:10] <= end_date)):
        
                repo_list.append({"id": item['id'], "title":item['title'], "user":item['user']['login'],
                "state":item['state'], "created_at":item['created_at']})

        if "next" not in response.links:
            break
        else:
            response=requests.get(response.links["next"]["url"])
            repo = response.json()
    
    return repo_list
    
print(get_pull_requests("Umuzi-org", "MphoTrevor-mashau-186-consume-github-api-python", "2022-03-01", "2022-09-26"))