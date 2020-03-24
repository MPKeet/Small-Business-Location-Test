

import requests
import json
import pandas as pd






#Geolocation API to find city, lat/lon, postcode, county, and state info
def Geolocate():
    address=input("Please enter a valid US Address: ")
    url="https://maps.googleapis.com/maps/api/geocode/json?address={}&key=A[Key]".format(address)
# Ping google for the reuslts:
    results = requests.get(url)
# Results will be in JSON format - convert to dict using requests functionality
    results = results.json()

    answer = results['results'][0]
    locality=",".join([x['long_name'] for x in answer.get('address_components')
                      if 'locality' in x.get('types')])
    latitude = answer.get('geometry').get('location').get('lat')
    longitude=answer.get('geometry').get('location').get('lng')
    postcode=",".join([x['long_name'] for x in answer.get('address_components') 
                                  if 'postal_code' in x.get('types')])
    county=','.join([x['long_name'] for x in answer.get('address_components')
                     if 'administrative_area_level_2' in x.get('types')])
    state=','.join([x['long_name'] for x in answer.get('address_components')
                     if 'administrative_area_level_1' in x.get('types')])

    print('City: {} \nLatitude = {}\nLongitude = {}\nPostcode: {}\nCounty: {}\nState: {}'.format(locality, latitude, longitude, postcode, county, state))

    
    Intersect(locality, latitude, longitude)
    
    Restauranter(address, latitude, longitude, postcode)
    
    
#calls the api to find nearest intersection to a given address

def Intersect(locality, latitude, longitude):
    url="http://api.geonames.org/findNearestIntersectionJSON?lat=%s&lng=%s&username=[User]" % (latitude, longitude)
    results=requests.get(url)
    results=results.json()


    answer = results['credits'][0]
    street1=results.get('intersection').get('street1')
    street2=results.get('intersection').get('street2')

      
    print('The nearest intersection is comprised of {} and {}'.format(street1,street2))

# finds nearby restaurants

def Restauranter(address, latitude, longitude, postcode):
    
    radius=500
    api_key='[Key]'
    headers={'Authorization': 'Bearer %s' % (api_key)}


    url='https://api.yelp.com/v3/businesses/search?latitude=%s&longitude=%s&radius=%s&term=restaurant' % (latitude,longitude,radius)

    results=requests.get(url, headers=headers)
    results=results.json()
    try:
        answer=results['businesses'][0]
        totalr=results.get('total')
    except (IndexError):
        totalr=0

    
    Grocer(address, latitude, longitude, postcode, totalr)

# finds nearby grocery stores

def Grocer(address, latitude, longitude, postcode, totalr):
    
    radius=500
    api_key='[Key]'
    headers={'Authorization': 'Bearer %s' % (api_key)}


    url='https://api.yelp.com/v3/businesses/search?latitude=%s&longitude=%s&radius=%s&term=Grocery+Store' % (latitude,longitude,radius)

    results=requests.get(url, headers=headers)
    results=results.json()
    try:
        answer=results['businesses'][0]
        totalg=results.get('total')
    except (IndexError):
        totalg=0

    Bigbox(address, latitude, longitude, postcode, totalr, totalg)

# finds nearby department stores

def Bigbox(address, latitude, longitude, postcode, totalr, totalg):
    radius=400
    api_key='[Key]'
    headers={'Authorization': 'Bearer %s' % (api_key)}


    url='https://api.yelp.com/v3/businesses/search?latitude=%s&longitude=%s&radius=%s&term=Department+Store' % (latitude,longitude,radius)

    results=requests.get(url, headers=headers)
    results=results.json()
    try:
        answer=results['businesses'][0]
        totalb=results.get('total')
    except (IndexError):
        totalb=0

    Anchors(address, latitude, longitude,postcode, totalr, totalg, totalb)

# gathers yelp API info to count nearby grocery stores, restaurants, and department stores

def Anchors(address, latitude, longitude,postcode, totalr, totalg, totalb):

    totala=(totalr)+(totalg)+(totalb)

    
    if 0<totala<=4:
        a_score=2
    elif 5<totala<=20:
        a_score=4
    elif 21<totala<=30:
        a_score=6
    else:
        a_score=8
      
    YelpComp(a_score,latitude,longitude, postcode)

