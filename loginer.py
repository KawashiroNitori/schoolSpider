import sys
import io
import pyocr
import pyocr.builders
from PIL import Image
from eventlet.green.urllib import parse, request
from eventlet.green.http import cookiejar
from bs4 import BeautifulSoup

BASE_URL = 'http://jwc.sut.edu.cn/'
DEFAULT_USER_ID = 'username'
DEFAULT_PASSWORD = 'pass'

def getCaptcha(captchaImage):
    tool = pyocr.get_available_tools()[0]
    return tool.image_to_string(Image.open(io.BytesIO(captchaImage)), lang = 'eng', builder = pyocr.tesseract.DigitBuilder())

def parseSubmitData(userID, password, captcha):
    return parse.urlencode([('WebUserNO', userID), ('Password', password), ('Agnomen', captcha)]).encode('utf-8')

def Login(userID = DEFAULT_USER_ID, password = DEFAULT_PASSWORD):
    LOGIN_METHOD = 'ACTIONLOGON.APPPROCESS?mode=4'
    CAPTCHA_METHOD = 'ACTIONVALIDATERANDOMPICTURE.APPPROCESS'
    while True:
        try:
            with request.urlopen(BASE_URL + CAPTCHA_METHOD) as response:
                captcha = getCaptcha(response.read())
                cookie = dict(response.info())['Set-Cookie']
                print('Get Cookie: %s' % cookie)
            print('Get captcha: %s' % captcha)
            reqData = request.Request(BASE_URL + LOGIN_METHOD, data = parseSubmitData(userID, password, captcha))
            reqData.add_header('Cookie', cookie)
            response = request.urlopen(reqData).read().decode('GBK')
            if '正确的附加码' in response:
                print('Captcha incorrect, Retrying...')
                continue
            elif '错误的用户名' in response:
                print('Username or password incorrect, Exit.')
                return
            elif '欢迎您登录' in response:
                page = BeautifulSoup(response, 'html.parser')
                username = str(page.find_all('td')[2].string)
                print('Username: %s' % username)
                print('Login successful.')
                return cookie
        except Exception as e:
            print('Error: %s' % e)
