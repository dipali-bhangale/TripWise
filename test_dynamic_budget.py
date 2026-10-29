from datetime import date,timedelta
from copy import deepcopy
from services.travel_service import generate_trip,optimize_trip,packing_list
from services.features import change_accommodation,add_day,route_optimizer,weather_advisor,transport_planner,hotel_recommender,restaurant_recommender,attraction_recommender,destination_recommender
from agent.travel_agent import answer
import pytest

def base():
 d=date(2026,11,4)
 return {'origin':'Nagpur','destination':'Goa','start':d,'end':d+timedelta(days=2),'travelers':2,'budget':15000,'style':'Budget','interests':['Nature'],'transport':'Train','accommodation':'Hostel'}

def test_transport_changes_estimate():
 x=base();a=generate_trip(x);x['transport']='Flight';b=generate_trip(x)
 assert b['costs']['Transportation']>a['costs']['Transportation'] and b['total']>a['total']

def test_accommodation_changes_estimate():
 x=base();a=generate_trip(x);x['accommodation']='Luxury hotel';b=generate_trip(x)
 assert b['costs']['Accommodation']>a['costs']['Accommodation']

def test_travelers_days_and_destination_change_estimate():
 x=base();a=generate_trip(x)
 x['travelers']=4;assert generate_trip(x)['total']>a['total']
 x=base();x['end']+=timedelta(days=2);assert generate_trip(x)['total']>a['total']
 x=base();x['destination']='Mumbai';assert generate_trip(x)['total']!=a['total']

def test_budget_is_cap_not_price():
 x=base();a=generate_trip(x);x['budget']=50000;b=generate_trip(x)
 assert a['total']==b['total'] and b['inputs']['budget']==50000

def test_chat_creates_trip():
 msg,p=answer('Plan a 3-day trip to Goa for 2 people under ₹15,000.',None)
 assert p and p['destination']=='Goa' and p['days']==3 and p['inputs']['budget']==15000

def test_chat_accommodation_recalculates():
 p=generate_trip(base());msg,new=answer('change hotel',p)
 assert new['inputs']['accommodation']=='Budget hotel' and new['costs']['Accommodation']!=p['costs']['Accommodation']

def test_tools_work():
 p=generate_trip(base())
 assert len(packing_list(p))>=5
 assert optimize_trip(p)['total']<p['total']
 assert add_day(p)['days']==4
 assert route_optimizer(p)['points']
 assert weather_advisor(p)['tips']
 assert transport_planner(p) and hotel_recommender(p) and restaurant_recommender(p) and attraction_recommender(p)
 assert destination_recommender(15000,3)

def test_validation():
 x=base();x['end']=x['start']-timedelta(days=1)
 with pytest.raises(ValueError):generate_trip(x)
 x=base();x['budget']=0
 with pytest.raises(ValueError):generate_trip(x)
