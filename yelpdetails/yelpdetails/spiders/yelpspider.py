# -*- coding: utf-8 -*-
import scrapy
import time
from ..items import YelpdetailsItem
# from scrapy.selector import Selector
from scrapy.selector import Selector
from scrapy_selenium import SeleniumRequest
import os
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
import re

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys

class YelpspiderSpider(scrapy.Spider):
    name = 'yelpspider'

    website = 'Yelp'
    web_link = ""
    webname = ""
    phone = ""
    direction = ""


    def start_requests(self):
        index = 0
        yield SeleniumRequest(
            url="https://www.yelp.com/",
            wait_time=1000,
            screenshot=True,
            callback=self.parse,
            meta={'index': index},
            dont_filter=True
        )

    def parse(self, response):

        driver=response.meta['driver']
        driver.find_element_by_xpath("//input[@id='find_desc']").clear()
        search_input1 = driver.find_element_by_xpath("//input[@id='find_desc']")
        # os.chdir("..")

        # a=os.path.join(os.path.abspath(os.curdir), "/web", "/templates", "/find.txt")
        print(os.path.abspath(os.curdir))
        firstinput = os.path.abspath(os.curdir)+"\option.txt"
        secondinput = os.path.abspath(os.curdir) + "\location.txt"
        # thirdinput = os.path.abspath(os.curdir) + "\catg.txt"
        thirdinput = os.path.abspath(os.curdir) + "\pages.txt"



        f = open(firstinput, "r")
        find=f.read().splitlines()


        f = open(secondinput, "r")
        near=f.read().splitlines()

        # f = open(thirdinput, "r")
        # catg = f.read().splitlines()

        f = open(thirdinput, "r")
        numpages = f.read().splitlines()

        numpages = int(numpages[0])

        length = len(find)
        index = response.meta['index']

        print()
        print()
        print()
        print(find,near)
        print()
        print()
        print()

        if(index<length):

            search_input1.send_keys(find[index])
            # find.pop(0)
            driver.find_element_by_xpath("//input[@id='dropperText_Mast']").clear()
            search_input2 = driver.find_element_by_xpath("//input[@id='dropperText_Mast']")

            search_input2.send_keys(near[index])
            # near.pop(0)
            ind = index
            index += 1

            search_button=driver.find_element_by_xpath("//button[@id='header-search-submit']")
            search_button.click()

            # time.sleep(4)
            print(driver.current_url)
            page=[]
            currpage=0
            duplicate_sponsored=[]
            yield SeleniumRequest(
                url=driver.current_url,
                wait_time=1000,
                screenshot=True,
                callback=self.numberofpages,
                meta = {'page': page,'index': index,'find': find[ind],'near': near[ind],'numpages': numpages,'currpage': currpage,'duplicate_sponsored':duplicate_sponsored},
                dont_filter=True
            )


    def numberofpages(self,response):
        driver = response.meta['driver']
        html = driver.page_source
        response_obj = Selector(text=html)
        page=response.meta['page']
        # catg=response.meta['catg']
        numpages=response.meta['numpages']
        currpage = response.meta['currpage']
        duplicate_sponsored = response.meta['duplicate_sponsored']

        print()
        print('on the next page')
        print('current url',driver.current_url)
        print()


        details = response_obj.xpath('//*[@id="wrap"]/div[3]/div[2]/div/div[1]/div[1]/div[2]/div[2]/ul/li/div')
        flag = 0
        for i,detail in enumerate(details):

            check=detail.xpath('.//h3/text()').get()
            if(check==None):
                check='NA'
            print(i,check)
            if('Sponsored Result' in check):
                flag=1
            elif('All Result' in check):
                flag=0
            else:
                if(flag==1):
                    sponsored_web_link = detail.xpath(".//div/div/div[2]/div[1]/div/div[1]/div/div[1]/div/div/h4/span/a/@href").get()
                    sponsored_web_name = detail.xpath(".//div/div/div[2]/div[1]/div/div[1]/div/div[1]/div/div/h4/span/a/text()").get()
                    if(sponsored_web_name not in duplicate_sponsored):
                        duplicate_sponsored.append(sponsored_web_name)
                        page.append(f"https://www.yelp.com{sponsored_web_link}")




        # time.sleep(100)


        index = response.meta['index']
        find = response.meta['find']
        near = response.meta['near']

        next_page = response_obj.xpath('//a[@class ="lemon--a__373c0__IEZFH link__373c0__1G70M next-link navigation-button__373c0__23BAT link-color--inherit__373c0__3dzpk link-size--inherit__373c0__1VFlE"]/@href').get()

        print(next_page)
        if (next_page and currpage<numpages):
            currpage += 1
            yield SeleniumRequest(
                url=f"https://www.yelp.com{next_page}",
                wait_time=1000,
                screenshot=True,
                callback=self.numberofpages,
                meta={'page': page,'index': index,'find': find,'near': near,'numpages': numpages,'currpage': currpage,'duplicate_sponsored':duplicate_sponsored},
                dont_filter=True
            )
        else:
            # page.pop(0)
            print()
            print('All pages')
            print(page)
            print()
            print()
            if(len(page)!=0):
                a=page[0]
                page.pop(0)
            yield SeleniumRequest(
                url=a,
                wait_time=1000,
                screenshot=True,
                callback=self.scrapepages,
                meta={'page': page,'index': index,'find': find,'near': near},
                dont_filter=True
            )


    def scrapepages(self,response):
        Yelpdetails_Item = YelpdetailsItem()
        driver = response.meta['driver']
        html = driver.page_source
        response_obj = Selector(text=html)
        page = response.meta['page']
        # category = response.meta['category']
        index = response.meta['index']
        find = response.meta['find']
        near = response.meta['near']
        # catg = response.meta['catg']
        # duplicateurl = response.meta['duplicateurl']

        if(response.url=='https://www.google.com/'):
            print()
            print()
            print(self.webname)
            # print(category)
            print()
            print()

            finalemail = response.meta['finalemail']

            Yelpdetails_Item['Name'] = self.name
            Yelpdetails_Item['website_link'] = self.web_link
            Yelpdetails_Item['website_name'] = self.webname
            Yelpdetails_Item['phone'] = self.phone
            Yelpdetails_Item['Direction'] = self.direction
            Yelpdetails_Item['category'] = 'Sponsored Result'
            Yelpdetails_Item['find'] = find
            Yelpdetails_Item['near'] = near
            Yelpdetails_Item['website'] = self.website

            Yelpdetails_Item['email'] = "NA"

            print()
            print()
            print(len(finalemail))
            print(type(finalemail))
            print()
            print()
            if(len(finalemail)==0):
                yield Yelpdetails_Item
            else:
                if(len(finalemail) < 5):
                    length = len(finalemail)
                else:
                    length = 5
                for i in range(0, length):
                    Yelpdetails_Item['email'] = finalemail[i]
                    yield Yelpdetails_Item




            if len(page) != 0:

                a=page[0]
                page.pop(0)
                yield SeleniumRequest(
                    url=a,
                    wait_time=1000,
                    screenshot=True,
                    callback=self.scrapepages,
                    meta={'page': page,'index': index, 'find': find, 'near': near},
                    dont_filter=True
                )

            else:
                yield SeleniumRequest(
                    url="https://www.yelp.com/",
                    wait_time=1000,
                    screenshot=True,
                    callback=self.parse,
                    meta={'index': index},
                    dont_filter=True
                )

        else:

            try:
                name = response_obj.xpath("//h1/text()").get()
            except:
                name = None

            try:
                webname = response_obj.xpath("//*[@id='wrap']/div[4]/div/div[4 or 3]/div/div/div[2]/div[2]/div/div/section[1 or 2]/div/div[1]/div/div[2]/p[2]/a/text()").get()
            except:
                webname = None

            if(webname != None):
                try:
                    web_link  = response_obj.xpath("//*[@id='wrap']/div[4]/div/div[4 or 3]/div/div/div[2]/div[2]/div/div/section[1 or 2]/div/div[1]/div/div[2]/p[2]/a/@href").get()
                except:
                    web_link = None

                try:
                    phone = response_obj.xpath("//*[@id='wrap']/div[4]/div/div[4 or 3]/div/div/div[2]/div[2]/div/div/section[1 or 2]/div/div[2]/div/div[2]/p[2]/text()").get()
                except:
                    phone = None
                try:
                    direction = response_obj.xpath("//*[@id='wrap']/div[4]/div/div[3 or 4]/div/div/div[2]/div[2]/div/div/section[1 or 2]/div/div[3]/div/div[2]/p/a/@href").get()
                except:
                    direction = None
            else:
                web_link = None
                try:
                    phone = response_obj.xpath("//*[@id='wrap']/div[4]/div/div[4 or 3]/div/div/div[2]/div[2]/div/div/section[1 or 2]/div/div[2 or 1]/div/div[2]/p[2]/text()").get()
                except:
                    phone = None
                try:
                    direction = response_obj.xpath("//*[@id='wrap']/div[4]/div/div[3 or 4]/div/div/div[2]/div[2]/div/div/section[1 or 2]/div/div[3 or 2]/div/div[2]/p/a/@href").get()
                except:
                    direction = None



            # try:
            #     category = category
            # except:
            #     category = 'All Results'
            print()
            print(name)
            print(direction)
            print(web_link)
            print(webname)
            print(phone)
            # print(category)
            print()
            if(name == None):
                name="NA"

            if (web_link == None):
                web_link="NA"
            else:
                web_link=f"https://www.yelp.com{web_link}"

            if (direction == None):
                direction = "NA"
            else:
                direction=f"https://www.yelp.com{direction}"

            if (webname == None):
                webname="NA"

            if (phone == None):
                phone="NA"

            self.name=name
            self.web_link = web_link
            self.webname = webname
            self.phone = phone
            self.direction = direction

            if(web_link != "NA"):
                yield SeleniumRequest(
                    url=web_link,
                    wait_time=1000,
                    screenshot=True,
                    callback=self.emailtrack,
                    dont_filter=True,
                    meta={'page': page,'index': index, 'find': find, 'near': near}
                )
            else:
                finalemail=[]
                yield SeleniumRequest(
                    url='https://www.google.com/',
                    wait_time=1000,
                    screenshot=True,
                    callback=self.scrapepages,
                    dont_filter=True,
                    meta={'page': page,'index': index, 'find': find, 'near': near,'finalemail': finalemail}
                )





    def emailtrack(self,response):
        driver = response.meta['driver']
        html = driver.page_source
        response_obj = Selector(text=html)
        page = response.meta['page']
        # category = response.meta['category']
        index = response.meta['index']
        find = response.meta['find']
        near = response.meta['near']
        # catg = response.meta['catg']
        # duplicateurl = response.meta['duplicateurl']
        links = LxmlLinkExtractor(allow=()).extract_links(response)
        Finallinks = [str(link.url) for link in links]
        links = []
        for link in Finallinks:
            if ('Contact' in link or 'contact' in link or 'About' in link or 'about' in link or 'home' in link or 'Home' in link or 'HOME' in link or 'CONTACT' in link or 'ABOUT' in link):
                links.append(link)

        links.append(str(response.url))

        if(len(links)>0):
            l=links[0]
            links.pop(0)
            uniqueemail = set()
            yield SeleniumRequest(
                url=l,
                wait_time=1000,
                screenshot=True,
                callback=self.finalemail,
                dont_filter=True,
                meta={'links': links,'page': page, 'index': index, 'find': find, 'near': near,'uniqueemail': uniqueemail}
            )
        else:
            yield SeleniumRequest(
                url='https://www.google.com/',
                wait_time=1000,
                screenshot=True,
                callback=self.scrapepages,
                dont_filter=True,
                meta={'page': page,'index': index, 'find': find, 'near': near,'finalemail': finalemail}
            )


    def finalemail(self, response):
        links = response.meta['links']
        driver = response.meta['driver']
        html = driver.page_source
        response_obj = Selector(text=html)
        page = response.meta['page']
        # category = response.meta['category']
        index = response.meta['index']
        find = response.meta['find']
        near = response.meta['near']
        # catg = response.meta['catg']
        # duplicateurl = response.meta['duplicateurl']
        uniqueemail = response.meta['uniqueemail']

        flag = 0
        bad_words = ['facebook', 'instagram', 'youtube', 'twitter', 'wiki']
        for word in bad_words:
            if word in str(response.url):
                # return
                flag = 1
        if (flag != 1):
            html_text = str(response.text)
            mail_list = re.findall('\w+@\w+\.{1}\w+', html_text)
            #
            mail_list = set(mail_list)
            if (len(mail_list) != 0):
                for i in mail_list:
                    mail_list = i
                    if (mail_list not in uniqueemail):
                        uniqueemail.add(mail_list)
                        print()
                        print()
                        print()
                        print(uniqueemail)
                        print()
                        print()
                        print()
            else:
                pass

        if (len(links) > 0 and len(uniqueemail) < 5):
            print()
            print()
            print()
            print('hi', len(links))
            print()
            print()
            print()
            l = links[0]
            links.pop(0)
            yield SeleniumRequest(
                url=l,
                wait_time=1000,
                screenshot=True,
                callback=self.finalemail,
                dont_filter=True,
                meta={'links': links,'page': page, 'index': index, 'find': find, 'near': near, 'uniqueemail': uniqueemail}
            )
        else:
            print()
            print()
            print()
            print('hello')
            print()
            print()
            print()
            emails = list(uniqueemail)
            finalemail = []
            discard = ['robert@broofa.com']
            for email in emails:
                if ('.in' in email or '.com' in email or 'info' in email):
                    for dis in discard:
                        if (dis not in email):
                            finalemail.append(email)
            print()
            print()
            print()
            print('final', finalemail)
            print()
            print()
            print()
            yield SeleniumRequest(
                url='https://www.google.com/',
                wait_time=1000,
                screenshot=True,
                callback=self.scrapepages,
                dont_filter=True,
                meta={'page': page, 'index': index, 'find': find, 'near': near,'finalemail': finalemail}
            )