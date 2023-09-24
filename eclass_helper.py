import numpy as np
import pandas as pd
import openpyxl
import getpass
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from seleniumbase import Driver 
import time 

myid = ''
mypwd = ''

if myid == '' or mypwd == '':
    myid = getpass.getpass("your id: (hidden)")
    mypwd = getpass.getpass("your password: (hidden)")

url_login = "https://sso1.mju.ac.kr/login.do?redirect_uri=https://home.mju.ac.kr/user/index.action"
url_classes = "https://home.mju.ac.kr/course/courseList.action?command=main&tab=course"
url_assignments = "https://home.mju.ac.kr/mainIndex/myHomeworkList.action?command=&tab=homework"

# headless인수를 False로 주면 인터넷 창 안 보임(대신 막힐 가능성 상승)
driver = Driver(browser="chrome", headless=True) 
driver.get(url_login)
driver.implicitly_wait(1)

# id, pw 입력할 곳을 찾 고 입력
print('login')
tag_id = driver.find_element(By.ID, 'id').send_keys(myid)
tag_pw = driver.find_element(By.ID, 'passwrd').send_keys(mypwd)

# 로그인 버튼을 클릭합니다
login_btn = driver.find_element(By.ID, 'loginButton').click()
driver.implicitly_wait(2)

# get assignments info
print('assignment')
assign_url_elements = driver.find_elements(By.CSS_SELECTOR, "#FrameRight > ul > li > dl > dt > a")
assgin_name_elements = driver.find_elements(By.CSS_SELECTOR, "#FrameRight > ul > li > dl > dt > a > strong")
assign_date_elements = driver.find_elements(By.CSS_SELECTOR, "#FrameRight > ul > li > dl > dd.information > p:nth-child(2) > span:nth-child(2)")
assign_submit_elements = driver.find_elements(By.CSS_SELECTOR, 
    "#FrameRight > ul > li > dl > dd.information > p:nth-child(3) > span:nth-child(2)")

assign_url = [e.get_attribute("href") for e in assign_url_elements]
assign_name = [e.text for e in assgin_name_elements] 
assign_date = [e.text for e in assign_date_elements]
assign_submit = [e.text for e in assign_submit_elements]
assignments = {'type':['assign']*len(assign_url), 'name': assign_name, 'url': assign_url,
                 'date':assign_date, 'submit': assign_submit}

# get class urls 
print('class list')
driver.get(url_classes)
class_elements = driver.find_elements(By.CSS_SELECTOR, "#FrameRight > table > tbody > tr > td:nth-child(2)")
class_names = [frame.text for frame in class_elements]
class_btns = driver.find_elements(By.LINK_TEXT, "바로가기")
class_urls = [btn.get_attribute("href") for btn in class_btns]

print('each class')
post_type = []
post_names = []
post_urls = []
post_parents = []
post_parent_urls = []
# get name and url of posts from urls
for i in range(len(class_names)):
    print(i) 
    driver.get(class_urls[i])
    driver.implicitly_wait(1)
    posts_btn = driver.find_elements(By.CSS_SELECTOR, "#MainContent a:not(.more)")
    post_count = len(posts_btn)
    if post_count == 0:
        continue 
    post_urls += [post.get_attribute("href") for post in posts_btn]
    post_names += [post.text for post in posts_btn]
    post_type += ['post']*post_count
    post_parents += [class_names[i]]*post_count
    post_parent_urls += [class_urls[i]]*post_count
posts = {'type': post_type, 'name': post_names, 'url': post_urls, 'parent': post_parents, 'parent_url':post_parent_urls}

# parse data to panda dataFrame and print posts info
assignments_df = pd.DataFrame(assignments)
posts_df = pd.DataFrame(posts)
print(assignments_df)
print(posts_df)

# save data
with pd.ExcelWriter(path='posts.xlsx') as writer:
    assignments_df.to_excel(writer, sheet_name='assignments')
    posts_df.to_excel(writer, sheet_name='posts')