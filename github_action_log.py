# 获取github action日志
import datetime
import os
import threading
import time

import requests
import json
from bs4 import BeautifulSoup
import urllib3
from configparser import  ConfigParser



urllib3.disable_warnings()
passwConf = ConfigParser();
passwConf.read('password.conf',encoding='utf-8')

github_url = "https://github.com"
username = passwConf.get('file1','name')
password = passwConf.get('file1','password')
post_url = 'https://github.com/session'
logPath = "D:/crawler/workSpace/logs/"
nowTime = datetime.datetime.now().date()
logExistTime = int(str(nowTime - datetime.timedelta(days=3 * 30)).replace('-', ''))

login_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.188',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Connection': 'close'
}

logined_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.188',
    'Connection': 'close'
}

search_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.188',
    'Connection': 'close'
}

s = requests.Session()  # 通过session保持登陆状态
s.keep_alive = False
def login():


    try:
        response_login = s.get(
            github_url + "/login",
            headers=login_headers,
            verify=False,
            timeout=20*60
        )
    except(Exception):
        time.sleep(61.1)
        response_login = s.get(
            github_url + "/login",
            headers=login_headers,
            verify=False,
            timeout=(10*60, 3)
        )


    soup = BeautifulSoup(response_login.text, "lxml")
    try:
        token = soup.find('input', attrs={'name': 'authenticity_token'}).get("value")
    except(Exception):
        login()
    post_data = {
        'commit': 'Sign in',
        'utf-8': '√',
        'authenticity_token': token,
        'login': username,
        'password': password
    }

    try:
        post = s.post(
            github_url + "/session",
            headers=logined_headers,
            data=post_data,
            verify=False,
            timeout=20*60
        )
    except(Exception):
        time.sleep(61.1)
        post = s.post(
            github_url + "/session",
            headers=logined_headers,
            data=post_data,
            verify=False,
            timeout=(10*60, 3)
        )
    time.sleep(1.3)
    print('登录')
    #保存登陆页面
    #fildName = 'post.html'
#
    #with open(fildName, 'w', encoding='utf-8') as fp:
    #    fp.write(post.text)
    #print(fildName, '保存成功')

    soup = BeautifulSoup(post.text, "html.parser")
    otp = soup.find(id='otp')
    form = soup.find('form')

    ##处理设备验证
    if otp != None:
        print('处理验证码')
        otp_value = input("输入验证码:")
        otp_data = {
            'authenticity_token': form.input['value'],
            'otp': otp_value
        }
        otp_page = s.post(
            github_url + "/sessions/verified-device",
            headers=logined_headers,
            data=otp_data,
            verify=False,
            timeout=(10*60, 3)
        )
        time.sleep(1.3)
        fildName = 'otp.html'

        with open(fildName, 'w', encoding='utf-8') as fp:
            fp.write(otp_page.text)
        print(fildName, '保存成功')
#检测日志文件夹是否存在,并定位到最新项目的中断日志位置
def isExistProject(name):

    #定位中断下载的位置
    disconFirstNames = os.listdir(logPath);
    disconFirstName = sorted(disconFirstNames, key=lambda file: os.path.getmtime(os.path.join(logPath, file)))[-1]
    disconSecondNames = os.listdir(logPath + '/' + disconFirstName);
    disconSecondName = sorted(disconSecondNames, key=lambda file: os.path.getmtime(os.path.join(logPath + '/' + disconFirstName, file)))[
        -1]
    logNames = os.listdir(logPath + '/' + disconFirstName + '/' + disconSecondName);

    commit = sorted(logNames, key=lambda file: os.path.getmtime(
        os.path.join(logPath + '/' + disconFirstName + '/' + disconSecondName, file)))[-1]
    commitId = commit.split('_')[1]


    #获取文件中已克隆的仓库列表，对仓库中已克隆的项目跳过
    firstNames = os.listdir(logPath)
    firstName = name.split("/")[0]
    secondName = name.split("/")[1]
    if firstName in firstNames :
        path = logPath+firstName
        secondNames = os.listdir(path)
        if secondName in secondNames :
            if firstName == disconFirstName and secondName == disconSecondName:
                #第四位返回值标志继续下载中断位置的日志信息

                return firstName+'/'+secondName,False,commitId,False
            return None,True,None,True

    return None,False,None,True


