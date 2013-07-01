import requests 
import re
import time
from bs4 import BeautifulSoup

HOST = 'http://www.urbanoutfitters.com/'
CATEGORY_URL = 'http://www.urbanoutfitters.com/urban/catalog/category.jsp?id='
IMG_URL = 'http://images.urbanoutfitters.com/is/image/UrbanOutfitters/%s_%s_' 
FORMS = ['?$detailThumb$', '?$detailMain$']    

def make_soup(url):
    r = requests.get(url)
    s = BeautifulSoup(r.content, 'lxml')
    return s    

def get_swatches(p):
    swatches = p.find('ul', 'category-product-swatches')
    return ([l.a['href'][-3:] for l in swatches.findAll('li')] if swatches 
            else [])

def get_id_and_colors(p):
    img_link = p.find('p', 'category-product-image').img['src']
    p_id, color, _ = img_link.split('/')[-1].split('_')
    swatches = get_swatches(p) 
    return p_id, (swatches if swatches else [color])

def get_detail(p):
    des = p.find(class_='category-product-description')
    instore = False if p.find('li',"category-product-online-only") else True
    price, name = get_price(des), des.find('a').string
    return price, name, instore

def get_price(des):
    price = (des.find('h3', 'price').string or
             des.find('h3', 'price').text or
             des.find(class_='price').find('span', 'price-sale').string)

    if len(price) > 8:
        l = map(float, re.findall('\d+(?:\.\d+)?', price))
        return l[-1] / (l[-2] if len(l) == 2 else 1)
    return float(price[1:6])

def get_page_products(s):
    cats = s.find(id='category-products')
    prods = [p for p in cats.findAll('div', 'category-product')] 
    return prods

def get_pages_and_items(s):
    span = s.find(class_ = 'category-pagination-pages')
    pages = int(re.findall('\d+', span.text)[-1])
    items = int(span.find('a')['href'].split('=')[-1])
    return pages, items

def get_pages_urls(pages, items, catg):
    base_uri = CATEGORY_URL + catg+ '&startValue=%d'
    rang = items - 1
    pages_uri = [base_uri % i for i in range(1, pages*rang, rang)]
    return pages_uri

def get_all_prods(category):
    uri = CATEGORY_URL + category
    s = make_soup(uri) 
    prods = get_page_products(s)

    pages, items = get_pages_and_items(s) 
    pages_uri = get_pages_urls(pages, items, category)

    for p_uri in pages_uri:
        p_soup = make_soup(p_uri)
        if p_soup:
            prods += get_page_products(p_soup)
    return prods

def compose_img_link(pid, color):
    return [IMG_URL % (pid, color) + char + form
            for char in 'bdef'
            for form in FORMS]

def letsparse(category):
    prods = get_all_prods(category)
    print 'category %s got %d items' % (category, len(prods))
    for p in prods:
        img_id, colors = get_id_and_colors(p) 
        for c in colors:
            for l in compose_img_link(img_id, c):
                print l

categories = """W_APP_DRESSES WOMENS_SHOES W_NEWARRIVALS W_CAMP M_TOPS MENS_SHOES M_NEWARRIVALS M_PATTERN A_DEC_BEDDING A_MEDIA_GADGETS A_NEWARRIVALS W_WORKAHOLIC SALE_W SALE_M SALE_APT""".split(' ') 


if __name__ == '__main__':
    print 'categories to consider, '
    for c in categories:
        print c
    catg = raw_input('enter a category, lets parse \n').upper()
    letsparse(catg)

