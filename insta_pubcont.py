'''
Scraping number of posts, followers, following + likes, and comments per photo 
from any public account
'''

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from datetime import datetime
import json, time, os, re


#List of users
user = 'lensational'


'''--------------------
InstAnalytics function
-------------------'''

def InstAnalytics():
    #launch browser

    browser = webdriver.Chrome(executable_path='C:/Users/vchan/Documents/Vera Docs/python/Lensational/chromedriver.exe')
    
        #load JSON
    with open('InstAnalytics.json') as iaFile:
        iaDictionary = json.load(iaFile)
        
    #Backup JSON
    with open('InstAnalytics_backup.json', 'w') as iaFile:
        json.dump(iaDictionary, iaFile, indent=4)
        
    #User's profile
    browser.get('https://instagram.com/' + user)
    time.sleep(0.5)
    
    # Soup
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    
    #User's statistics
    postsT = soup.html.body.span.section.main.article.header.findAll('div',\
    recursive=False)[1].ul.findAll('li', recursive=False)[0].span.findAll('span',recursive=False)[0].getText()
    followersT = soup.html.body.span.section.main.article.header.findAll('div',\
    recursive=False)[1].ul.findAll('li', recursive=False)[1].span.findAll('span',recursive=False)[0].getText()
    followingT = soup.html.body.span.section.main.article.header.findAll('div',\
    recursive=False)[1].ul.findAll('li', recursive=False)[2].span.findAll('span',recursive=False)[0].getText()
    
    #remove all non-numeric characters
    posts = int(re.sub('[^0-9]', '', postsT))
    followers = int(re.sub('[^0-9]', '', followersT))
    following = int(re.sub('[^0-9]', '', followingT))
    
   
    
    #skipped section where it converts k to thousands and m to millions
    if posts > 12:
        #click the 'load more' button
        browser.find_element_by_xpath('/html/body/span/section/main/article/div/div[3]/a').click()
        
    if posts > 24:
        #Load more by scrolling to the bottom of the page
        for i in range(0, (posts-24)//12):
            browser.execute_script('window.scrollTo(0, document.body.scrollHeight)')
            time.sleep(0.1)
            browser.execute_script('window.scrollTo(0,0)')
            time.sleep(0.5)
            
    browser.execute_script('window.scrollTo(0,0)')
    
    #Soup
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    
    #User's phot statistics
    links = []
    for link in soup.html.body.span.section.main.article.findAll('a'):
        if link.get('href')[:3] == '/p/' : links.append(link.get('href'))
            
    photosDic = []
    pLikesT = 0
    pCounter = 0
    
    for link in links:
        #photo id
        pID = link.split("/")[2]
        #Hover over a photo reveals likes and comments
        time.sleep(0.2)
        photo = browser.find_element_by_xpath('//a[contains(@href, "' + pID + '")]')
        time.sleep(0.2) 
        ActionChains(browser).move_to_element(photo).perform()
        #Soup
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        #Likes
        pLikes = int(re.sub('[^0-9]', '', soup.html.body.span.section.main.article.findAll(\
        'div', recursive=False)[0].findAll('div',recursive=False)[0].findAll('a')[pCounter].find(\
        'ul').findAll('li', recursive=False)[0].findAll('span',recursive=False)[0].getText()))
        #Comments
        pComments = int(re.sub('[^0-9]', '', soup.html.body.span.section.main.article.findAll(\
        'div', recursive=False)[0].findAll('div',recursive=False)[0].findAll('a')[pCounter].find(\
        'ul').findAll('li', recursive=False)[1].findAll('span',recursive=False)[0].getText()))
        #Photo dictionary
        photoDic = {
                    'pID': pID,
                    'pLikes': pLikes,
                    'pComments': pComments
        }
        photosDic.append(photoDic)
        #Total likes
        pLikesT += pLikes
        #simple counter
        pCounter += 1
        
    #Dictionary
    userDic = {
                'username' : user,
                'date' : datetime.now().strftime(timeFormat),
                'data' : {
                        'posts' : posts,
                        'followers' : followers,
                        'following' : following,
                        'pLikesT' : pLikesT,
                        'photos' : photosDic
                        }
                }
                    
        #Add data to JSON
    iaDictionary.append(userDic)
    with open('InstAnalytics.json', 'w') as iaFile:
        json.dump(iaDictionary, iaFile, indent=4)
        
    print('|', user)
    
    ##Quit browser
    browser.quit()

def JSONtoCSV():
    
    #Write json data into csv format
    with open('InstAnalytics.csv') as iaCSV:
        

'''------------
Main
------------'''
            
        
        
if __name__ == '__main__':
    
    timeFormat = '%Y-%m-%d'
    
    #Check if the JSON file exists, otherwise create it
    if os.path.isfile('InstAnalytics.json') == False:
        iaDictionary = []
        with open ('InstAnalytics.json', 'w') as iaFile:
            json.dump(iaDictionary, iaFile, indent=4)
            
    InstAnalytics()

    print('Scraping data from', user, 'account every day at 11am\n')

    while True:
        #Scheduled, every day at 11pm
        if datetime.now().hour == 13:
            print(datetime.now().strftime(timeFormat))
            try:
                InstAnalytics()
                time.sleep(82800) #sleep for 23 hours 
            except Exception:
                print('Error')
                time.sleep(30) #Retry after 30s
        else:
            time.sleep(60) #Check every minute
        
        #write json into csv
    