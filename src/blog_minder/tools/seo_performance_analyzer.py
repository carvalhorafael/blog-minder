import os
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

# Build Google Search Console service
webmasters_service = build('searchconsole', 'v1', credentials=credentials)


def get_search_console_data(url):
    site_url = 'sc-domain:' + os.environ["GOOGLE_SEARCH_CONSOLE_SITE_DOMAIN"]
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


class IdentifyWinningPost(BaseTool):
    name: str = "Identify the winning post"
    description: str = (
        "Receives the URL of two posts and returns which one is the winning post."
    )

    def _run(self, post01_url: str, post02_url: str) -> str:
        data_url1 = get_search_console_data(post01_url)
        data_url2 = get_search_console_data(post02_url)

        if data_url1['rows'][0]['position'] <= data_url2['rows'][0]['position']:
            return post01_url
        else:
            return post02_url
