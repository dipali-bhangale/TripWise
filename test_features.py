from datetime import date,timedelta
from services.travel_service import generate_trip
from services.features import destination_recommender,route_optimizer,add_day,add_attraction,restaurant_recommender,hotel_recommender,transport_planner
from agent.travel_agent import answer

def trip():
 d=date(2026,11,2)
 return generate_trip({'origin':'Nagpur','destination':'Goa','start':d,'end':d+timedelta(days=2),'travelers':2,'budget':15000,'style':'Budget','interests':['Beaches'],'transport':'Train','accommodation':'Hostel'})

def test_destination_recommendation():assert len(destination_recommender(15000,3,2))>=5

def test_route_has_unique_points():
 r=route_optimizer(trip());assert len(r['points'])>=3;assert len({p['name'] for p in r['points']})==len(r['points'])

def test_add_day_and_attraction():
 p=trip();extended=add_day(p);assert extended['days']==4 and p['days']==3
 edited=add_attraction(p,'Fort Aguada');assert edited['itinerary'][0]['afternoon']=='Fort Aguada'

def test_recommendations():
 p=trip();assert hotel_recommender(p) and transport_planner(p) and restaurant_recommender(p)

def test_chat_changes_context():
 p=trip();response,new=answer('add one more day',p);assert new['days']==4
 response,new=answer('make my trip cheaper',p);assert new['total']<p['total']
 response,new=answer('add a beach',p);assert 'Beach' in new['itinerary'][0]['afternoon']
