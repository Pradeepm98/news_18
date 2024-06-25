
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import time




headers = {
    'sec-ch-ua': '"Chromium";v="124", "Microsoft Edge";v="124", "Not-A.Brand";v="99"',
    'Referer': 'https://www.livescore.com/',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0',
    'sec-ch-ua-platform': '"Linux"',
}


def parse_date_to_utc(date_string):
    naive_datetime = datetime.strptime(date_string, "%Y%m%d%H%M%S")
    
    # tz = pytz.timezone('Asia/Ho_Chi_Minh')
    tz = pytz.utc
    
    local_datetime = tz.localize(naive_datetime)
    
    formatted_datetime = local_datetime.strftime("%A, %m/%d/%Y - %I:%M %p %z")
    
    return formatted_datetime


async def fetch_data(query):
    params = {
    'query': query,
    'limit': '20',
    'locale': 'en',
    'countryCode': 'UK',
    'sCategories': 'true',
    'sStages': 'true',
    }
    async with aiohttp.ClientSession() as session:
        async with session.get('https://search-api.livescore.com/api/v2/search/soccer/team', params=params, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                return {'error': 'Failed to fetch data', 'status_code': response.status}
            

async def load_teams_from_fixtures(teamname ,teamid,prod_token):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://www.livescore.com/_next/data/'+prod_token+'/en/football/team/'+teamname+'/'+teamid+'/fixtures.json', headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                return {'error': 'Failed to fetch data', 'status_code': response.status}

async def load_teams_from_results(teamname ,teamid,prod_token):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://www.livescore.com/_next/data/'+prod_token+'/en/football/team/'+teamname+'/'+teamid+'/results.json', headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                return {'error': 'Failed to fetch data', 'status_code': response.status}

async def get_prod_token():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    async with aiohttp.ClientSession() as session:
        async with session.get('https://www.livescore.com/en/football/team/barcelona/2911/fixtures/', headers=headers) as response:
            if response.status == 200:
                content = await response.read()
                soup = BeautifulSoup(content, "html.parser")
                script_tags = soup.find_all("script")
                for script_tag in script_tags:
                    if 'createGlobalNamespace' in script_tag.text:
                        index = script_tag.text.find('})(')
                        if index != -1: 
                            string = script_tag.text[index + 3:]   
                            start_quote = string.find("'") + 1
                            end_quote = string.find("'", start_quote)
                            extracted_string = string[start_quote:end_quote]
                            return extracted_string
            else:
                return 'Error: Status Code ' + str(response.status)
            


async def get_next_match_club(query):
    all_results = []  
    prod_token = await get_prod_token()
    async def fetch_and_load(team):
        team_data = {
            'name': team['Nm'],
            'upcoming_match': []
        }
        team_result = await load_teams_from_fixtures(team['Nm'], team['ID'], prod_token)
        for events in team_result['pageProps']['initialData']['eventsByMatchType']:
            for event in events['Events'][:1]:
                event_data = {
                    'label': events['Snm'],
                    'home': event['T1'][0]['Nm'],
                    'away': event['T2'][0]['Nm'],
                    'time': event['Esd'],
'club_logo': (team_result.get('pageProps', {})
                              .get('initialData', {})
                              .get('basicInfo', {})
                              .get('badge', {})
                              .get('high', {})),                    'results':'No data found'
                }
                team_data['upcoming_match']=event_data
        if not team_data['upcoming_match']:
             team_result = await load_teams_from_results(team['Nm'], team['ID'], prod_token)
             for events in team_result['pageProps']['initialData']['eventsByMatchType']:
                for event in events['Events'][:1]:
                    event_data = {
                        'label': events['Snm'],
                        'home': event['T1'][0]['Nm'],
                        'away': event['T2'][0]['Nm'],
                        'time': event['Esd'],
                        'club_logo': (team_result.get('pageProps', {})
                              .get('initialData', {})
                              .get('basicInfo', {})
                              .get('badge', {})
                              .get('high', {})),                            'results':{
                             'Tr1': event.get('Tr1', 'N/A'),
                                'Tr2': event.get('Tr2', 'N/A'),
                        }
                    }
                    team_data['upcoming_match']=event_data
        if not team_data['upcoming_match']:
            team_data['upcoming_match'] = "No data found"
        return team_data

    tasks = []
    result = await fetch_data(query)
    for team in result['Teams']:
        tasks.append(fetch_and_load(team))

    all_results = await asyncio.gather(*tasks)

    end_time = time.time() 
    return {'search_result':all_results}


