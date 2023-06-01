import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import sqlite3

conn = sqlite3.connect("C:\\Users\\USER\\Project.MOS\\ALAM.db", isolation_level=None)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS Alam(alam text, MID text)")
c.execute("CREATE TABLE IF NOT EXISTS Info(MID text, info text)")

c.execute("SELECT * FROM Info")
i_df = c.fetchall()
i_cols = [column[0] for column in c.description]
info_df = pd.DataFrame.from_records(data=i_df, columns=i_cols)

Options = webdriver.ChromeOptions()
Options.add_argument('--blink-settings=imagesEnabled=false')

driver = webdriver.Chrome('C:\\Users\\USER\\chromedriver.exe',options = Options)
url = "https://talk.worksmobile.com/#/"
driver.get(url)
driver.implicitly_wait(1)

def login():
    id_box = driver.find_element_by_css_selector('#login_param')
    login_button_1 = driver.find_element_by_css_selector('#loginStart')
    act = ActionChains(driver)
    print("아이디를 입력하세요.")
    id = input("ID: ")    #아이디 입력받기
    act.send_keys_to_element(id_box, '{}'.format(id)).click(login_button_1).perform()
    time.sleep(1)
    
    password_box = driver.find_element_by_css_selector('#password')
    login_button_2 = driver.find_element_by_css_selector('#loginBtn')
    act = ActionChains(driver)
    print("비밀번호를 입력하세요.")
    password = input("PASSWORD: ")
    act.send_keys_to_element(password_box, '{}'.format(password)).click(login_button_2).perform()
    time.sleep(1)
    
    SMS = driver.find_element_by_css_selector('#phoneNumberButton')
    act = ActionChains(driver)
    act.click(SMS).perform()
    time.sleep(1)
    
    SMS_box = driver.find_element_by_css_selector('#checkNumber > input._authNo._authNo1')
    act = ActionChains(driver)
    print("인증번호를 입력하세요.")
    SMS_ID = input("SMS: ")
    act.send_keys_to_element(SMS_box, '{}'.format(SMS_ID)).perform()
    time.sleep(1)

login()

html = driver.page_source
soup = BeautifulSoup(html,'html.parser')

def alamcheck():
    html = driver.page_source
    soup = BeautifulSoup(html,'html.parser')
    c_room = soup.find(string=['<AI_MON:거래감소>','<AI_MON:거래급증>','<AI_MON:성공율하락>','<AI_MON:VAN>','<AI_MON:PG>','<AI_MON:Error>','[VAN] 가상계좌','[VAN] 펌뱅킹'])
    c_li_room = c_room.find_parent('li')
    check = c_li_room.find(class_='new')
    if check:
        for i in check:
            if reversed(i):
                A = soup.find(string=['<AI_MON:거래감소>','<AI_MON:거래급증>','<AI_MON:성공율하락>','<AI_MON:VAN>','<AI_MON:PG>','<AI_MON:Error>','[VAN] 가상계좌'])
                A_li = A.find_parent('li')
                A_N = A_li.find(class_='new')
                A_new = A_N.find_parent('li')
                A_alam = A_new.find('dd').get_text()
                if '●' in A_alam:
                    MID_1 = A_alam.split('가맹점:')
                    MID_2 = MID_1[1].split('[',1)
                    MID_3 = MID_2[1].split(']',1)
                    MID = MID_3[0]
                    c.execute("INSERT INTO Alam(alam, MID) VALUES(?,?)",(A_alam,MID))
                elif '◎' not in A_alam:
                    if 'autocancel' in A_alam:
                        c.execute("INSERT INTO Alam(alam, MID) VALUES(?,?)",(A_alam,'autocancel'))
                    else:
                        A_1 = A_alam.replace('(주)','')
                        A_code_1 = A_1.split('(',1)
                        A_code_2 = A_code_1[1].split(')',1)
                        A_code = A_code_2[0]
                        c.execute("INSERT INTO Alam(alam, MID) VALUES(?,?)",(A_alam,A_code))

                B = soup.find(string=['<AI_MON:거래감소>','<AI_MON:거래급증>','<AI_MON:성공율하락>','<AI_MON:VAN>','<AI_MON:PG>','<AI_MON:Error>','[VAN] 펌뱅킹'])
                B_li = B.find_parent('li')
                B_N = B_li.find(class_='new')
                B_new = B_N.find_parent('li')
                B_alam = B_new.find('dd').get_text()
                if '●' in B_alam:
                    pass
                elif '◎' not in B_alam:
                    c.execute("INSERT INTO Alam(alam, MID) VALUES(?,?)",(B_alam,''))
            else:
                pass
            new_alam = driver.find_element(By.CLASS_NAME,'chat_list').find_element(By.CLASS_NAME,'new')
            new_alam.click()
            out = driver.find_element(By.CLASS_NAME,'item_chat')
            out.click()
            driver.get(driver.current_url)
            time.sleep(1)
    else:
        pass
    c.execute("SELECT * FROM Alam ORDER BY ROWID DESC LIMIT 10")
    df = c.fetchall()
    cols = [column[0] for column in c.description]
    Alam_df = pd.DataFrame.from_records(data=df, columns=cols)
    return Alam_df