from datetime import timedelta
DESTINATIONS={
 'Goa':{'places':['Baga Beach','Fort Aguada','Anjuna Beach','Old Goa Churches','Palolem Beach'],'food':['Goan fish curry','Bebinca','Vegetarian thali'],'lat':15.49,'lon':73.82,'evenings':['Sunset at Candolim Beach','Panaji riverside promenade','Anjuna evening cafés','Miramar Beach sunset','Local Goan cultural performance']},
 'Jaipur':{'places':['Amber Fort','Hawa Mahal','City Palace','Jantar Mantar','Nahargarh Fort'],'food':['Dal baati churma','Ghewar','Kachori'],'lat':26.91,'lon':75.79,'evenings':['Nahargarh sunset viewpoint','Johari Bazaar walk','Albert Hall Museum illuminated exterior','Traditional Rajasthani cultural evening','Hawa Mahal evening photo walk']},
 'Manali':{'places':['Hadimba Temple','Solang Valley','Old Manali','Vashisht Hot Springs','Mall Road'],'food':['Siddu','Thukpa','Rajma chawal'],'lat':32.24,'lon':77.19,'evenings':['Old Manali café evening','Mall Road stroll','Beas River viewpoint','Local Himachali food tasting','Quiet mountain sunset viewpoint']},
 'Mumbai':{'places':['Gateway of India','Marine Drive','Elephanta Caves','Juhu Beach','Sanjay Gandhi National Park'],'food':['Vada pav','Pav bhaji','Bhel puri'],'lat':19.08,'lon':72.88,'evenings':['Marine Drive sunset','Juhu Beach evening','Bandra Bandstand stroll','Colaba evening walk','Worli Sea Face sunset']},
 'Delhi':{'places':['India Gate','Red Fort','Qutub Minar','Humayun Tomb','Lodhi Garden'],'food':['Chole bhature','Paratha','Chaat'],'lat':28.61,'lon':77.21,'evenings':['India Gate evening walk','Connaught Place stroll','Dilli Haat cultural evening','Lodhi Garden early evening','Old Delhi food exploration']},
 'Udaipur':{'places':['City Palace','Lake Pichola','Fateh Sagar Lake','Saheliyon Ki Bari','Sajjangarh Palace'],'food':['Dal baati','Gatte ki sabzi','Kachori'],'lat':24.59,'lon':73.71,'evenings':['Lake Pichola sunset','Fateh Sagar lakeside walk','Bagore Ki Haveli cultural show','Ambrai Ghat evening','Old City heritage stroll']},
}
CATEGORIES=['Transportation','Accommodation','Food','Attractions','Activities','Local transportation','Miscellaneous']
WEIGHTS=[.23,.30,.17,.08,.08,.09,.05]
def validate_trip(t):
 if not t.get('origin','').strip(): raise ValueError('Please enter a starting city.')
 if not t['destination'].strip(): raise ValueError('Please enter a destination.')
 if t['end']<t['start']: raise ValueError('Return date cannot be before departure.')
 if t['budget']<=0: raise ValueError('Budget must be positive.')
 if t['travelers']<1: raise ValueError('At least one traveler is required.')
def generate_trip(t):
 validate_trip(t)
 days=(t['end']-t['start']).days+1
 dest=t['destination'].strip().title()
 data=DESTINATIONS.get(dest,{'places':['City center exploration','Local heritage walk','Popular market','Nature excursion','Cultural experience'],'food':['Local specialties','Regional thali','Street food'],'lat':None,'lon':None})
 # All values are offline illustrative rates, never live quotations.
 people=t['travelers']; nights=max(0,days-1)
 style_factor={'Budget':1.0,'Moderate':1.45,'Luxury':2.5,'Adventure':1.3,'Family':1.25,'Romantic':1.5,'Relaxation':1.3,'Cultural':1.15}.get(t['style'],1.0)
 destination_factor={'Goa':1.15,'Jaipur':1.0,'Manali':1.2,'Mumbai':1.45,'Delhi':1.2,'Udaipur':1.1}.get(dest,1.0)
 transport_rates={'Bus':1200,'Train':1800,'Car':4500,'Flight':6500}
 hotel_rates={'Hostel':850,'Budget hotel':1450,'Mid-range hotel':2700,'Luxury hotel':5500,'Homestay':1250}
 rooms=max(1,(people+1)//2) if t['accommodation']!='Hostel' else people
 travel=round(transport_rates.get(t['transport'],1800)*people*destination_factor)
 accommodation=round(hotel_rates.get(t['accommodation'],1450)*nights*rooms*destination_factor*style_factor)
 costs={'Transportation':travel,'Accommodation':accommodation,'Food':round(450*days*people*destination_factor*style_factor),'Attractions':round(180*days*people*destination_factor),'Activities':round(220*days*people*style_factor),'Local transportation':round(170*days*people*destination_factor),'Miscellaneous':round(120*days*people)}
 itinerary=[]
 for i in range(days):
  a=data['places'][(2*i)%len(data['places'])]; b=data['places'][(2*i+1)%len(data['places'])]
  itinerary.append({'day':i+1,'date':str(t['start']+timedelta(days=i)),'morning':a,'afternoon':b,'evening':data.get('evenings',['Local evening exploration']) [i%len(data.get('evenings',['Local evening exploration']))],'food':data['food'][i%len(data['food'])],'estimated_activity_cost':round(costs['Attractions']/days+costs['Activities']/days),'activities':[a,b],'travel_time':'Not verified'})
 return {'inputs':{**t,'start':str(t['start']),'end':str(t['end'])},'destination':dest,'days':days,'itinerary':itinerary,'costs':costs,'total':sum(costs.values()),'places':data['places'],'food':data['food'],'lat':data['lat'],'lon':data['lon'],'notes':'Illustrative input-sensitive estimates only; not verified live prices or bookings.'}
def optimize_trip(trip):
 p={**trip,'costs':trip['costs'].copy()}
 for k,f in [('Accommodation',.72),('Transportation',.82),('Food',.85),('Activities',.75)]: p['costs'][k]=round(p['costs'][k]*f)
 p['total']=sum(p['costs'].values())
 p['optimization']={'original_total':trip['total'],'optimized_total':p['total'],'savings':trip['total']-p['total'],'changes':['Lower-cost accommodation category','Lower-cost transportation','Economical dining','Reduced paid activities']}
 return p

def packing_list(trip):
 return {'Documents':['ID proof','Tickets and reservations'],'Clothing':['Comfortable outfits','Walking shoes','Weather-appropriate jacket'],'Electronics':['Phone charger','Power bank'],'Toiletries':['Toothbrush','Sunscreen'],'Medicines':['Personal medicines','First aid kit'],'Travel essentials':['Reusable water bottle','Wallet'],'Activities':['Daypack','Camera']}