#looks for nearby potential competitors from yelp API and makes a score based on how saturated the area is for the category

def YelpComp(a_score, latitude,longitude, postcode):

    business_cat=input("Please enter your business category: ")
    radius=1609
    
    api_key='[Key]'
    headers={'Authorization': 'Bearer %s' % (api_key)}


    url='https://api.yelp.com/v3/businesses/search?latitude=%s&longitude=%s&radius=%s&term=%s' % (latitude,longitude,radius, business_cat)

    results=requests.get(url, headers=headers)
    results=results.json()
    answer=results['businesses'][0]
    total=results.get('total')
    
    print('Number of businesses nearby in the {} category: {}'.format(business_cat, total))
    
    #arbitrary numbers because business saturation is a subjective call and depends on market category
    #deprecated after change from user input to set radius
   
    if 10>total>=0:
        comp_score=30
    elif 20>total>=11:
        comp_score=20
    elif 30>total>=21:
        comp_score=10
    else:
        comp_score=0
    Traffic(a_score, comp_score, postcode)

#Asks user to check state provided data against program-given intersection for traffic counts

def Traffic(a_score, comp_score, postcode):
    AADT=int(input("Please enter the AADT count for the provided intersection above(numbers only): "))

    if 300>AADT>=0:
        count_score=0
    elif 600>AADT>=0:
        count_score=10
    elif 1200>AADT>=601:
        count_score=20
    elif 2500>AADT>=1201:
        count_score=30
    elif 5000>AADT>=2501:
        count_score=40
    else:
        count_score=45
    
    Highway(a_score, comp_score, count_score, postcode)

# asks for user input as to whether there is a nearby highway

def Highway(a_score, comp_score, count_score, postcode):
    Hi_Close=input("Is there a highway within 2 miles?(enter y or n): ")
    if Hi_Close is 'y':
        hi_score=5
    if Hi_Close is 'n':
        hi_score=0
    Popper(a_score, comp_score, count_score, hi_score, postcode)

# API call to gather population information for the local zipcode of given address

def Popper(a_score, comp_score, count_score, hi_score, postcode):
    api_key='[Key]'
    url='https://api.census.gov/data/2017/acs/acs5?key={}&get=B01003_001E&for=zip%20code%20tabulation%20area:{}'.format(api_key, postcode)
    results=requests.get(url)
    results=results.json()[1:]
    results=[item[::-1] for item in results]
    pops=pd.DataFrame(columns=['zip', 'pop'], data=results)
    pop=pops.iloc[0]['pop']
    pop=int(pop)
    print('Population: {}\n***\n'.format(pop))
    Poppy(a_score, comp_score, count_score, hi_score, pop)

#converts zipcode population info from census API to a score out of 12

def Poppy(a_score, comp_score, count_score, hi_score, pop):
    if 1<pop<=10000:
        pop_score=2
    elif 10001<pop<=20000:
        pop_score=3
    elif 20001<pop<=30000:
        pop_score=4
    elif 30001<pop<=40000:
        pop_score=5
    elif 40001<pop<=50000:
        pop_score=6
    elif 50001<pop<=60000:
        pop_score=7
    elif 60001<pop<=70000:
        pop_score=8
    elif 70001<pop<=80000:
        pop_score=9
    elif 80001<pop<=90000:
        pop_score=10
    elif 90001<pop<=10000:
        pop_score=11
    else:
        pop_score=12

    Grader(pop_score, comp_score, a_score, count_score, hi_score)
    
# Grades the above scores to a total score out of 100

def Grader(pop_score, comp_score, a_score, count_score, hi_score):
    Grade=pop_score+comp_score+a_score+count_score+hi_score
    print('[Business Location Viability Score: {}/100]'.format(Grade))

    print('Traffic Score: {}/45'.format(count_score))
    print('Comp Score: {}/30'.format(comp_score))
    print('Population Score: {}/12'.format(pop_score))
    print('Anchor Score: {}/8'.format(a_score))
    print('Highway Access Score: {}/5'.format(hi_score))
    
    

Geolocate()
