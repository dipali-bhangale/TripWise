"""Offline-first travel tools. All prices and route estimates are illustrative."""
from datetime import date, timedelta
from math import radians, sin, cos, asin, sqrt
from copy import deepcopy
from services.travel_service import DESTINATIONS, generate_trip, packing_list, optimize_trip

ATTRACTIONS = {
 'Goa': [('Baga Beach',15.5553,73.7517,'Beach'),('Fort Aguada',15.4922,73.7736,'History'),('Anjuna Beach',15.5736,73.7407,'Beach'),('Basilica of Bom Jesus',15.5009,73.9116,'Culture'),('Palolem Beach',15.0100,74.0232,'Beach')],
 'Jaipur':[('Amber Fort',26.9855,75.8513,'History'),('Hawa Mahal',26.9239,75.8267,'History'),('City Palace',26.9258,75.8237,'Culture'),('Jantar Mantar',26.9248,75.8246,'Culture'),('Nahargarh Fort',26.9373,75.8155,'History')],
 'Mumbai':[('Gateway of India',18.9220,72.8347,'History'),('Marine Drive',18.9430,72.8238,'Nature'),('Elephanta Caves',18.9633,72.9315,'History'),('Juhu Beach',19.0988,72.8264,'Beach')],
 'Delhi':[('India Gate',28.6129,77.2295,'History'),('Red Fort',28.6562,77.2410,'History'),('Qutub Minar',28.5244,77.1855,'History'),('Humayun Tomb',28.5933,77.2507,'History')],
 'Udaipur':[('City Palace',24.5764,73.6835,'History'),('Lake Pichola',24.5720,73.6790,'Nature'),('Fateh Sagar Lake',24.6011,73.6734,'Nature'),('Saheliyon Ki Bari',24.6032,73.6850,'Nature')],
 'Manali':[('Hadimba Temple',32.2485,77.1801,'Culture'),('Solang Valley',32.3160,77.1550,'Adventure'),('Old Manali',32.2581,77.1745,'Culture'),('Vashisht Hot Springs',32.2645,77.1880,'Nature')]
}

def destination_recommender(budget,days,travelers=1,interests=None,weather='Any'):
 interests=interests or []
 ranked=[]
 for name,info in DESTINATIONS.items():
  from datetime import date
  start=date.today()+timedelta(days=7)
  estimate=generate_trip({'origin':'Starting city','destination':name,'start':start,'end':start+timedelta(days=days-1),'travelers':travelers,'budget':max(1,budget),'style':'Budget','interests':interests,'transport':'Train','accommodation':'Budget hotel'})
  total=estimate['total']
  match=sum(any(w.lower() in a.lower() for a in info['places']) for w in interests)
  ranked.append({'destination':name,'estimated_total':total,'days':days,'attractions':info['places'][:3],'reason':('Matches your interests; ' if match else '')+('within indicative budget' if total<=budget else 'may exceed your budget'),'score':match*3+(2 if total<=budget else 0),'description':f'Explore {name} with a mix of sightseeing and local culture','recommended_duration':f'{days} days','activities':info['places'][:2], 'weather_note':'Seasonal conditions must be checked separately'})
 return sorted(ranked,key=lambda x:x['score'],reverse=True)

def hotel_recommender(trip):
 nights=max(trip['days']-1,1)
 return [{'name':name,'location':f'{trip["destination"]} central area (area suggestion only)','nightly_inr':rate,'nights':nights,'estimated_total_inr':rate*nights,'advantages':adv,'status':'Illustrative category, not a verified property'} for name,rate,adv in [('Hostel / shared stay',850,'Lowest indicative cost'),('Budget guesthouse',1450,'Private-room option'),('Mid-range hotel',2700,'More amenities'),('Premium accommodation',5500,'Comfort-focused')]]

