# 사용자가 옵션을 선택하는 동작, 글자를 입력하거나 버튼을 클릭하거나 등의 동작이 필요하다면 selenium 이라는 패키지로 해결 가능
# 동작 없이 페이지에 접속하여 바로 데이터를 가져와도 된다면 requests도 좋은 선택

# selenium 을 사용하기 위해서 브라우저를 제어하기 위한 WebDriver 필요

import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By

browser = webdriver.Chrome()
browser.maximize_window() # 창 크기 최대화

# 1. 페이지 이동
url = 'https://finance.naver.com/sise/sise_market_sum.naver?&page='
browser.get(url)

# 2. 조회항목 초기화 (체크되어있는 항목 해제) : F12 개발자 도구
checkboxes = browser.find_elements(By.NAME,'fieldIds') # filedIDs 를 NAME으로 가지는 객체에 접근
for checkbox in  checkboxes : 
    if checkbox.is_selected(): # 체크된 상태라면
        checkbox.click() # 클릭(체크 해제)

# 3. 조회 항목 설정 (원하는 항목 체크)
# items_to_select = ['영업이익', '자산총계', '매출액']
items_to_select = ['시가', '고가', '저가']
for checkbox in checkboxes:
    parent =  checkbox.find_element(By.XPATH, '..') # 부모 element 찾기
    label = parent.find_element(By.TAG_NAME,'label')
    # print(label.text) # 이름 확인
    
    if label.text in items_to_select: # 선택 항목과 일치한다면
        checkbox.click() # 체크

# 4. 적용하기 버튼 클릭
btn_apply = browser.find_element(By.XPATH, '//a[@href="javascript:fieldSubmit()"]')
btn_apply.click()


for idx in range(1, 40): # 1~ 40 미만 페이지 반복
    # 사전 작업 : 페이지 이동
    browser.get(url+str(idx)) # page = idx 

    # 5. 데이터 추출 pandas : read_html (자동으로 테이블 elements를 식별하여 가져와줌)
    df = pd.read_html(browser.page_source)[1]
    # 결측치가 있는 행열 삭제 : index (가로 기준) / column (세로 기준) / how = 'all' : 특정 행열이 모두 NaN 값 일때 / inplace
    df.dropna(axis='index', how='all', inplace=True)
    df.dropna(axis='columns',how='all',inplace=True)
    if len(df) == 0 : # 더 이상 가져올 데이터가 없으면
        break

    # 6. 데이터 파일 저장
    f_name = 'sise.csv'
    if os.path.exists(f_name): # 파일이 있다면 헤더 제외
        df.to_csv(f_name, encoding='utf-8-sig', index=False, mode='a', header=False)
    else: # 파일이 없다면 헤더 포함
        df.to_csv(f_name, encoding='utf-8-sig', index=False)
    print(f'{idx} 페이지 완료')


browser.quit() # 브라우저 종료