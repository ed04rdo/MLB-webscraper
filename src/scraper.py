import pandas as pd
import os.path
from bs4 import BeautifulSoup as bs4
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options


mlb_url = "https://www.mlb.com/scores/"
"""

REVISAR FECHA 2023-02-27
HAY UN JUEGO QUE TERMINÓ EN 7 ENTRADAS, CAUSA ERROR

"""
check_date = "2023-03-05"
file_path = os.path.dirname(__file__)


def main():
    driver = open_web_driver()
    driver.get(mlb_url+check_date)
    html = driver.page_source
    soup = parse_html(html)
    driver.close()
    results_df =format_data(soup)
    write_file(results_df)


def open_web_driver():
    options = Options()
    options.add_argument('--disable-blink-features=AutomationControlled') # unable differences between automated browser and standard browser
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument('--incognito')
    options.add_argument('--headless') # WITHOUT LAUNCHING WINDOW BUT SENDS DATA TO CONSOLE
    options.add_argument('--log-level=1') 
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.517 Safari/537.36'
    options.add_argument('user-agent={0}'.format(user_agent))
    driver = webdriver.Chrome(options=options)
    
    return driver

def parse_html(html):
    soup = bs4(html,'html.parser')

    # UNCOMMENT FOR WRITING HTML RESULT ON A TXT FILE FOR ANALYSIS
    with open(file_path+'/../output/bsoup.txt', mode='wt', encoding='utf-8') as file:
        file.write(soup.prettify())
    
    return soup

def format_data(soup):
    results_df = pd.read_csv(file_path+"/../output/results_df.csv")
    results = soup.find_all('div',{'class':'TeamMatchupLayerstyle__TeamMatchupLayerWrapper-sc-7tca6g-0 bFUvsX'})
    
    for result in results:
        teams = result.find_all('div',{'class':'TeamWrappersstyle__DesktopTeamWrapper-sc-uqs6qh-0 fdaoCu'})
        local_score_by_inning = result.find_all('div',{'class':'lineScorestyle__StyledInningCell-sc-1d7bghs-1 fbtTqY'})
        local_score = result.find_all('div',{'class':'lineScorestyle__StyledInningCell-sc-1d7bghs-1 ddFUsj'})
        local_hits_errors = result.find_all('div',{'class':'lineScorestyle__StyledInningCell-sc-1d7bghs-1 bybxiY'})
        
        visit_score_by_inning = result.find_all('div',{'class':'lineScorestyle__StyledInningCell-sc-1d7bghs-1 cCJzxi'})
        visit_score = result.find_all('div',{'class':'lineScorestyle__StyledInningCell-sc-1d7bghs-1 jPCzPZ'})
        visit_hits_errors = result.find_all('div',{'class':'lineScorestyle__StyledInningCell-sc-1d7bghs-1 ggbVFi'})

        results_df.loc[len(results_df)] = [check_date,
                           teams[0].get_text(),
                           teams[1].get_text(),
                           "test",
                           local_score_by_inning[0].get_text(),
                           local_score_by_inning[1].get_text(),
                           local_score_by_inning[2].get_text(),
                           local_score_by_inning[3].get_text(),
                           local_score_by_inning[4].get_text(),
                           local_score_by_inning[5].get_text(),
                           local_score_by_inning[6].get_text(),
                           local_score_by_inning[7].get_text(),
                           local_score_by_inning[8].get_text(),
                           local_score[0].get_text(),
                           local_hits_errors[0].get_text(),
                           local_hits_errors[1].get_text(),
                           "test"]
        
        results_df.loc[len(results_df)] = [check_date,
                           teams[1].get_text(),
                           teams[0].get_text(),
                           "test",
                           visit_score_by_inning[0].get_text(),
                           visit_score_by_inning[1].get_text(),
                           visit_score_by_inning[2].get_text(),
                           visit_score_by_inning[3].get_text(),
                           visit_score_by_inning[4].get_text(),
                           visit_score_by_inning[5].get_text(),
                           visit_score_by_inning[6].get_text(),
                           visit_score_by_inning[7].get_text(),
                           visit_score_by_inning[8].get_text(),
                           visit_score[1].get_text(),
                           visit_hits_errors[0].get_text(),
                           visit_hits_errors[1].get_text(),
                           "test"]
        
    return results_df


def write_file(results_df):
    results_df.to_csv(file_path+"/../output/results_df.csv",index=False)
                           
        
if __name__ == "__main__":
    main()