def transport_planner(trip):
 passengers=trip['inputs']['travelers']
 return [{'mode':mode,'estimated_roundtrip_inr':cost*passengers,'estimated_duration':'Not verified; varies by route','convenience':rating,'suitability':'Budget' if cost<=1800 else 'Convenience'} for mode,cost,rating in [('Bus',1200,'Medium'),('Train',1800,'High'),('Car',4500,'Flexible'),('Flight',6500,'Fast where available')]]

def attraction_recommender(trip):
 return [{'name':name,'category':cat,'duration':'1–3 hours (illustrative)','entry_cost':'Check locally','why':'Popular destination highlight'} for name,_,_,cat in ATTRACTIONS.get(trip['destination'],[]) ] or [{'name':x,'category':'Explore','duration':'Varies','entry_cost':'Unknown','why':'Illustrative activity'} for x in trip['places']]

def restaurant_recommender(trip,diet='Any'):
 return [{'name':f'{trip["destination"]} local dining area — {food}','cuisine':'Regional','dish':food,'meal':'Lunch / dinner','price':'₹150–₹500 per person (illustrative)','location':'Search near your attractions','status':'Food idea, not a verified restaurant'} for food in trip['food'] if diet!='Vegetarian' or not any(x in food.lower() for x in ['fish','chicken','meat'])]

def weather_advisor(trip):
 return {'status':'No live forecast; general planning advice','tips':['Carry rain protection and check a forecast before departure.','Choose indoor museums or markets during heavy rain.','Carry water, sunscreen and comfortable footwear for outdoor activities.']}

def distance_km(a,b):
 lat1,lon1=map(radians,a);lat2,lon2=map(radians,b)
 v=sin((lat2-lat1)/2)**2+cos(lat1)*cos(lat2)*sin((lon2-lon1)/2)**2
 return 6371*2*asin(min(1,sqrt(v)))

def route_optimizer(trip,mode='Walking'):
 points=ATTRACTIONS.get(trip['destination'],[])
 if not points:return {'points':[],'straight_line_km':None,'status':'No verified attraction coordinates available'}
 remaining=points.copy(); ordered=[remaining.pop(0)]
 while remaining:
  last=ordered[-1];idx=min(range(len(remaining)),key=lambda i:distance_km(last[1:3],remaining[i][1:3]))
  ordered.append(remaining.pop(idx))
 distance=sum(distance_km(a[1:3],b[1:3]) for a,b in zip(ordered,ordered[1:]))
 return {'points':[{'name':p[0],'lat':p[1],'lon':p[2],'category':p[3]} for p in ordered],'straight_line_km':round(distance,1),'status':f'Illustrative nearest-neighbor sequence ({mode}); straight-line distance is NOT road distance or travel time'}

def replace_activity(trip,day,period,activity):
 return add_attraction(trip,activity,day,period)

def add_day(trip):
 p=deepcopy(trip);inputs=p['inputs'].copy();inputs['end']=str(date.fromisoformat(inputs['end'])+timedelta(days=1))
 inputs['start']=date.fromisoformat(inputs['start']);inputs['end']=date.fromisoformat(inputs['end'])
 new=generate_trip(inputs)
 for idx,old in enumerate(trip['itinerary']):
  if idx<len(new['itinerary']):
   for field in ('morning','afternoon','evening','food'):
    new['itinerary'][idx][field]=old[field]
 return new

def add_attraction(trip,attraction,day=1,period='afternoon'):
 p=deepcopy(trip)
 if not 1<=day<=p['days']:raise ValueError('Day is outside trip duration')
 if period not in ('morning','afternoon','evening'):raise ValueError('Invalid period')
 p['itinerary'][day-1][period]=attraction
 return p

def change_accommodation(trip,kind='Budget hotel'):
 p=deepcopy(trip);p['inputs']['accommodation']=kind
 inputs=p['inputs'].copy();inputs['start']=date.fromisoformat(inputs['start']);inputs['end']=date.fromisoformat(inputs['end'])
 new=generate_trip(inputs)
 for idx,old in enumerate(trip['itinerary']):
  if idx<len(new['itinerary']):
   for field in ('morning','afternoon','evening','food'):new['itinerary'][idx][field]=old[field]
 return new
