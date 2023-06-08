import time
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup

import sqlite3
import pandas as pd
import telegram

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

access_token = '5884635842:AAHwfsQplsJ4BXBLh9U-LLY4CyJ6UV_l0xI'
chat_id = '2016776409'

bot = telegram.Bot(token=access_token)

conn = sqlite3.connect("C:\\Users\\USER\\Project.MOS\\ALAM.db", isolation_level=None)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS Info(MID text, info text, chr text, issue text)")
I_df = pd.read_sql("SELECT * FROM Info",conn)

Alam = pd.DataFrame({'MON':[],'MID':[],'ser':[],'tra':[]})
exce = '◎'#알람 제외

async def alamcheck():
    global Alam, exce
    html = driver.page_source
    soup = BeautifulSoup(html,'html.parser')
    c_room = soup.find(string=['<AI_MON:거래감소>','<AI_MON:거래급증>','<AI_MON:성공율하락>','<AI_MON:VAN>','<AI_MON:PG>','<AI_MON:Error>','[VAN] 가상계좌','[VAN] 펌뱅킹'])
    c_li_room = c_room.find_parent('li')
    check = c_li_room.find(class_='new')
    if check:
        for i in check:
            if reversed(i):
                #AI_MON
                AI = soup.find(string=['<AI_MON:거래감소>','<AI_MON:거래급증>','<AI_MON:성공율하락>','<AI_MON:VAN>','<AI_MON:PG>','<AI_MON:Error>'])
                AI_li = AI.find_parent('li')
                AI_N = AI_li.find(class_='new')
                AI_new = AI_N.find_parent('li')
                AI_alam = AI_new.find('dd').get_text()
                if exce not in AI_alam:
                    #MON
                    MON_1 = AI_alam.split('AI_MON:')
                    MON_2 = MON_1[1].split(']',1)
                    MON = MON_2[0]
                    
                    #MID
                    MID_1 = AI_alam.split('가맹점:')
                    MID_2 = MID_1[1].split('[',1)
                    MID_3 = MID_2[1].split(']',1)
                    MID = MID_3[0]
                    
                    #ser
                    ser_1 = AI_alam.split('서비스:')
                    ser_2 = ser_1[1].split('●',1)
                    ser = ser_2[0]
                    #tra
                    tra_1 = AI_alam.split('거래종류:')
                    tra_2 = tra_1[1].split('●',1)
                    tra = tra_2[0]
                    
                    AI_A = AI_alam

                #VAN 가상계좌
                VV = soup.find(string=['<AI_MON:거래감소>','<AI_MON:거래급증>','<AI_MON:성공율하락>','<AI_MON:VAN>','<AI_MON:PG>','<AI_MON:Error>','[VAN] 가상계좌'])
                VV_li = VV.find_parent('li')
                VV_N = VV_li.find(class_='new')
                VV_new = VV_N.find_parent('li')
                VV_alam = VV_new.find('dd').get_text()
                if 'AI_MON' not in VV_alam:
                    #기관코드
                    VV_code_1 = VV_alam.replace('(주)','')
                    VV_code_2 = VV_code_1.split('(',1)
                    VV_code_3 = VV_code_2[1].split(')',1)
                    vv_code = VV_code_3[0]
                    
                    VV_A = VV_alam

                #VAN 펌뱅킹
                VF = soup.find(string=['<AI_MON:거래감소>','<AI_MON:거래급증>','<AI_MON:성공율하락>','<AI_MON:VAN>','<AI_MON:PG>','<AI_MON:Error>','[VAN] 펌뱅킹'])
                VF_li = VF.find_parent('li')
                VF_N = VF_li.find(class_='new')
                VF_new = VF_N.find_parent('li')
                VF_alam = VF_new.find('dd').get_text()
                if 'AI_MON' not in VF_alam:
                    VF_A = VF_alam

                #DB 반영
                try:
                    if AI_A:
                        Alam.loc[0] = [MON,MID,ser,tra]
                    elif VV_A:
                        if 'autocancel' in VV_A:
                            Alam.loc[0] = [VV_A,'autocancel','','']
                        else:
                            Alam.loc[0] = [VV_A,VV_code,'Timeout','']
                    elif VF_A:
                        Alam.loc[0] = [VF_A,'','','']
                    #await bot.sendMessage(chat_id=chat_id, text=df_d)
                except:
                    pass
                new_alam = driver.find_element(By.CLASS_NAME,'chat_list').find_element(By.CLASS_NAME,'new')
                new_alam.click()
                out = driver.find_element(By.CLASS_NAME,'item_chat')
                out.click()
                driver.get(driver.current_url)
                time.sleep(1)
    else:
        pass
    df_merge = pd.merge(Alam, I_df, how='left', left_on='MID', right_on='MID')
    if not df_merge['MID'].empty:
        df_merge = df_merge.to_string(header=False,index=False,line_width=1)
        await bot.sendMessage(chat_id=chat_id, text=df_merge)
    return df_merge

await alamcheck()