import xmltodict
import requests
import mysql.connector


def find_href_title(html, url):
    strings = []
    start = start_for_href_find = end_of_a = False
    starting_point = 0
    while start != -1:
        if not start:
            start_for_href_find = html.find('<a', starting_point)
            start = html.find('href="', start_for_href_find)
            starting_point = start + 6
            end = False
        else:
            end = html.find('"', starting_point)
            end_of_a = html.find('</a>', starting_point)
        if start and end and start_for_href_find and end_of_a:
            main_list = ["", "", ""]
            for p in range(start+6, end):
                main_list[0] = main_list[0]+str(html[p])
                main_list[2] = url
            start_title = start_for_href_find
            while True:
                start_of_title = html.find('title="', start_title, end_of_a)
                end_of_title = html.find('"', start_of_title+7, end_of_a)
                for p in range(start_of_title + 7, end_of_title):
                    if start_of_title != -1:
                        main_list[1] = main_list[1]+str(html[p])
                break

            main_list = tuple(main_list)
            strings.append(main_list)
            starting_point = end
            start = False
    return strings

cnx = mysql.connector.connect(user='sql_user', password='abcdef',
                              host='database',
                              database='scraper',
                              auth_plugin='mysql_native_password')
cursor = cnx.cursor()

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
xml = requests.get("https://covid.gov.cz/sitemap.xml", headers=headers)
xml.encoding = "utf-8"
xml_dict = xmltodict.parse(xml.text)

for urls in xml_dict['urlset']['url']:
    r = requests.get(urls["loc"], headers=headers)
    r.encoding = "utf-8"
    add_data = find_href_title(r.text, urls["loc"])
    add_sql = ("INSERT INTO websites (url, title, domain) VALUES (%s, %s, %s)")
    cursor.executemany(add_sql, add_data)

cnx.commit()

cursor.close()
cnx.close()
