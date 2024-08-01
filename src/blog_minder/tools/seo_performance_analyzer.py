import os
import csv
import google.auth
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from crewai_tools import BaseTool

# Credentials here
credentials = service_account.Credentials.from_service_account_file(
    os.environ["GOOGLE_SEARCH_CONSOLE_JSON_CREDENTIAL"],
    scopes=['https://www.googleapis.com/auth/webmasters', 'https://www.googleapis.com/auth/analytics.readonly']
)

today = datetime.today().strftime('%Y-%m-%d')
a_month_ago = (datetime.today() - timedelta(days=30)).strftime('%Y-%m-%d')
site_url = 'sc-domain:' + os.environ["GOOGLE_SEARCH_CONSOLE_SITE_DOMAIN"]

# Build Google Search Console service
webmasters_service = build('searchconsole', 'v1', credentials=credentials)


def get_search_console_data(url):
    request = {
        'startDate': a_month_ago,
        'endDate': today,
        'dimensions': ['page'],
        'dimensionFilterGroups': [{
            'filters': [{
                'dimension': 'page',
                'operator': 'equals',
                'expression': url
            }]
        }]
    }    
    response = webmasters_service.searchanalytics().query(siteUrl=site_url, body=request).execute()
    return response


def add_log_entry(log_entry):
    file_path = 'tmp/log_posts_not_indexed_by_google.csv'
    file_exists = os.path.isfile(file_path)
    with open(file_path, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)        
        # If the file does not exist, write the header first
        if not file_exists:
            writer.writerow(["URL"])  # Example header, modify as needed
        # Write the log entry
        writer.writerow(log_entry)


class IdentifyWinningPost(BaseTool):
    name: str = "Identify the winning post"
    description: str = (
        "Receives the URL of two posts and returns which one is the winning post."
    )

    def _run(self, post01_url: str, post02_url: str) -> str:
        data_url1 = get_search_console_data(post01_url)
        data_url2 = get_search_console_data(post02_url)

        # Some URLs may have problems and may not be indexed by Google.
        # In this case, the other URL will be declared the winner and the unindexed URL will be added to the log.
        # If both URLs are indexed, the one with the best position is declared the winner.
        if 'rows' not in data_url1:
            add_log_entry([post01_url])
            return post02_url
        elif 'rows' not in data_url2:
            add_log_entry([post02_url])
            return post01_url
        else:    
            if data_url1['rows'][0]['position'] <= data_url2['rows'][0]['position']:
                return post01_url
            else:
                return post02_url


class GetPagesMetrics(BaseTool):
    name: str = "Get pages metrics of a website."
    description: str = (
        "Returns pages metrics."
    )

    def _run(self) -> str:
        request = {
            'startDate': a_month_ago,
            'endDate': today,
            'dimensions': ['page'],
            'rowLimit': 20,
            'orderBy': [{
                'field': 'impressions',
                'direction': 'descending'
            }]
        }
        response = webmasters_service.searchanalytics().query(siteUrl=site_url, body=request).execute()
        
        for row in response.get('rows', []):
            page = row['keys'][0]
            clicks = row['clicks']
            impressions = row['impressions']
            ctr = row['ctr']
            position = row['position']
            
            print(f'URL: {page}, Cliques: {clicks}, Impressões: {impressions}, CTR: {ctr:.2%}, Posição: {position:.2f}')

        return "all OK"