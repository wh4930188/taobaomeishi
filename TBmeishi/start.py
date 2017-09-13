#conding:utf-8
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq
import pymongo
from config import *
browser=webdriver.Chrome()
wait=WebDriverWait(browser,10)
client=pymongo.MongoClient(MONGO_URL)   #创建mongo客户端对象
db=client[MONGO_DB]           #客户端建表

def search():
    try:
        browser.get('http://www.taobao.com')  #浏览器去get到预定的网址
        input=wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR,"#q"))  #等待浏览器出现某个选择框选项,赋值
        )
        submit=wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR,"#J_TSearchForm > div.search-button > button"))
        )  #等待出现这个提交框框,赋值
        input.send_keys('美食')   #在输入框内,输入内容,此处规定了输入的内容
        submit.click()  #触发点击事件
        total=wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"#mainsrp-pager > div > div > div > div.total")))
        #页码,赋值
        get_products() #获取产品
        return total.text #返回页码总大小
    except TimeoutError:return search()

def next_page(page_number):
    try:
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > div.form > input"))
        )  #页码输入框
        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit"))
        )  #页码输入框旁边那个点击按钮
        input.clear()  #清空输入框内容
        input.send_keys(page_number)  #输入页码
        submit.click()  #点击确定
        wait.until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR,"#mainsrp-pager > div > div > div > ul > li.item.active > span"),str(page_number)))
        get_products()  #等所在页面为  page_number页面
    except TimeoutError:return next_page(page_number)
def get_products():  #获取信息的函数
    wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#mainsrp-itemlist .items .item")))   #刷出了内容
    html=browser.page_source #可以拿到整个网页的源代码
    doc=pq(html)    #创建query对象
    items=doc("#mainsrp-itemlist .items .item").items() #所有产品
    for item in items:   #查找其中的各类元素
        products={
            'image':item.find('.pic .img').attr('src'),
            'price':item.find('.price').text(),
            'deal':item.find('.deal-cnt').text(),
            'title':item.find('.title').text(),
            'shop':item.find('.shop').text(),
            'location':item.find('.location').text()
        }
        print(products)   #将找到的元素打印一下
        save_to_mongo(products)   #调用保存的函数,保存一下
def save_to_mongo(result):
    try:
        if db[MONGO_TABLE].insert(result):
            print('存储到MONGODB成功',result)
    except Exception:print('存储到MONGODB失败',result)
def main():
    try:
        total=search()   #第一次?先去搜索的第一页,去爬取内容,并且返回页码总数   本来拿到的是   共 100 页，  这个东西
        total=int(re.compile('(\d+)').search(total).group(1))  #返回的是数字
        for i in range(2,total+1):  #从2开始往下  都执行下数字页面的提取操作
            next_page(i)
    except Exception:print('出错了')
    finally:
        browser.close()  #将这个浏览器关闭
if __name__ == '__main__':
    main()
