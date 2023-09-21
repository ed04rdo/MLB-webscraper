import pandas as pd
import os.path
import datetime
from sys import exit
from bs4 import BeautifulSoup as bs4
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options

"""
    SPECIAL CASES CONSIDERATIONS
        CHECK DATE 2023-02-24
            GAMES OF 7 INNINGS CAUSES INDEX OUT OF RANGE
        CHECK DATE 2023-03-01
            GAMES OF 7 INNINGS BUT NOT OUT OF RANGE
            HAS VALUE = ' '
        CHECK DATE 2023-03-15
            CANCELED GAMES
        CHECK DATE 2023-04-02
            EXTRA INNING GAME
"""


def main():
    initialize_vars()
    driver = open_web_driver()
    process(driver)
    driver.close()
    write_file()

def initialize_vars():
    global file_path
    global results_df
    global mlb_url
    global single_date
    global date_range

    file_path = os.path.dirname(__file__)
    results_df = pd.read_csv(file_path+"/../output/multi_date_results_df.csv")
    mlb_url = "https://www.mlb.com/scores/"
    single_date = "2023-04-02"

    start_date = datetime.date(2023,2,24)
    end_date = datetime.date(2023,4,1)
    delta = end_date-start_date
    date_range = [start_date + datetime.timedelta(day) for day in range(0,delta.days+1)]


def validate_date(date):
    if results_df[results_df.game_date == date].game_date.count() != 0:
        print("DATE ALREADY CONTAINED IN DF, TRY ANOTHER")
        exit()

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

def process(driver):
    """
        mode determines if single date or multidate process
        0 = single date process
        1 = multi-date process 
    """
    mode = 1
    if mode == 0:
        validate_date(single_date)
        driver.get(mlb_url+single_date)
        html = driver.page_source
        soup = parse_html(html)
        format_data(soup, single_date)
    else:
        for date in date_range:
            validate_date(str(date))
            print("CURRENTLY WORKING DATE",date)
            driver.get(mlb_url+str(date))
            html = driver.page_source
            soup = parse_html(html)
            format_data(soup,date)


def parse_html(html):
    soup = bs4(html,'html.parser')

    # UNCOMMENT FOR WRITING HTML RESULT ON A TXT FILE FOR ANALYSIS
    # with open(file_path+'/../output/bsoup.txt', mode='wt', encoding='utf-8') as file:
    #    file.write(soup.prettify())
    
    return soup

def format_data(soup,date):
    results = soup.find_all('div',{'class':'grid-itemstyle__GridItemWrapper-sc-cq9wv2-0 gmoPjI'})
    
    for result in results:

        game_status = result.find('span',{'class':'StatusLayerstyle__GameStateWrapper-sc-1s2c2o8-3 feaLYF'})
        print(game_status.get_text())

        if game_status.get_text() != 'Canceled':
            teams = result.find_all('div',{'class':'TeamWrappersstyle__DesktopTeamWrapper-sc-uqs6qh-0 fdaoCu'})
            teams_record = result.find_all('div',{'class':'teamstyle__TeamLabel-sc-1suh43a-3 teamstyle__DesktopRecordWrapper-sc-1suh43a-4 gbRmLr'})

            local_score_by_inning = result.find_all('div',{'class':'lineScorestyle__StyledInningCell-sc-1d7bghs-1 fbtTqY'})
            local_score = result.find_all('div',{'class':'lineScorestyle__StyledInningCell-sc-1d7bghs-1 ddFUsj'})
            local_hits_errors = result.find_all('div',{'class':'lineScorestyle__StyledInningCell-sc-1d7bghs-1 bybxiY'})
            
            visit_score_by_inning = result.find_all('div',{'class':'lineScorestyle__StyledInningCell-sc-1d7bghs-1 cCJzxi'})
            visit_score = result.find_all('div',{'class':'lineScorestyle__StyledInningCell-sc-1d7bghs-1 jPCzPZ'})
            visit_hits_errors = result.find_all('div',{'class':'lineScorestyle__StyledInningCell-sc-1d7bghs-1 ggbVFi'})

            winner = int(local_score[0].get_text()) > int(visit_score[1].get_text())
            tie = int(local_score[0].get_text()) == int(visit_score[1].get_text())
    
            register = full_game_validator(local_score_by_inning, visit_score_by_inning)

            results_df.loc[len(results_df)] = [date,
                            teams[0].get_text(),
                            teams[1].get_text(),
                            teams_record[0].get_text(),
                            register[0],
                            register[2],
                            register[4],
                            register[6],
                            register[8],
                            register[10],
                            register[12],
                            register[14],
                            register[16],
                            local_score[0].get_text(),
                            local_hits_errors[0].get_text(),
                            local_hits_errors[1].get_text(),
                            "W" if winner else ("T" if winner or tie else "L")]

            results_df.loc[len(results_df)] = [date,
                            teams[1].get_text(),
                            teams[0].get_text(),
                            teams_record[1].get_text(),
                            register[1],
                            register[3],
                            register[5],
                            register[7],
                            register[9],
                            register[11],
                            register[13],
                            register[15],
                            register[17],
                            visit_score[1].get_text(),
                            visit_hits_errors[0].get_text(),
                            visit_hits_errors[1].get_text(),
                            "L" if winner else ("T" if winner or tie else "W")]


def full_game_validator(local,visit):
    # GAMES THAT DIDN´T END ON 9 INNINGS
    score_by_inning = []
    for x in range(9):
        try:
            score_by_inning.append(str(local[x].get_text()))
            score_by_inning.append(str(visit[x].get_text()))
        except IndexError as e:
            score_by_inning.append('X')
            score_by_inning.append('X')
    return score_by_inning

def write_file():
    results_df.to_csv(file_path+"/../output/multi_date_results_df.csv",index=False)
                           
        
if __name__ == "__main__":
    main()