import re
import requests
from bs4 import BeautifulSoup
import persian
import csv



Data = []

divar_url = "https://divar.ir"
buy_residential_divar_url = f'https://divar.ir/s/tehran/buy-apartment?page=1'


req_buy_residential_divar = requests.get(buy_residential_divar_url).text
soup_buy_residential_divar = BeautifulSoup(req_buy_residential_divar,'html.parser')

for article_advertising in soup_buy_residential_divar.find_all('article',class_ = 'kt-post-card kt-post-card--outlined kt-post-card--padded kt-post-card--has-action'):
    advertising_residential_item_divar_url = divar_url + article_advertising.parent.get('href')
    req_advertising_residential_item_divar = requests.get(advertising_residential_item_divar_url).text
    soup_advertising_residential_item_divar = BeautifulSoup(req_advertising_residential_item_divar,'html.parser')

    #set title
    title_advertising_residential_item_divar = soup_advertising_residential_item_divar.find('div','kt-page-title__title kt-page-title__title--responsive-sized')
    title_advertising_residential_item_divar = title_advertising_residential_item_divar.text if title_advertising_residential_item_divar else ' '
    

    #find main item info
    main_item_array = []
    pattern_main_item = r'<span class="kt-group-row-item__value">(\d*)</span>'
    for main_item in soup_advertising_residential_item_divar.find_all('span', class_ = 'kt-group-row-item__value'):
        temp_main_item = str(main_item)
        value_match_pattern_main_item = re.findall(pattern_main_item, temp_main_item)
        if value_match_pattern_main_item:
            main_item_array.append(int(value_match_pattern_main_item[0]))
        else:
            main_item_array.append(0)

    if len(main_item_array) > 0:        
        main_item_array = main_item_array[0:3]            

    #find item property info
    prop_item_array = []
    pattern_prop_item = r'<span class="kt-group-row-item__value kt-body kt-body--stable">(.*(\u0646\u062F\u0627\u0631\u062F).*)</span>'
    for prop_item in soup_advertising_residential_item_divar.find_all('span', class_ = 'kt-group-row-item__value kt-body kt-body--stable'):
        temp_prop_item = str(prop_item)
        value_match_pattern_prop_item = re.findall(pattern_prop_item, temp_prop_item)
        if value_match_pattern_prop_item:
            prop_item_array.append(0)
        else:
            prop_item_array.append(1)

    #find total price and per meter
    price_item_array = []
    pattern_price_item = r'<p class="kt-unexpandable-row__value">((.*)(\u062A\u0648\u0645\u0627\u0646))</p>'
    for price_item in soup_advertising_residential_item_divar.find_all('p',class_='kt-unexpandable-row__value'):
        temp_price_item = str(price_item)
        value_match_pattern_price_item = re.findall(pattern_price_item, temp_price_item)
        if value_match_pattern_price_item:
            temp_price_value = 0
            for i in value_match_pattern_price_item[0][1]:
                i = persian.convert_fa_numbers(i)
                if i.isnumeric():
                    temp_price_value = temp_price_value * 10 + int(i)      
            price_item_array.append(temp_price_value)
        else:
            price_item_array.append(0)

    #find floor
    floor = 0
    pattern_floor_in_floors = r'<p class="kt-unexpandable-row__value">(.*)(\u0627\u0632)(.*)</p>'
    pattern_floor_digit = r'<p class="kt-unexpandable-row__value">(\d*)</p>'
    for floor_item in soup_advertising_residential_item_divar.find_all('p',class_ = 'kt-unexpandable-row__value'):
        temp_floor_item = str(floor_item)
        value_match_pattern_floor_item = re.findall(pattern_floor_in_floors, temp_floor_item)
        if value_match_pattern_floor_item:
            persian_to_english_number_of_floor = persian.convert_fa_numbers(value_match_pattern_floor_item[0][0])
            if persian_to_english_number_of_floor.isnumeric():
                floor = int(persian_to_english_number_of_floor)
        else:
            value_match_pattern_floor_item_digit = re.findall(pattern_floor_digit,temp_floor_item)
            if value_match_pattern_floor_item_digit:
                persian_to_english_number_of_floor = persian.convert_fa_numbers(value_match_pattern_floor_item_digit[0][0])
                if persian_to_english_number_of_floor.isnumeric():
                    floor = int(persian_to_english_number_of_floor)
            else:
                floor = 0

    #find neighborhood ،(.*)\|
    neighborhood = ''
    pattern_neighborhood = r'<div class="kt-page-title__subtitle kt-page-title__subtitle--responsive-sized">(.*)(،(.*)\|)(.*)</div>'
    for neighborhood_item in soup_advertising_residential_item_divar.find_all('div',class_= 'kt-page-title__subtitle kt-page-title__subtitle--responsive-sized'):
        temp_neighborhood_item = str(neighborhood_item)
        value_match_pattern_neighborhood_item = re.findall(pattern_neighborhood,temp_neighborhood_item)
        neighborhood = str(persian.convert_en_characters(value_match_pattern_neighborhood_item[0][2].strip()))

    row = [title_advertising_residential_item_divar, main_item_array[0],
           main_item_array[1], main_item_array[2],
           prop_item_array[0], prop_item_array[1], 
           prop_item_array[2], floor, neighborhood, 
           price_item_array[0],price_item_array[1],advertising_residential_item_divar_url]
    
    Data.append(row)


with open('DivarCsv.csv', 'w', encoding='utf-32', newline='') as DivarCsv:
    fieldnames = ['Title', 'Meterage', 'YearConstruction', 'NumberOfRooms', 
                  'HasElevator','HasParking','HasWarehouse',
                  'Floor', 'Neighborhood','TotalPrice',
                  'PricePerMeterage', 'URL']
    writer = csv.DictWriter(DivarCsv, fieldnames=fieldnames)

    writer.writeheader()
    for row in Data:
        writer.writerow({'Title': row[0], 'Meterage': row[1], 'YearConstruction': row[2], 'NumberOfRooms': row[3],
                         'HasElevator': row[4], 'HasParking': row[5],
                         'HasWarehouse': row[6], 'Floor': row[7],
                         'Neighborhood': row[8], 'TotalPrice': row[9],
                         'PricePerMeterage': row[10], 'URL':row[11]})
