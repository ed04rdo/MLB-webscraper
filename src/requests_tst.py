import pandas as pd
import os.path
import datetime
import multiprocessing
import time

from sys import exit
from requests import get
from bs4 import BeautifulSoup as bs4
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from multiprocessing.pool import ThreadPool

"""
    SPECIAL CASES CONSIDERATIONS
        1. CHECK DATE 2023-02-24
                GAMES OF 7 INNINGS CAUSES INDEX OUT OF RANGE
        2. CHECK DATE 2023-03-01
                GAMES OF 7 INNINGS BUT NOT OUT OF RANGE
                HAS VALUE = ' '
        3. CHECK DATE 2023-03-15
                CANCELED GAMES
        4. CHECK DATE 2023-04-02
                EXTRA INNING GAME
        5. CHECK DATE 2023-04-05
                POSTPONED GAME
"""

def main():
    initialize_vars()
    global results_df
    with ThreadPool(16) as pool:
        date_range_df = pool.map(multi_process,date_range)

    for day_df in date_range_df:
        results_df = pd.concat([results_df,day_df])
    
    write_file()

def single_process():
    """

    """
    validate_date(single_date)
    driver.get(mlb_url+single_date)
    html = driver.page_source
    soup = parse_html(html)
    driver.quit()
    format_data(soup, single_date)
    write_file()
    exit()

def multi_process(date):
    """

    """
    if validate_date(date.isoformat()) == 1:
        return
    
    print("CURRENTLY WORKING DATE",date)
    #start = time.time()
    #print('It took', time.time()-start, 'seconds.')
    html = get(mlb_url+date.isoformat()) 
    soup = parse_html(html.text)
    tmp_df = format_data(soup,date.isoformat())

    return tmp_df
   

def initialize_vars():
    """
        @mode  
            determines if single date or multidate process
            each process works with a different file
                0 = single date process
                1 = multi-date process 

        @single_date
            used in mode 0
        
        @date_range
            used in mode 1
            first set start_date,end_date

        @multi_date_df
            used in mode 1
            output csv file name
        
        @single_date_test_df
            used in mode 0
            output csv file name      
    """

    global mode
    global single_date
    global date_range
    global file_path
    global file
    global results_df
    global mlb_url
    global schema 
     
    mode = 1
    single_date = "2022-04-25"
    start_date = datetime.date(2011,2,1)
    end_date = datetime.date(2011,11,30)
    delta = end_date-start_date
    date_range = [start_date + datetime.timedelta(day) for day in range(0,delta.days+1)]
    multi_date_df = "{}_MLB_Season_df".format(str(start_date.year))
    single_date_test_df = "single_date_test_df"
    schema = ['game_date', 'team', 'opponent', 'record', '1st_inning', '2nd_inning',
            '3rd_inning', '4th_inning', '5th_inning', '6th_inning', '7th_inning',
            '8th_inning', '9th_inning', '10th_inning', '11th_inning', '12th_inning',
            '13th_inning', '14th_inning', '15th_inning', '16th_inning', '17th_inning', 
            '18th_inning', '19th_inning', '20th_inning', '21th_inning', '22th_inning', 
            '23th_inning', '24th_inning', '25th_inning', '26th_inning', 'extra_inning', 
            'total_innings', 'runs', 'hits', 'errors', 'result']
    
    file_path = os.path.dirname(__file__)
    file = multi_date_df if mode == 1 else single_date_test_df
    results_df = pd.read_csv(file_path+"/../output/{}.csv".format(file))
    mlb_url = "https://www.mlb.com/scores/"


def validate_date(date):
    if results_df[results_df.game_date == date].game_date.count() != 0 and mode == 0:
        print("DATE ALREADY CONTAINED IN DF, TRY ANOTHER")
        exit()
    elif results_df[results_df.game_date == date].game_date.count() != 0 and mode == 1:
        print("DATE ALREADY CONTAINED IN DF, SKIPPING TO NEXT DATE")
        return 1

def open_web_driver():
    options = Options()
    options.add_argument('--disable-blink-features=AutomationControlled') # unable differences between automated browser and standard browser
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("prefs", { "profile.managed_default_content_settings.images": 2}) # block image loading
    options.add_argument('--incognito')
    options.add_argument('--headless') # WITHOUT LAUNCHING WINDOW BUT SENDS DATA TO CONSOLE
    options.add_argument('--log-level=1') 
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.517 Safari/537.36'
    options.add_argument('user-agent={0}'.format(user_agent))
    driver = webdriver.Chrome(options=options)

    return driver

