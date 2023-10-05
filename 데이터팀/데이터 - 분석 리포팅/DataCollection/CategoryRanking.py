############################################ Package Importing
import pandas as pd
import numpy as np

from bs4 import BeautifulSoup as bs
from urllib.request import urlopen, Request, urlretrieve
from urllib.request import Request
from urllib.parse import quote_plus
from datetime import datetime

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import subprocess
import time
from tqdm import tqdm
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
## from PIL import Image


option = Options()
option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

# Chrome WebDriver 초기화
chrome_driver = ChromeDriverManager().install()
service = Service(chrome_driver)
driver = webdriver.Chrome(service = service)

url = "https://www.musinsa.com/ranking/best?period=now&age=ALL&mainCategory=002&subCategory=&leafCategory=&price=&golf=false&kids=false&newProduct=false&exclusive=false&discount=false&soldOut=false&page=1&viewType=small&includeWomen=false&priceMin=&priceMax=#pol3039295"
driver.get(url)
driver.implicitly_wait(10)



############################# 카테고리 ID 식별
def identify_Category_id():
    main_cat = ['전체', 
            '상의', '아우터', '바지', '원피스', '스커트', '스니커즈', '신발', '가방', '여성 가방','스포츠용품', 
            '모자', '양말레그웨어', '속옷', '선글라스안경테', '액세서리', '시계', '주얼리', '뷰티', '디지털테크', '리빙',
            '컬쳐', '반려동물']

    main_cat_id = ['', 
                '001', '002', '003', '020', '022', '018', '005', '004', '054', '017',
                '007', '008', '026', '009', '011', '006', '025', '015', '012', '058',
                '014', '021']

    main_cat_dict = {}

    for i in range(len(main_cat)):
        main_cat_dict[main_cat[i]] = main_cat_id[i]
    
    return main_cat_dict


########### 상품정보 크롤링을 위한 selector 지정
def setting_selector():
    
    selector1 = '#product_order_info > div.explan_product.product_info_section > ul > li:nth-child(1) > p.product_article_contents > strong'
    selector2 = '#product_order_info > div.explan_product.product_info_section > ul > li:nth-child(1) > p.product_article_contents > strong > a'
    selector3 = '#page_product_detail > div.right_area.page_detail_product > div.right_contents.section_product_summary > span > em'
    selector4 = '#goods_price > del'
    selector4_2 = '#goods_price'
    selector5 = '#sPrice > ul > li.pertinent > span.txt_price_member'
    
    selectors = [selector1, selector2, selector3, selector4, selector4_2, selector5]

    return selectors

########### 카테고리별 상품 랭킹 리스트 
def extraction_ranking(main_cat_dict, selectors, sex):
    for key, value in main_cat_dict.items():
        
        base_url_01 = 'https://www.musinsa.com/ranking/best?period=now&age=ALL&mainCategory='
        base_url_02 = '&subCategory=&leafCategory=&price=&golf=false&kids=false&newProduct=False&exclusive=false&discount=false&soldOut=false&page='
        base_url_03 = '&viewType=small&includeWomen=false&priceMin=&priceMax='
        page_num = 1
        
        items_url = []
        while page_num <= 2:
            search_url = base_url_01 + value + base_url_02 + str(page_num) + base_url_03

            html = Request(search_url, headers={'User-Agent' : 'Mozilla/5.0'})
            page = urlopen(html)
            # print(page)

            selector = '#goodsRankList > li div.li_inner > div.article_info > p.list_info > a'
            soup = bs(page, 'html.parser')
            selected = soup.select(selector)

            for item in selected:
                items_url.append(item['href'])
            
            page_num += 1
            
        items_url = items_url[:100]
        print('URL 완료')
        
        category = []
        ranking = []
        product_id = []
        brand_name = []
        product_title = []
        sales_price = []
        non_member_price = []
        # new_member_price = []
        product_like = []

        rank = 1
        for url in items_url:
            html = Request(url, headers={'User-Agent' : 'Mozilla/5.0'})
            page = urlopen(html)
            soup = bs(page, 'html.parser')  
            
            check = {}
            
            selected01 = soup.select(selectors[0])
            
            selected02 = soup.select(selectors[1])
            
            selected03 = soup.select(selectors[2])
            
            selected04 = soup.select(selectors[3])
            selected04_2 = soup.select(selectors[4])
            
            selected05 = soup.select(selectors[5])
            
            
            driver.get(url)
            selected07 = driver.find_elements(By.XPATH, '//*[@id="product-top-like"]/p[2]/span')[0].text
            product_like.append(selected07.replace(',' ,''))
            
            if not selected04:
                selected04 = selected04_2
            if not selected05:
                selected05 = selected04
  
                
            #for pid, name, title, price, like in zip(selected01, selected02, selected03, selected04, selected05):
            #for pid, name, title, price1, price2, price3 in zip(selected01, selected02, selected03, selected04, selected05, selected06):
            for pid, name, title, price1, price2 in zip(selected01, selected02, selected03, selected04, selected05):
                category.append(key)
                ranking.append(rank)
                rank += 1
                
                product_id.append(pid.get_text().split(' / ')[1])
                brand_name.append(name.get_text())
                product_title.append(title.get_text().split(' / ')[0])
                sales_price.append(price1.text.replace(',', '').split('원')[0])
                non_member_price.append(price2.text.replace(',', '').split('원')[0])
                #new_member_price.append(price3.text.replace(',', '').split('원')[0])
        
        print(len(category), len(ranking), len(product_id), len(brand_name), len(product_title), len(sales_price), 
              len(non_member_price), len(product_like), len(items_url)) 
        df = pd.DataFrame({'카테고리' : category, '순위' : ranking, '품번' : product_id, '브랜드명' : brand_name, '상품명(한글)' : product_title ,
                '판매가' : sales_price, '비회원가' : non_member_price, '좋아요 수' : product_like, 'URL' : items_url})

        now = datetime.now()
        now_str = now.strftime("%Y%m%d%H%M%S")
        df.to_csv(f'무신사_{sex}_{key}_Top100_{now_str}.csv',index=False, encoding='utf-8-sig')
        
        
def main():
    
    sex = {'ALL', 'MEN', 'WOMEN'}
    
    ## 카테고리 식별
    category_dict = identify_Category_id()
    
    ## 상품정보 크롤링을 위한 selector 지정
    list_of_selectors = setting_selector()
    
    ## ########### 카테고리별 상품 랭킹 리스트 
    extraction_ranking(category_dict, list_of_selectors, 'MEN')
    extraction_ranking(category_dict, list_of_selectors, 'WOMEN')
    extraction_ranking(category_dict, list_of_selectors, 'ALL')
    
 
if __name__ == "__main__":
    main()