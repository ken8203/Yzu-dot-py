#! /usr/bin/python
# -*- coding: utf8 -*-

import re, sys, json, time, random, urllib2, cookielib
from urllib import urlencode
from bs4 import BeautifulSoup

class Yzu:
    '''
    A class contains functions about accessing YZU portal.
    By Jay Chung
    '''

    # do with cookie
    cookie_support= urllib2.HTTPCookieProcessor(cookielib.CookieJar())
    opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip,deflate,sdch',
        'Accept-Language': 'zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4',
        'Cache-Control': 'max-age=0',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36'
    }

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def login(self):
        url = 'https://portal.yzu.edu.tw/logincheck_new.aspx'
        form_data = {'uid': self.username, 'pwd': self.password}

        # get the cookie
        Yzu.opener.open(url, urlencode(form_data))
        urllib2.install_opener(Yzu.opener)

        # check if user login successfully
        portal_page = urllib2.urlopen('https://portal.yzu.edu.tw/Index_Survey.aspx').read()
        if portal_page.find('登入逾時') == -1:
            return False
        else:
            return True
        
    def get_course_credits(self):
        credit_info = dict()

        # access portal menu page
        portal_left_menu_url = 'https://portal.yzu.edu.tw/Left_index.aspx'
        grade_page_url = 'https://portal.yzu.edu.tw/VC2/Student/console/My_Stdregi_Score.aspx'
        portal_left_menu = urllib2.urlopen(portal_left_menu_url).read()
        student_profile_url = 'https://portal.yzu.edu.tw/' + re.findall(r"<a class=\"left_menu\" href='(.*?)' target='_top'>", portal_left_menu)[0].replace('..', '')
        urllib2.urlopen(student_profile_url)

        # get the semester_list
        grade_page = urllib2.urlopen(grade_page_url).read()
        semester_list = re.findall(r'<option.*?value="(.*?)">', grade_page)

        form_data = {
            '__EVENTTARGET': 'DropDownList2', 
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            '__VIEWSTATE': '/wEPDwULLTEzOTQyNjQwNzIPZBYCAgEPZBYMAgEPZBYIZg8PFgIeBFRleHQFC+ioiuaBryAoMTcpZGQCAQ8PFgIfAGVkZAICDw8WAh8AZWRkAgMPDxYCHwBlZGQCBQ8QDxYGHg1EYXRhVGV4dEZpZWxkBQdkaXNwbGF5Hg5EYXRhVmFsdWVGaWVsZAUFdmFsdWUeC18hRGF0YUJvdW5kZ2QQFQcVMTAw5a245bm0IOesrDEg5a245pyfFTEwMOWtuOW5tCDnrKwyIOWtuOacnxUxMDDlrbjlubQg56ysMyDlrbjmnJ8VMTAx5a245bm0IOesrDEg5a245pyfFTEwMeWtuOW5tCDnrKwyIOWtuOacnxUxMDLlrbjlubQg56ysMSDlrbjmnJ8VMTAy5a245bm0IOesrDIg5a245pyfFQcFMTAwLzEFMTAwLzIFMTAwLzMFMTAxLzEFMTAxLzIFMTAyLzEFMTAyLzIUKwMHZ2dnZ2dnZ2RkAgYPD2QWAh4HT25jbGljawUSamF2YXNjcmlwdDp0ZXN0KCk7ZAIIDw8WAh8ABSTlrbjliIblsI/oqIg6IDI2ICAg5bey6YGO5a245YiG77yaMjZkZAIKDw8WBh4IQ3NzQ2xhc3MFB3RhYmxlXzEeBVdpZHRoGwAAAAAAoIRAAQAAAB4EXyFTQgKCAmRkAgwPDxYCHwBlZGRkctnX7qhfZ9EwZu5JJzuVyPgLMMtENWkviSmrxdO/zlc=',
            '__EVENTVALIDATION': '/wEdAApRFkRsigzCAY8gQIHwPsgS0Tx48zdi+nUOQef8HWeKXTrKVJ4rSo/VmreZUyLUTPnAPBEeknvFXKGUq8uchx77coi1Nx/JT1vh5Xz90Tg7udExRrPKpUrM8vrqznR3k0zLN4JO4XGhTcb9Kxi6YRjScctQgn/jLqA1aM7q1ZxcDdx7juoTtAEYQqAO5miotHtZ2dGYdmpix2hYFZPmaQFYoc8bbxA4zdumTeqNOZM81TlWtvYM1f+avgFplzXeuRk=',
            'agree': '',
            'x': ''
        }

        for semester in semester_list:
            credit_info[semester] = []

            form_data['DropDownList2'] = semester
            request = urllib2.Request(
                url = grade_page_url,
                headers = Yzu.headers,
                data = urlencode(form_data)
            )
            response = urllib2.urlopen(request).read()

            beauty_response = BeautifulSoup(response)
            tr_list = beauty_response.find('table', id='Table1').find_all('tr')[1:]
            for tr in tr_list:
                td_list = tr.find_all('td')
                course_code = td_list[2].text.encode('utf8')
                course_name = td_list[4].contents[0].encode('utf8')
                course_credit = td_list[6].text.encode('utf8')
                course_grade = td_list[7].text.encode('utf8')

                credit_info[semester].append([course_code, course_name, course_credit, course_grade])

        # 依照學期分類
        return credit_info

    def get_classic_point(self):
        classic_info = dict()

        # access portal menu page
        portal_left_menu_url = 'https://portal.yzu.edu.tw/Left_index.aspx'
        portal_left_menu = urllib2.urlopen(portal_left_menu_url).read()
        student_profile_url = 'https://portal.yzu.edu.tw/' + re.findall(r"<a class=\"left_menu\" href='(.*?)' target='_top'>", portal_left_menu)[0].replace('..', '')
        urllib2.urlopen(student_profile_url)

        fifty_point_page_url = 'https://portal.yzu.edu.tw/VC2/Student/Book50/StdGetPoint.aspx'
        fifty_point_page = urllib2.urlopen(fifty_point_page_url).read()
        beauty_fifty_point_page = BeautifulSoup(fifty_point_page)
        
        tr_list = beauty_fifty_point_page.find('div', id='Div_B50GetPoint').find_all('tr')
        tr_list = tr_list[1:len(tr_list)-1]
        for tr in tr_list:
            td_list = tr.find_all('td')

            semester = td_list[0].text.encode('utf8')
            if semester not in classic_info.keys():
                classic_info[semester] = []

            time = td_list[1].text.encode('utf8')
            teacher = td_list[2].text.encode('utf8')
            book_name = td_list[3].text.encode('utf8')
            category = td_list[4].text.encode('utf8')
            point = td_list[5].text.encode('utf8')
            note = td_list[6].text.encode('utf8')

            classic_info[semester].append([time, teacher, book_name, category, point, note])

        return classic_info

    def get_serving_point(self):
        # access portal menu page
        portal_left_menu_url = 'https://portal.yzu.edu.tw/Left_index.aspx'
        portal_left_menu = urllib2.urlopen(portal_left_menu_url).read()
        student_profile_url = 'https://portal.yzu.edu.tw/' + re.findall(r"<a class=\"left_menu\" href='(.*?)' target='_top'>", portal_left_menu)[0].replace('..', '')
        urllib2.urlopen(student_profile_url)

        student_profile_left_menu_url = 'https://portal.yzu.edu.tw/VC2/Student/classLeft_S.aspx'
        student_profile_left_menu = urllib2.urlopen(student_profile_left_menu_url).read()
        serve_learn_page_url = 'https://portal.yzu.edu.tw/' + re.findall(r'<a class="left_menu" href="(.*?)" target="main"   title="服務學習檔案">', student_profile_left_menu)[0].replace('..', '')
        serve_learn_page = urllib2.urlopen(serve_learn_page_url)
        serve_learn_record_page_url = 'https://portal.yzu.edu.tw/Ser_learn/stdserv_std/ser_std_recdata.asp'
        serve_learn_record_page = urllib2.urlopen(serve_learn_record_page_url).read()

        hour_data = re.findall(r'<font color="#669900">(.*?)</font>', serve_learn_record_page)[1]
        return re.findall(r'\d+', hour_data)

    def get_all_course(self, semester):
        # access the global course page
        global_course_page_url = 'https://portal.yzu.edu.tw/vc2/global_cos.aspx'
        global_course_page = urllib2.urlopen(global_course_page_url).read()
        beauty_global_course_page = BeautifulSoup(global_course_page)

        # parse the department list
        DDL_Dept_select = beauty_global_course_page.find('select', id='DDL_Dept')
        all_DDL_Dept = re.findall(r'<option.*?value="(.*?)">', str(DDL_Dept_select))

        for DDL_Dept in all_DDL_Dept:
            # first time post payload
            payload = {
                '__EVENTTARGET': 'DDL_Dept',
                '__EVENTARGUMENT': '',
                '__LASTFOCUS': '',
                '__VIEWSTATE': '/wEPDwUJNjkxNzU2MjcxD2QWAgIBD2QWHGYPDxYCHgRUZXh0BRjlhYPmmbrlpKflrbjoqrLnqIvmn6XoqaJkZAIBD2QWAmYPZBYCZg9kFhQCAQ8QDxYEHwAFDOezu+aJgOafpeipoh4HQ2hlY2tlZGdkZGRkAgMPEA8WBB8ABQ/oqrLnqIvpl5zpjbXlrZcfAWhkZGRkAgUPEA8WBB8ABQzmlZnluKvlp5PlkI0fAWhkZGRkAgcPEA8WBB8ABQzmmYLplpPmn6XoqaIfAWhkZGRkAgkPEA8WBB8ABQ/oqrLntrHpl5zpjbXlrZcfAWhkZGRkAgsPEA8WAh8BaGRkZGQCDQ8QDxYEHwAFGOiLseiqnuaOiOiqsuaOqOiWpuiqsueoix8BaGRkZGQCDw8QDxYCHwFoZGRkZAIRDxAPFgIfAWhkZGRkAhMPEA8WBB8ABQ/mmpHmnJ/lhYjkv67oqrIfAWhkZGRkAgIPZBYCAgEPZBYIZg9kFgICAQ8QDxYGHg1EYXRhVGV4dEZpZWxkBQROYW1lHg5EYXRhVmFsdWVGaWVsZAUFVmFsdWUeC18hRGF0YUJvdW5kZ2QQFSUEMTAyMwQxMDIyBDEwMjEEMTAxNQQxMDEzBDEwMTIEMTAxMQQxMDA1BDEwMDMEMTAwMgQxMDAxAzk5NgM5OTUDOTkzAzk5MgM5OTEDOTg2Azk4MgM5ODEDOTc2Azk3NQM5NzQDOTczAzk3MgM5NzEDOTY2Azk2NQM5NjQDOTYzAzk2MgM5NjEDOTU2Azk1NQM5NTQDOTUzAzk1MgM5NTEVJQcxMDIsMyAgBzEwMiwyICAHMTAyLDEgIAcxMDEsNSAgBzEwMSwzICAHMTAxLDIgIAcxMDEsMSAgBzEwMCw1ICAHMTAwLDMgIAcxMDAsMiAgBzEwMCwxICAGOTksNiAgBjk5LDUgIAY5OSwzICAGOTksMiAgBjk5LDEgIAY5OCw2ICAGOTgsMiAgBjk4LDEgIAY5Nyw2ICAGOTcsNSAgBjk3LDQgIAY5NywzICAGOTcsMiAgBjk3LDEgIAY5Niw2ICAGOTYsNSAgBjk2LDQgIAY5NiwzICAGOTYsMiAgBjk2LDEgIAY5NSw2ICAGOTUsNSAgBjk1LDQgIAY5NSwzICAGOTUsMiAgBjk1LDEgIBQrAyVnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZGQCAQ9kFgICAQ8QDxYGHwIFBG5hbWUfAwUHRGVwdF9ubx8EZ2QQFTUi5bel56iL5a246ZmiICAgICAgICAgICAgICAgICAgICAgICHjgIDjgIDmqZ/morDlt6XnqIvlrbjns7vlrbjlo6vnj60w44CA44CA5YyW5a245bel56iL6IiH5p2Q5paZ56eR5a245a2457O75a245aOr54+tKuOAgOOAgOW3pealreW3peeoi+iIh+euoeeQhuWtuOezu+WtuOWjq+ePrSHjgIDjgIDmqZ/morDlt6XnqIvlrbjns7vnoqnlo6vnj60w44CA44CA5YyW5a245bel56iL6IiH5p2Q5paZ56eR5a245a2457O756Kp5aOr54+tKuOAgOOAgOW3pealreW3peeoi+iIh+euoeeQhuWtuOezu+eiqeWjq+ePrS3jgIDjgIDnlJ/niannp5HmioDoiIflt6XnqIvnoJTnqbbmiYDnoqnlo6vnj60k44CA44CA5YWI6YCy6IO95rqQ56Kp5aOr5a245L2N5a2456iLIeOAgOOAgOapn+aisOW3peeoi+WtuOezu+WNmuWjq+ePrTDjgIDjgIDljJblrbjlt6XnqIvoiIfmnZDmlpnnp5Hlrbjlrbjns7vljZrlo6vnj60q44CA44CA5bel5qWt5bel56iL6IiH566h55CG5a2457O75Y2a5aOr54+tIueuoeeQhuWtuOmZoiAgICAgICAgICAgICAgICAgICAgICAb44CA44CA566h55CG5a246Zmi5a245aOr54+tJ+OAgOOAgOeuoeeQhuWtuOmZoue2k+eHn+euoeeQhueiqeWjq+ePrSHjgIDjgIDnrqHnkIblrbjpmaLllYblrbjnoqnlo6vnj60q44CA44CA566h55CG5a246Zmi566h55CG56Kp5aOr5Zyo6IG35bCI54+tG+OAgOOAgOeuoeeQhuWtuOmZouWNmuWjq+ePrSTkurrmlofnpL7mnIPlrbjpmaIgICAgICAgICAgICAgICAgICAh44CA44CA5oeJ55So5aSW6Kqe5a2457O75a245aOr54+tIeOAgOOAgOS4reWci+iqnuaWh+WtuOezu+WtuOWjq+ePrSTjgIDjgIDol53ooZPoiIfoqK3oqIjlrbjns7vlrbjlo6vnj60q44CA44CA56S+5pyD5pqo5pS/562W56eR5a245a2457O75a245aOr54+tIeOAgOOAgOaHieeUqOWkluiqnuWtuOezu+eiqeWjq+ePrSHjgIDjgIDkuK3lnIvoqp7mloflrbjns7vnoqnlo6vnj60y44CA44CA6Jed6KGT6IiH6Kit6KiI5a2457O7KOiXneihk+euoeeQhueiqeWjq+ePrSkq44CA44CA56S+5pyD5pqo5pS/562W56eR5a245a2457O756Kp5aOr54+tIuizh+ioiuWtuOmZoiAgICAgICAgICAgICAgICAgICAgICAh44CA44CA6LOH6KiK5bel56iL5a2457O75a245aOr54+tIeOAgOOAgOizh+ioiueuoeeQhuWtuOezu+WtuOWjq+ePrSHjgIDjgIDos4foqIrlgrPmkq3lrbjns7vlrbjlo6vnj60h44CA44CA6LOH6KiK566h55CG5a2457O756Kp5aOr54+tIeOAgOOAgOizh+ioiuWCs+aSreWtuOezu+eiqeWjq+ePrSfjgIDjgIDos4foqIrnpL7mnIPlrbjnoqnlo6vlrbjkvY3lrbjnqIsh44CA44CA6LOH6KiK5bel56iL5a2457O756Kp5aOr54+tLeOAgOOAgOeUn+eJqeiIh+mGq+WtuOizh+ioiueiqeWjq+WtuOS9jeWtuOeoiyHjgIDjgIDos4foqIrnrqHnkIblrbjns7vljZrlo6vnj60h44CA44CA6LOH6KiK5bel56iL5a2457O75Y2a5aOr54+tEumbu+apn+mAmuioiuWtuOmZoiHjgIDjgIDpm7vmqZ/lt6XnqIvlrbjns7vlrbjlo6vnj60h44CA44CA6YCa6KiK5bel56iL5a2457O75a245aOr54+tIeOAgOOAgOWFiembu+W3peeoi+WtuOezu+WtuOWjq+ePrSHjgIDjgIDpm7vmqZ/lt6XnqIvlrbjns7vnoqnlo6vnj60h44CA44CA6YCa6KiK5bel56iL5a2457O756Kp5aOr54+tIeOAgOOAgOWFiembu+W3peeoi+WtuOezu+eiqeWjq+ePrSHjgIDjgIDpm7vmqZ/lt6XnqIvlrbjns7vljZrlo6vnj60h44CA44CA6YCa6KiK5bel56iL5a2457O75Y2a5aOr54+tIeOAgOOA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5bel56iL5a2457O756Kp5aOr54+tMOOAgOOAgOWMluWtuOW3peeoi+iIh+adkOaWmeenkeWtuOWtuOezu+eiqeWjq+ePrSrjgIDjgIDlt6Xmpa3lt6XnqIvoiIfnrqHnkIblrbjns7vnoqnlo6vnj60t44CA44CA55Sf54mp56eR5oqA6IiH5bel56iL56CU56m25omA56Kp5aOr54+tJOOAgOOAgOWFiOmAsuiDvea6kOeiqeWjq+WtuOS9jeWtuOeoiyHjgIDjgIDmqZ/morDlt6XnqIvlrbjns7vljZrlo6vnj60w44CA44CA5YyW5a245bel56iL6IiH5p2Q5paZ56eR5a245a2457O75Y2a5aOr54+tKuOAgOOAgOW3pealreW3peeoi+iIh+euoeeQhuWtuOezu+WNmuWjq+ePrSLnrqHnkIblrbjpmaIgICAgICAgICAgICAgICAgICAgICAgG+OAgOOAgOeuoeeQhuWtuOmZouWtuOWjq+ePrSfjgIDjgIDnrqHnkIblrbjpmaLntpPnh5/nrqHnkIbnoqnlo6vnj60h44CA44CA566h55CG5a246Zmi5ZWG5a2456Kp5aOr54+tKuOAgOOAgOeuoeeQhuWtuOmZoueuoeeQhueiqeWjq+WcqOiBt+WwiOePrRvjgIDjgIDnrqHnkIblrbjpmaLljZrlo6vnj60k5Lq65paH56S+5pyD5a246ZmiICAgICAgICAgICAgICAgICAgIeOAgOOAgOaHieeUqOWkluiqnuWtuOezu+WtuOWjq+ePrSHjgIDjgIDkuK3lnIvoqp7mloflrbjns7vlrbjlo6vnj60k44CA44CA6Jed6KGT6IiH6Kit6KiI5a2457O75a245aOr54+tKuOAgOOAgOekvuacg+aaqOaUv+etluenkeWtuOWtuOezu+WtuOWjq+ePrSHjgIDjgIDmh4nnlKjlpJboqp7lrbjns7vnoqnlo6vnj60h44CA44CA5Lit5ZyL6Kqe5paH5a2457O756Kp5aOr54+tMuOAgOOAgOiXneihk+iIh+ioreioiOWtuOezuyjol53ooZPnrqHnkIbnoqnlo6vnj60pKuOAgOOAgOekvuacg+aaqOaUv+etluenkeWtuOWtuOezu+eiqeWjq+ePrSLos4foqIrlrbjpmaIgICAgICAgICAgICAgICAgICAgICAgIeOAgOOAgOizh+ioiuW3peeoi+WtuOezu+WtuOWjq+ePrSHjgIDjgIDos4foqIrnrqHnkIblrbjns7vlrbjlo6vnj60h44CA44CA6LOH6KiK5YKz5pKt5a2457O75a245aOr54+tIeOAgOOAgOizh+ioiueuoeeQhuWtuOezu+eiqeWjq+ePrSHjgIDjgIDos4foqIrlgrPmkq3lrbjns7vnoqnlo6vnj60n44CA44CA6LOH6KiK56S+5pyD5a2456Kp5aOr5a245L2N5a2456iLIeOAgOOAgOizh+ioiuW3peeoi+WtuOezu+eiqeWjq+ePrS3jgIDjgIDnlJ/nianoiIfphqvlrbjos4foqIrnoqnlo6vlrbjkvY3lrbjnqIsh44CA44CA6LOH6KiK566h55CG5a2457O75Y2a5aOr54+tIeOAgOOAgOizh+ioiuW3peeoi+WtuOezu+WNmuWjq+ePrRLpm7vmqZ/pgJroqIrlrbjpmaIh44CA44CA6Zu75qmf5bel56iL5a2457O75a245aOr54+tIeOAgOOAgOmAmuioiuW3peeoi+WtuOezu+WtuOWjq+ePrSHjgIDjgIDlhYnpm7vlt6XnqIvlrbjns7vlrbjlo6vnj60h44CA44CA6Zu75qmf5bel56iL5a2457O756Kp5aOr54+tIeOAgOOAgOmAmuioiuW3peeoi+WtuOezu+eiqeWjq+ePrSHjgIDjgIDlhYnpm7vlt6XnqIvlrbjns7vnoqnlo6vnj60h44CA44CA6Zu75qmf5bel56iL5a2457O75Y2a5aOr54+tIeOAgOOAgOmAmuioiuW3peeoi+WtuOezu+WNmuWjq+ePrSHjgIDjgIDlhYnpm7vlt6XnqIvlrbjns7vljZrlo6vnj60P6YCa6K2Y5pWZ5a246YOoIei7jeiok+WupCAgICAgICAgICAgICAgICAgICAgICAgICHpq5TogrLlrqQgICAgICAgICAgICAgICAgICAgICAgICAY5ZyL6Zqb6Kqe6KiA5paH5YyW5Lit5b+DFeWci+mam+WFqeWyuOS6i+WLmeWupBU2AAMzMDADMzAyAzMwMwMzMDUDMzIyAzMyMwMzMjUDMzI5AzMzMAMzNTIDMzUzAzM1NQM1MDADNTA1AzUzMAM1MzEDNTMyAzU1NAM2MDADNjAxAzYwMgM2MDMDNjA0AzYyMQM2MjIDNjIzAzYyNAM3MDADMzA0AzcwMQM3MDIDNzIxAzcyMgM3MjMDNzI0AzcyNQM3NTEDNzU0AzgwMAMzMDEDMzA3AzMwOAMzMjYDMzI3AzMyOAMzNTYDMzU3AzM1OAM5MDEDOTAzAzkwNAM5MDYDOTA3FCsDNmdnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZxYBZmQCAg9kFgICAQ8PFgIfAAUG56K65a6aZGQCCQ8WAh8FaBYCAgEPZBYGZg9kFgJmDxAPFgYfAgUETmFtZR8DBQVWYWx1ZR8EZ2QQFSUEMTAyMwQxMDIyBDEwMjEEMTAxNQQxMDEzBDEwMTIEMTAxMQQxMDA1BDEwMDMEMTAwMgQxMDAxAzk5NgM5OTUDOTkzAzk5MgM5OTEDOTg2Azk4MgM5ODEDOTc2Azk3NQM5NzQDOTczAzk3MgM5NzEDOTY2Azk2NQM5NjQDOTYzAzk2MgM5NjEDOTU2Azk1NQM5NTQDOTUzAzk1MgM5NTEVJQcxMDIsMyAgBzEwMiwyICAHMTAyLDEgIAcxMDEsNSAgBzEwMSwzICAHMTAxLDIgIAcxMDEsMSAgBzEwMCw1ICAHMTAwLDMgIAcxMDAsMiAgBzEwMCwxICAGOTksNiAgBjk5LDUgIAY5OSwzICAGOTksMiAgBjk5LDEgIAY5OCw2ICAGOTgsMiAgBjk4LDEgIAY5Nyw2ICAGOTcsNSAgBjk3LDQgIAY5NywzICAGOTcsMiAgBjk3LDEgIAY5Niw2ICAGOTYsNSAgBjk2LDQgIAY5NiwzICAGOTYsMiAgBjk2LDEgIAY5NSw2ICAGOTUsNSAgBjk1LDQgIAY5NSwzICAGOTUsMiAgBjk1LDEgIBQrAyVnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnFgECAmQCAQ9kFgJmDxAPFgYfAgUEbmFtZR8DBQdEZXB0X25vHwRnZBAVNgzlhajpg6ggKEFsbCki5bel56iL5a246ZmiICAgICAgICAgICAgICAgICAgICAgICHjgIDjgIDmqZ/morDlt6XnqIvlrbjns7vlrbjlo6vnj60w44CA44CA5YyW5a245bel56iL6IiH5p2Q5paZ56eR5a245a2457O75a245aOr54+tKuOAgOOAgOW3pealreW3peeoi+iIh+euoeeQhuWtuOezu+WtuOWjq+ePrSHjgIDjgIDmqZ/morDlt6XnqIvlrbjns7vnoqnlo6vnj60w44CA44CA5YyW5a245bel56iL6IiH5p2Q5paZ56eR5a245a2457O756Kp5aOr54+tKuOAgOOAgOW3pealreW3peeoi+iIh+euoeeQhuWtuOezu+eiqeWjq+ePrS3jgIDjgIDnlJ/niannp5HmioDoiIflt6XnqIvnoJTnqbbmiYDnoqnlo6vnj60k44CA44CA5YWI6YCy6IO95rqQ56Kp5aOr5a245L2N5a2456iLIeOAgOOAgOapn+aisOW3peeoi+WtuOezu+WNmuWjq+ePrTDjgIDjgIDljJblrbjlt6XnqIvoiIfmnZDmlpnnp5Hlrbjlrbjns7vljZrlo6vnj60q44CA44CA5bel5qWt5bel56iL6IiH566h55CG5a2457O75Y2a5aOr54+tIueuoeeQhuWtuOmZoiAgICAgICAgICAgICAgICAgICAgICAb44CA44CA566h55CG5a246Zmi5a245aOr54+tJ+OAgOOAgOeuoeeQhuWtuOmZoue2k+eHn+euoeeQhueiqeWjq+ePrSHjgIDjgIDnrqHnkIblrbjpmaLllYblrbjnoqnlo6vnj60q44CA44CA566h55CG5a246Zmi566h55CG56Kp5aOr5Zyo6IG35bCI54+tG+OAgOOAgOeuoeeQhuWtuOmZouWNmuWjq+ePrSTkurrmlofnpL7mnIPlrbjpmaIgICAgICAgICAgICAgICAgICAh44CA44CA5oeJ55So5aSW6Kqe5a2457O75a245aOr54+tIeOAgOOAgOS4reWci+iqnuaWh+WtuOezu+WtuOWjq+ePrSTjgIDjgIDol53ooZPoiIfoqK3oqIjlrbjns7vlrbjlo6vnj60q44CA44CA56S+5pyD5pqo5pS/562W56eR5a245a2457O75a245aOr54+tIeOAgOOAgOaHieeUqOWkluiqnuWtuOezu+eiqeWjq+ePrSHjgIDjgIDkuK3lnIvoqp7mloflrbjns7vnoqnlo6vnj60y44CA44CA6Jed6KGT6IiH6Kit6KiI5a2457O7KOiXneihk+euoeeQhueiqeWjq+ePrSkq44CA44CA56S+5pyD5pqo5pS/562W56eR5a245a2457O756Kp5aOr54+tIuizh+ioiuWtuOmZoiAgICAgICAgICAgICAgICAgICAgICAh44CA44CA6LOH6KiK5bel56iL5a2457O75a245aOr54+tIeOAgOOAgOizh+ioiueuoeeQhuWtuOezu+WtuOWjq+ePrSHjgIDjgIDos4foqIrlgrPmkq3lrbjns7vlrbjlo6vnj60h44CA44CA6LOH6KiK566h55CG5a2457O756Kp5aOr54+tIeOAgOOAgOizh+ioiuWCs+aSreWtuOezu+eiqeWjq+ePrSfjgIDjgIDos4foqIrnpL7mnIPlrbjnoqnlo6vlrbjkvY3lrbjnqIsh44CA44CA6LOH6KiK5bel56iL5a2457O756Kp5aOr54+tLeOAgOOAgOeUn+eJqeiIh+mGq+WtuOizh+ioiueiqeWjq+WtuOS9jeWtuOeoiyHjgIDjgIDos4foqIrnrqHnkIblrbjns7vljZrlo6vnj60h44CA44CA6LOH6KiK5bel56iL5a2457O75Y2a5aOr54+tEumbu+apn+mAmuioiuWtuOmZoiHjgIDjgIDpm7vmqZ/lt6XnqIvlrbjns7vlrbjlo6vnj60h44CA44CA6YCa6KiK5bel56iL5a2457O75a245aOr54+tIeOAgOOAgOWFiembu+W3peeoi+WtuOezu+WtuOWjq+ePrSHjgIDjgIDpm7vmqZ/lt6XnqIvlrbjns7vnoqnlo6vnj60h44CA44CA6YCa6KiK5bel56iL5a2457O756Kp5aOr54+tIeOAgOOAgOWFiembu+W3peeoi+WtuOezu+eiqeWjq+ePrSHjgIDjgIDpm7vmqZ/lt6XnqIvlrbjns7vljZrlo6vnj60h44CA44CA6YCa6KiK5bel56iL5a2457O75Y2a5aOr54+tIeOAgOOAgOWFiembu+W3peeoi+WtuOezu+WNmuWjq+ePrQ/pgJrorZjmlZnlrbjpg6gh6LuN6KiT5a6kICAgICAgICAgICAgICAgICAgICAgICAgIemrlOiCsuWupCAgICAgICAgICAgICAgICAgICAgICAgIBjlnIvpmpvoqp7oqIDmlofljJbkuK3lv4MV5ZyL6Zqb5YWp5bK45LqL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',
                '__EVENTVALIDATION': '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',
                'agree': '',
                'Q': 'RadioButton1',
                'DDL_YM': semester,
                'DDL_Degree': '0'
            }

            payload['DDL_Dept'] = DDL_Dept
            pre_request = urllib2.Request(
                        url=global_course_page_url, 
                        headers=Yzu.headers,
                        data=urlencode(payload)
                )
            pre_response = urllib2.urlopen(pre_request).read()
            __VIEWSTATE = re.findall(r'<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="(.*?)"', pre_response)[0]
            __EVENTVALIDATION = re.findall(r'<input type="hidden" name="__EVENTVALIDATION" id="__EVENTVALIDATION" value="(.*?)"', pre_response)[0]
            
            # second time post payload
            payload['__VIEWSTATE'] = __VIEWSTATE
            payload['__EVENTVALIDATION'] = __EVENTVALIDATION
            payload['__EVENTTARGET'] = ''
            payload['Button1'] = '確定'

            # retry function to avoid occurring socket error
            for i in range(0, 10):
                try:
                    request = urllib2.Request(
                            url=global_course_page_url,
                            headers=Yzu.headers,
                            data=urlencode(payload)
                        )
                    response = urllib2.urlopen(request).read()
                    beauty_response = BeautifulSoup(response)

                    table = beauty_response.find('table', id='Table1')
                    if '無課程資料！' in str(table):
                        print "無課程資料！"
                    else:
                        tr_list = table.find_all('tr')[1:]
                        for tr in tr_list:
                            td_list = tr.find_all('td')
                            if len(td_list) < 7:
                                continue

                            course_code = td_list[1].text.encode('utf8')
                            department = td_list[2].text.encode('utf8').split(' ')
                            course_info = td_list[3].contents[0]['href'].replace('./', 'https://portal.yzu.edu.tw/vc2/')
                            course_name = td_list[3].contents[0].string.encode('utf8')
                            course_type = td_list[4].text.encode('utf8')
                            course_time = '|'.join([item.replace('        ', '').encode('utf8').split(',')[0] for item in td_list[5].find('span').contents if len(item) != 0])
                            teacher = td_list[6].text.encode('utf8')

                            global_course_data = {
                                'course_code': course_code,
                                'course_name': course_name,
                                'course_department': department[0],
                                'course_grade': department[1],
                                'course_type': course_type,
                                'course_time': course_time,
                                'course_teacher': teacher
                            }

                            '''##########

                            do I/O here

                            ##########'''

                except Exception as e:
                    print 'Error: ' + str(e) + '   ' + DDL_YM + ' ' + DDL_Dept
                    time.sleep(5)
                    continue
                break





