#! /usr/bin/python
# -*- coding: utf8 -*-

import re, sys, json, time, random, urllib2, cookielib
from urllib import urlencode
from bs4 import BeautifulSoup

import models

class Yzu:
    '''
    A class contains functions about accessing YZU portal.
    By Jay Chung
    '''

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
        # do with cookie
        '''self.cookie_support = urllib2.HTTPCookieProcessor(cookielib.CookieJar())
        self.opener = urllib2.build_opener(self.cookie_support, urllib2.HTTPHandler)'''
        self.cookiejar = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar))

    def cookieExists(self):
        _cookie = [cookie.value for cookie in self.cookiejar if cookie.name == 'ASP.NET_SessionId']
        if _cookie != []:
            return True
        else:
            return False

    def login(self):
        if not self.cookieExists():
            url = 'https://portal.yzu.edu.tw/logincheck_new.aspx'
            form_data = {'uid': self.username, 'pwd': self.password}

            # get the cookie
            self.opener.open(url, urlencode(form_data))
            urllib2.install_opener(self.opener)

            # check if user login successfully
            portal_page = urllib2.urlopen('https://portal.yzu.edu.tw/Index_Survey.aspx').read()
            if portal_page.find('登入逾時') == -1:
                return True
            else:
                return False
        else:
            return True

    def get_course_credits(self):
        credit_info = dict()

        # Portal slide menu access
        portal_left_menu_url = 'https://portal.yzu.edu.tw/Left_index.aspx'
        grade_page_url = 'https://portal.yzu.edu.tw/VC2/Student/console/My_Stdregi_Score.aspx'
        portal_left_menu = urllib2.urlopen(portal_left_menu_url).read()
        student_profile_url = 'https://portal.yzu.edu.tw/' + re.findall(r"<a class=\"left_menu\" href='(.*?)' target='_top'>", portal_left_menu)[0].replace('..', '')
        urllib2.urlopen(student_profile_url)

        # get the semester_list
        grade_page = urllib2.urlopen(grade_page_url).read()
        semester_list = re.findall(r'<option.*?value="(.*?)">', grade_page)

        __VIEWSTATE = re.findall(r'<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="(.*?)" />', grade_page)[0]
        __EVENTVALIDATION = re.findall(r'<input type="hidden" name="__EVENTVALIDATION" id="__EVENTVALIDATION" value="(.*?)" />', grade_page)[0]

        form_data = {
            '__EVENTTARGET': 'DropDownList2',
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            '__VIEWSTATE': __VIEWSTATE,
            '__EVENTVALIDATION': __EVENTVALIDATION,
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

        # Portal 側欄取得認證
        portal_left_menu_url = 'https://portal.yzu.edu.tw/Left_index.aspx'
        portal_left_menu = urllib2.urlopen(portal_left_menu_url).read()
        student_profile_url = 'https://portal.yzu.edu.tw/' + re.findall(r"<a class=\"left_menu\" href='(.*?)' target='_top'>", portal_left_menu)[0].replace('..', '')
        urllib2.urlopen(student_profile_url)

        # 進入經典五十頁面
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

        # 依照學期分類
        return classic_info

    def get_serving_point(self):
        # Portal 側欄取得認證
        portal_left_menu_url = 'https://portal.yzu.edu.tw/Left_index.aspx'
        portal_left_menu = urllib2.urlopen(portal_left_menu_url).read()
        student_profile_url = 'https://portal.yzu.edu.tw/' + re.findall(r"<a class=\"left_menu\" href='(.*?)' target='_top'>", portal_left_menu)[0].replace('..', '')
        urllib2.urlopen(student_profile_url)

        # 進入到服務學習的紀錄區
        student_profile_left_menu_url = 'https://portal.yzu.edu.tw/VC2/Student/classLeft_S.aspx'
        student_profile_left_menu = urllib2.urlopen(student_profile_left_menu_url).read()
        serve_learn_page_url = 'https://portal.yzu.edu.tw/' + re.findall(r'<a class="left_menu" href="(.*?)" target="main"   title="服務學習檔案">', student_profile_left_menu)[0].replace('..', '')
        serve_learn_page = urllib2.urlopen(serve_learn_page_url)
        serve_learn_record_page_url = 'https://portal.yzu.edu.tw/Ser_learn/stdserv_std/ser_std_recdata.asp'
        serve_learn_record_page = urllib2.urlopen(serve_learn_record_page_url).read()

        hour_data = re.findall(r'<font color="#669900">(.*?)</font>', serve_learn_record_page)[1]
        #print hour_data.decode('utf8')
        point = [x.replace('&nbsp;', '') for x in re.findall(r'&nbsp;[\d\s.]*&nbsp;', hour_data)]
        if point[0] == '':
            point[0] = '0'
        if point[1] == '':
            point[1] = '0'
        return point

    def get_course_schedule(self):
        schedule_dict = dict()
        schedule_dict['owner'] = self.username

        # Portal 側欄取得認證
        portal_left_menu_url = 'https://portal.yzu.edu.tw/Left_index.aspx'
        portal_left_menu = urllib2.urlopen(portal_left_menu_url).read()
        student_profile_url = 'https://portal.yzu.edu.tw/' + re.findall(r"<a class=\"left_menu\" href='(.*?)' target='_top'>", portal_left_menu)[0].replace('..', '')
        urllib2.urlopen(student_profile_url)
        urllib2.urlopen('https://portal.yzu.edu.tw/VC2/Student/console/Message_ALert_S.aspx')

        schedule_url = 'https://portal.yzu.edu.tw/VC2/Student/console/My_Schedule_XP.aspx'
        schedule_page = urllib2.urlopen(schedule_url).read()

        __VIEWSTATE = urlencode({'__VIEWSTATE': re.findall(r'<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="(.*?)"', schedule_page)[0]})
        __EVENTVALIDATION = urlencode({'__EVENTVALIDATION': re.findall(r'<input type="hidden" name="__EVENTVALIDATION" id="__EVENTVALIDATION" value="(.*?)"', schedule_page)[0]})

        payload = '__EVENTTARGET=DropDownList2&__EVENTARGUMENT=&__LASTFOCUS=&' + __VIEWSTATE + '&' + __EVENTVALIDATION + '&agree=&x=&DropDownList2=102%2F2'
        request = urllib2.Request(
                url=schedule_url,
                headers=Yzu.headers,
                data=payload
            )
        response = urllib2.urlopen(request).read()
        beauty_response = BeautifulSoup(response)

        table = beauty_response.find('table', id='Table1')
        tr_list = table.find_all('tr')[1:]

        t1 = 1
        t2 = 1
        key = ''
        for tr in tr_list:
            td_list = tr.find_all('td')[1:]
            for td in td_list:
                course_name = ''
                if td.text != '':
                    course_name = td.text.encode('utf8').split(')')[1].split('*')[0]

                if t2 < 10:
                    key = 't' + str(t1) + '0' + str(t2)
                else:
                    key = 't' + str(t1) + str(t2)

                schedule_dict[key] = course_name.strip()
                t1 = t1 + 1

            t1 = 1
            t2 = t2 + 1

        #do I/O here


    def get_all_course(self):
        # access the global course page
        global_course_page_url = 'https://portal.yzu.edu.tw/vc2/global_cos.aspx'
        global_course_page = urllib2.urlopen(global_course_page_url).read()
        beauty_global_course_page = BeautifulSoup(global_course_page)

        # parse the department list
        DDL_Dept_select = beauty_global_course_page.find('select', id='DDL_Dept')
        all_DDL_Dept = re.findall(r'<option.*?value="(.*?)">', str(DDL_Dept_select))

        __VIEWSTATE = re.findall(r'<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="(.*?)" />', global_course_page)[0]
        __EVENTVALIDATION = re.findall(r'<input type="hidden" name="__EVENTVALIDATION" id="__EVENTVALIDATION" value="(.*?)" />', global_course_page)[0]


        for DDL_Dept in all_DDL_Dept:
            # first time post payload
            payload = {
                '__EVENTTARGET': 'DDL_Dept',
                '__EVENTARGUMENT': '',
                '__LASTFOCUS': '',
                '__VIEWSTATE': __VIEWSTATE,
                '__EVENTVALIDATION': __EVENTVALIDATION,
                'agree': '',
                'Q': 'RadioButton1',
                'DDL_YM': '102,2  ',
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

                            #do I/O here

                except Exception as e:
                    time.sleep(5)
                    continue
                break

        return "hello"