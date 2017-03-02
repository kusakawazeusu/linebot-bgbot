# -*- coding: utf8 -*-
import urllib2
import re
import MySQLdb
import jianfan
from bs4 import BeautifulSoup

# 存放遊戲連結
good_links = []

# 目前擷取：Boardgamegeek
for i in range(11,31):
    url = 'https://www.boardgamegeek.com/browse/boardgame/page/' + str(i)
    response = urllib2.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(''.join(html),"html.parser")

    for tags in soup.find_all('div',{'id':re.compile("^results_objectname")}):
        for games in tags.find_all('a',{'href':re.compile("^/boardgame/")}):
            bid = games['href'].split('/')
            good_links.append(bid[2])

db = MySQLdb.connect('127.0.0.1','root','kuanting','BGbot',charset='utf8', init_command='SET NAMES UTF8')

for bggid in good_links:
    url = 'https://www.boardgamegeek.com/xmlapi/boardgame/' + bggid + '?&stats=1'
    response = urllib2.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(''.join(html),'xml')
        
    name_eng = soup.find('name',{'primary':'true'}).string

    name_cht_possible = soup.find_all('name')
        
    find = 0 # 是否有找到中文名字
    for name in name_cht_possible:
        name = name.string
        for character in name:
            if( u'\u4e00' <= character <= u'\u9fff'):
                name = name.encode('utf8')
                name_cht = jianfan.jtof(name)
                find = 1
                break
        if find == 0:
            name_cht = 'No cht name'
            
    rating = soup.find('usersrated').string
    player_min = soup.find('minplayers').string
    player_max = soup.find('maxplayers').string
    game_time = soup.find('maxplaytime').string
    publish_year = soup.find('yearpublished').string
        
    imgsrc = soup.find('image').string
    imgsrc = imgsrc.split('/')[4]

    total_rank = soup.find('rank',{'name':'boardgame'})['value']
    print total_rank

    cata = soup.find_all('rank',{'name': lambda x: x!= 'boardgame'})
    if len(cata) > 0:
        cata2_name = cata[0]['friendlyname']
        cata2_rank = cata[0]['value']
    if len(cata) > 1:
        cata3_name = cata[1]['friendlyname']
        cata3_rank = cata[1]['value']
    else:
        cata3_name = 'null'
        cata3_rank = '0'
        
    if len(cata) > 2:
        print 'i have more than two catas'
        print len(cata)

            
        
        

    cursor = db.cursor()
    sql = """INSERT INTO games(name_eng,name_chinese,bggid,rating,player_min,player_max, \
            publish_year,game_time,catalog1_rank,catalog2,catalog2_rank,catalog3,catalog3_rank,imgsrc) \
            VALUES ("%s","%s","%s","%d","%d","%d","%d","%d","%d","%s","%d","%s","%d","%s")""" % \
            (name_eng,name_cht,bggid,int(rating),int(player_min),int(player_max),int(publish_year),int(game_time),int(total_rank),cata2_name,int(cata2_rank),cata3_name,int(cata3_rank),imgsrc)
            
    cursor.execute(sql)
    print 'Insert Completed : %s , %s' % (name_eng,name_cht)
    db.commit()

db.close()