import os
import sys
import random
import time
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
import requests

# Load environment variables from .env file
def load_env_file(env_file=".env"):
    if not os.path.exists(env_file):
        raise FileNotFoundError(f"Environment file `{env_file}` not found.")
    with open(env_file, 'r') as file:
        for line in file:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key.strip()] = value.strip()

# Call load_env_file to populate environment variables
load_env_file()

# Retrieve email addresses from environment variables
GD_DEFAULT_EMAIL_ADDRESS = os.getenv('GD_DEFAULT_EMAIL_ADDRESS', 'default_gd_email@example.com') # For Glassdoor
LI_DEFAULT_EMAIL_ADDRESS = os.getenv('LI_DEFAULT_EMAIL_ADDRESS', 'default_li_email@example.com') # For LinkedIn
EXCEPT_GD_LI_DEFAULT_EMAIL_ADDRESS = os.getenv('EXCEPT_GD_LI_DEFAULT_EMAIL_ADDRESS', 'default_except_email@example.com') # Except for LinkedIn & Glassdoor

# Extended list of possible user agents
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0',
    'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36'
]

# List of possible proxies (use a proxy pool service or free proxies list)
PROXIES = [
    'http://130.61.171.71:80',
]

# Utility functions
def yellow_text(text):
    return f"\033[93m{text}\033[0m"

def blue_text(text):
    return f"\033[94m{text}\033[0m"

def get_random_user_agent():
    return random.choice(USER_AGENTS)

def get_random_proxy():
    return {'http': random.choice(PROXIES), 'https': random.choice(PROXIES)}

def translate_job_location(job_location: str):
    deu_to_eng = {'München': 'Munich'}
    return deu_to_eng.get(job_location, job_location)

# Web scrapers
def linkedin_web_scraper(url: str):
    url = url.partition('?')[0].strip()
    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.google.com/'
    }
    session = requests.Session()
    proxy = get_random_proxy()
    time.sleep(random.uniform(1, 5))
    response = session.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    job_title = soup.find('h1', class_='topcard__title').get_text(strip=True)
    company_name = soup.find('a', class_='topcard__org-name-link').get_text(strip=True)
    company_website = soup.find('a', class_='topcard__org-name-link')['href'].partition('?')[0].strip()

    return {
        'job_url': url,
        'job_title': job_title,
        'company_name': company_name,
        'company_website': company_website,
    }

def glassdoor_web_scraper():
    directory = Path(__file__).parent / 'glassdoor_job_pages'
    html_files = list(directory.glob('*.html')) + list(directory.glob('*.htm'))
    latest_file = max(html_files, key=lambda f: f.stat().st_mtime) if html_files else None
    if not latest_file:
        raise FileNotFoundError(f"No .html/.htm files in directory `{directory}`.")
    
    with latest_file.open('r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    job_string = soup.find('meta', property='og:title')['content']
    job_url = soup.find('meta', property='og:url')['content'] if soup.find('meta', {'property': 'og:url'}) else "N/A"
    
    company_name, job_title_location = job_string.split(" bietet Job als ")
    job_title, location = job_title_location.split(" in ")
    location = location.split(" | ")[0]

    company_website = "Company website not found"
    schema = soup.find('script', type='application/ld+json')
    if schema:
        job_data = schema.string
        if '"sameAs":"' in job_data:
            start_index = job_data.index('"sameAs":"') + len('"sameAs":"')
            end_index = job_data.index('"', start_index)
            company_website = job_data[start_index:end_index]
    
    return {
        'job_url': job_url,
        'job_title': job_title,
        'company_name': company_name,
        'company_website': company_website,
        'job_location': location,
    }

# Main function
def extract_job_info():
    application_date = datetime.now().strftime('%Y-%m-%d')
    status = "Applied"

    main_job_url = input(yellow_text("> (If applicable) Please enter the main job URL: ")).strip()
    linkedin_url_or_gd = input(yellow_text("> Enter the LinkedIn job URL or enter `gd` for Glassdoor Job Ad: ")).strip().lower()

    if not linkedin_url_or_gd:
        raise ValueError('The URL cannot be empty.')

    if main_job_url:
        account_created = input(yellow_text("> Did you create an account for this job application? (Default: `No`): ")).strip().lower()
        account_created = 'TRUE' if account_created in ['yes', 'y', 'true'] else 'FALSE'
    else:
        account_created = 'FALSE'

    if main_job_url:
        email_address = input(yellow_text(f"> Enter the email address used for this application (Default: `{EXCEPT_GD_LI_DEFAULT_EMAIL_ADDRESS}`): ")).strip() or EXCEPT_GD_LI_DEFAULT_EMAIL_ADDRESS
    elif linkedin_url_or_gd == 'gd':
        email_address = input(yellow_text(f"> Enter the email address used for this application (Default: `{GD_DEFAULT_EMAIL_ADDRESS}`): ")).strip() or GD_DEFAULT_EMAIL_ADDRESS
    else:
        email_address = input(yellow_text(f"> Enter the email address used for this application (Default: `{LI_DEFAULT_EMAIL_ADDRESS}`): ")).strip() or LI_DEFAULT_EMAIL_ADDRESS

    if linkedin_url_or_gd == 'gd':
        result = glassdoor_web_scraper()
        job_location = result.get('job_location', 'N/A')
        work_mode = 'unknown'
    else:
        job_location = input(yellow_text("> Enter the job location (Default: `Munich`): ")).strip().capitalize() or "Munich"
        work_mode = input(yellow_text("> Enter the work mode (`hybrid`, `on-site`, or `remote`) (Default: `hybrid`): ")).strip().lower() or "hybrid"
        while True:
            try:
                result = linkedin_web_scraper(url=linkedin_url_or_gd)
            except AttributeError:
                print('[WARN] The LinkedIn Web scraping has failed, trying again..')
                time.sleep(5)
                continue
            break

    job_info_list = [
        application_date,
        status,
        main_job_url if main_job_url else result.get('job_url', 'N/A'),
        result.get('job_url', 'N/A') if main_job_url else "X",
        result.get('company_name', 'N/A'),
        result.get('job_title', 'N/A'),
        result.get('company_website', 'N/A'),
        translate_job_location(job_location),
        work_mode,
        email_address,
        account_created,
    ]

    print(blue_text("\t".join(job_info_list)))

if __name__ == '__main__':
    extract_job_info()