def parse_html(html):
    soup = bs4(html,'html.parser')
    """
        # UNCOMMENT FOR WRITING HTML RESULT ON A TXT FILE FOR ANALYSIS
        # with open(file_path+'/../output/bsoup.txt', mode='wt', encoding='utf-8') as file:
        #    file.write(soup.prettify())
    """
    return soup


def format_data(soup,date):

    tmp_df = pd.DataFrame(columns=schema)

    results = soup.find_all('div',{'class':'grid-itemstyle__GridItemWrapper-sc-cq9wv2-0 gmoPjI'})
    
    for result in results:

        game_status = result.find('span',{'class':'StatusLayerstyle__GameStateWrapper-sc-1s2c2o8-3 feaLYF'})

        if game_status.get_text() != 'Canceled' and game_status.get_text() != 'Postponed':
            teams = result.find_all('div',{'class':'TeamWrappersstyle__DesktopTeamWrapper-sc-uqs6qh-0 fdaoCu'})
            teams_record = result.find_all('div',{'class':'teamstyle__TeamLabel-sc-1suh43a-3 teamstyle__DesktopRecordWrapper-sc-1suh43a-4 gbRmLr'})

            local_score_by_inning = result.find_all('div',{'class':'lineScorestyle__StyledInningCell-sc-1d7bghs-1 fbtTqY'})
            local_score = result.find_all('div',{'class':'lineScorestyle__StyledInningCell-sc-1d7bghs-1 ddFUsj'})
            local_hits_errors = result.find_all('div',{'class':'lineScorestyle__StyledInningCell-sc-1d7bghs-1 bybxiY'})
            
            visit_score_by_inning = result.find_all('div',{'class':'lineScorestyle__StyledInningCell-sc-1d7bghs-1 cCJzxi'})
            visit_score = result.find_all('div',{'class':'lineScorestyle__StyledInningCell-sc-1d7bghs-1 jPCzPZ'})
            visit_hits_errors = result.find_all('div',{'class':'lineScorestyle__StyledInningCell-sc-1d7bghs-1 ggbVFi'})

            try:
                winner = int(local_score[0].get_text()) > int(visit_score[1].get_text())
                tie = int(local_score[0].get_text()) == int(visit_score[1].get_text())
            except:
                continue

            register = full_game_validator(local_score_by_inning, visit_score_by_inning)

            tmp_df.loc[len(tmp_df)] = [date,
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
                                    register[18],
                                    register[20],
                                    register[22],
                                    register[24],
                                    register[26],
                                    register[28],
                                    register[30],
                                    register[32],
                                    register[34],
                                    register[36],
                                    register[38],
                                    register[40],
                                    register[42],
                                    register[44],
                                    register[46],
                                    register[48],
                                    register[50],
                                    "Y" if register[18] != "X" else "N",
                                    register[52],
                                    local_score[0].get_text(),
                                    local_hits_errors[0].get_text(),
                                    local_hits_errors[1].get_text(),
                                    "W" if winner else ("T" if winner or tie else "L")]

            tmp_df.loc[len(tmp_df)] = [date,
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
                                    register[19],
                                    register[21],
                                    register[23],
                                    register[25],
                                    register[27],
                                    register[29],
                                    register[31],
                                    register[33],
                                    register[35],
                                    register[37],
                                    register[39],
                                    register[41],
                                    register[43],
                                    register[45],
                                    register[47],
                                    register[49],
                                    register[51],
                                    "Y" if register[18] != "X" else "N",
                                    register[52],
                                    visit_score[1].get_text(),
                                    visit_hits_errors[0].get_text(),
                                    visit_hits_errors[1].get_text(),
                                    "L" if winner else ("T" if winner or tie else "W")]
    return tmp_df


def full_game_validator(local,visit):
    # GAMES THAT DIDN´T END ON 9 INNINGS
    score_by_inning = []
    for inning in range(26):
        try:
            score_by_inning.append(str(local[inning].get_text()) if str(local[inning].get_text()) != ' ' else 'X')
            score_by_inning.append(str(visit[inning].get_text()) if str(visit[inning].get_text()) != ' ' else 'X')
        except IndexError as e:
            score_by_inning.append('X')
            score_by_inning.append('X')
    score_by_inning.append((score_by_inning.index('X')+1)//2)
    return score_by_inning

def write_file():
    results_df.to_csv(file_path+"/../output/{}.csv".format(file),index=False)
                           
        
if __name__ == "__main__":
    main()