#登出并重新登陆
def logout():
    try:
        response_logout = requests.get(
            github_url + "/logout",
            headers=login_headers,
            verify=False,
            timeout=20*60
        )
    except(Exception):
        time.sleep(61.1)
        response_logout = requests.get(
            github_url + "/logout",
            headers=login_headers,
            verify=False,
            timeout=(10*60, 3)
        )

    soup = BeautifulSoup(response_logout.text, "lxml")
    try:
        token = soup.find('input', attrs={'name': 'authenticity_token'}).get("value")
    except(Exception):
        time.sleep(61.1)
        logout()
        return
    post_data = {
        'authenticity_token': token,
    }
    try:
        requests.post(
            github_url + "/logout",
            headers=logined_headers,
            data=post_data,
            verify=False,
            timeout=20*60
        )
    except(Exception):
        time.sleep(61.1)
        requests.post(
            github_url + "/logout",
            headers=logined_headers,
            data=post_data,
            verify=False,
            timeout=(10*60, 3)
        )



    print('登出')


if __name__ == '__main__':


    with open('data/results.json', 'r',encoding='ISO-8859-1') as f:
        jsonList = json.load(f)
    login()
    # 标记是否需要检测文件夹中已存在该项目日志，若为False则此后不再进行判断
    existFlag = True
    for infor in jsonList['items']:
        isContinue = True
        page = 1
        projectName = infor["name"]
        #定位当前项目名称
        print(projectName)


        if existFlag:
            disconName,flag,commitID,existFlag = isExistProject(projectName)
            #flag判断是否是已下载项目
            if flag:
                continue

        #标记是否需要从断开位置继续爬取日志
        disconLogFlag = False

        if disconName==projectName:
            disconLogFlag = True

        #若日志日期超时，则搜索下一项目
        while isContinue:
            try:
                response = s.get(
                    'https://github.com/' + projectName + '/actions?page=' + str(page),
                    headers=logined_headers,
                    verify=False,
                    stream=True,
                    timeout=20 * 60
                )
            except(Exception):
                time.sleep(61.1)
                logout()
                login()
                response = s.get(
                    'https://github.com/' + projectName + '/actions?page=' + str(page),
                    headers=logined_headers,
                    verify=False,
                    stream=True,
                    timeout=(10 * 60, 3)
                )

            time.sleep(1.1)
            soup = BeautifulSoup(response.text, "html.parser")
            names = soup.find_all(class_ = 'Link--primary css-truncate css-truncate-target')
            isLogin = soup.find(class_='HeaderMenu-link HeaderMenu-link--sign-in flex-shrink-0 no-underline d-block d-lg-inline-block border border-lg-0 rounded rounded-lg-0 p-2 p-lg-0')
            ##判断登录session是否超时
            if isLogin != None:
                s=requests.Session()
                s.keep_alive = False
                login()
                response = s.get(
                    'https://github.com/' + projectName + '/actions?page=' + str(page),
                    headers=logined_headers,
                    verify=False,
                    stream=True,
                    timeout=(10*60,5)
                )

            ##判断是否未使用github action
            isAction = soup.find(class_="col-lg-8 col-md-7 col-sm-12 float-left")
            if isAction!=None:
                if isAction.p.text == "Automate your workflow from idea to production":
                    break
            isBlank = soup.find(class_="blankslate blankslate-large blankslate-spacious")
             ##判断此页的ci是否为空
            if isBlank!= None :
                break
            hrefs = soup.find_all(class_="Link--primary css-truncate css-truncate-target")
            ##时间
            spans = soup.find_all(class_="d-inline d-md-block lh-condensed color-fg-muted my-1 pr-2 pr-md-0")

            account = 0
            for i in range(len(hrefs)):

                projectTime = int(spans[i].find_next("relative-time")["datetime"][:10].replace('-', ''))

                if projectTime > logExistTime:
                    try:
                        response_run = s.get(
                            github_url + hrefs[i]["href"],
                            headers=search_headers,
                            verify=False,
                            stream=True,
                            timeout=20 * 60
                        )
                    except(Exception):
                        time.sleep(61.1)
                        logout()
                        login()
                        response_run = s.get(
                            github_url + hrefs[i]["href"],
                            headers=search_headers,
                            verify=False,
                            stream=True,
                            timeout=(10 * 60, 3)
                        )

                    #重试获取页面
                    try:
                        soup = BeautifulSoup(response_run.text, "html.parser")
                    except:
                        print('重试获取page页面')
                        time.sleep(61.1)
                        logout()
                        login()
                        try:
                            response_run = s.get(
                                github_url + hrefs[i]["href"],
                                headers=search_headers,
                                verify=False,
                                stream=True,
                                timeout=20 * 60
                            )
                        except(Exception):
                            time.sleep(3.1)
                            logout()
                            login()
                            response_run = s.get(
                                github_url + hrefs[i]["href"],
                                headers=search_headers,
                                verify=False,
                                stream=True,
                                timeout=(10 * 60, 3)
                            )
                        soup = BeautifulSoup(response_run.text, "html.parser")
                    time.sleep(1.3)
                    ##完整左侧列表
                    span = soup.find(
                        class_="PageLayout-region PageLayout-pane PageLayout-region--dividerNarrow-none-after PageLayout-pane--sticky border-right-0")
                    try:
                        job_elements = span.find_all_next(class_="ActionListContent ActionListContent--visual16")
                    except(Exception):
                        continue

                    time.sleep(1.2)
                    for job_element in job_elements:

                        ##按class筛选的job有部分不是job的链接
                        if 'href' in str(job_element):
                            state = job_element.svg
                            try:
                                response_job = s.get(
                                    github_url + job_element["href"],
                                    headers=search_headers,
                                    verify=False,
                                    stream=True,
                                    timeout=20 * 60
                                )
                            except(Exception):
                                time.sleep(61.1)
                                logout()
                                login()
                                response_job = s.get(
                                    github_url + job_element["href"],
                                    headers=search_headers,
                                    verify=False,
                                    stream=True,
                                    timeout=(10 * 60, 3)
                                )


                            time.sleep(1.3)

                            # 重试获取页面
                            try:
                                soup = BeautifulSoup(response_job.text, "html.parser")
                            except:
                                print('重试获取log页面')
                                time.sleep(61.1)
                                logout()
                                login()
                                try:
                                    response_job = s.get(
                                        github_url + job_element["href"],
                                        headers=search_headers,
                                        verify=False,
                                        stream=True,
                                        timeout=20 * 60
                                    )
                                except(Exception):
                                    time.sleep(61.1)
                                    logout()
                                    login()
                                    response_job = s.get(
                                        github_url + job_element["href"],
                                        headers=search_headers,
                                        verify=False,
                                        stream=True,
                                        timeout=(10 * 60, 3)
                                    )
                                soup = BeautifulSoup(response_job.text, "html.parser")

                            log = soup.find(class_="pl-5 dropdown-item btn-link js-steps-dropdown-raw-logs")

                            if log != None:
                                #由项目名匹配确定，此项目日志未下载完全，根据commitID筛选到最新的日志，之后将标志设为False，此后正常下载
                                if disconLogFlag:
                                    print("跳过："+log["href"].split('/')[4][:7])
                                    #更改page快速跳转，下面page有+1操作
                                    page = 23

                                    if log["href"].split('/')[4][:7] == commitID:
                                        disconLogFlag = False
                                    break
                                try:
                                    response_log = s.get(
                                        github_url + log["href"],
                                        headers=search_headers,
                                        verify=False,
                                        stream=True,
                                        timeout=20 * 60
                                    )
                                except(Exception):
                                    time.sleep(61.1)
                                    logout()
                                    login()
                                    response_log = s.get(
                                        github_url + log["href"],
                                        headers=search_headers,
                                        verify=False,
                                        stream=True,
                                        timeout=(10 * 60, 3)
                                    )

                                # 重试获取页面
                                try:
                                    soup = BeautifulSoup(response_log.text, "html.parser")
                                except:
                                    print('重试获取job页面')
                                    time.sleep(61.1)
                                    logout()
                                    login()
                                    try:
                                        response_log = s.get(
                                            github_url + log["href"],
                                            headers=search_headers,
                                            verify=False,
                                            stream=True,
                                            timeout=20 * 60
                                        )
                                    except(Exception):
                                        time.sleep(61.1)
                                        logout()
                                        login()
                                        response_log = s.get(
                                            github_url + log["href"],
                                            headers=search_headers,
                                            verify=False,
                                            stream=True,
                                            timeout=(10 * 60, 3)
                                        )
                                    soup = BeautifulSoup(response_log.text, "html.parser")
                                time.sleep(1.3)
                                current_time = datetime.datetime.now()
                                time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
                                ##去除文件夹中不允许出现的符号
                                name = names[i].text.replace(' ','_').replace('\\','_').replace('/','_').replace(':', '_').replace('*','_').replace('?','_').replace('<','_').replace('>','_').replace('|','_').replace('"','_')[:11]
                                fileName = f'../logs/' + projectName + '/' +state["aria-label"].replace(' ','-')+'_'+log["href"].split('/')[4][:7] +'_'+ time_str.replace(' ','_').replace(':','_')[11:]+'_'+name+ '.html'
                                os.makedirs(os.path.dirname(fileName), exist_ok=True)
                                with open(fileName,'w', encoding='utf-8') as fp:
                                    fp.write('commitId: ' + log["href"].split('/')[4] + '\n')
                                    fp.write(response_log.text+"\n"+"exit")

                                print(fileName, '保存成功')
                else:
                    isContinue = False
                    break

            #每运行完一页重新登陆
            logout()
            time.sleep(3.6)
            login()
            page += 1

# page_text = r3.text
# fildName = 'r3.html'
# with open(fildName, 'w', encoding='utf-8') as fp:
#    fp.write(page_text)
# print(fildName, '保存成功')
