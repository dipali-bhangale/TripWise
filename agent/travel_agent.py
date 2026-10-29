"""Context-aware deterministic tool router, with optional Gemini explanations."""
import re
from datetime import date,timedelta
from services.features import add_day,add_attraction,change_accommodation,hotel_recommender,restaurant_recommender,route_optimizer,weather_advisor,transport_planner,attraction_recommender
from services.travel_service import optimize_trip,packing_list,generate_trip
from config import GEMINI_API_KEY

def answer(message,trip):
 q=message.lower().strip()
 # A new trip request works even without an existing trip or Gemini credentials.
 if re.search(r'\b(plan|create|generate)\b.*\btrip\b',q):
  dest_match=re.search(r'\bto\s+([a-z][a-z ]{1,35}?)(?=\s+for\b|\s+under\b|[.,!?]|$)',q)
  days_match=re.search(r'(\d+)\s*[- ]?day',q)
  people_match=re.search(r'(\d+)\s*(?:people|persons|travelers|travellers)',q)
  budget_match=re.search(r'(?:under|budget(?: of)?|within)\s*[₹rs. ]*([\d,]+)',q)
  if dest_match:
   dest=dest_match.group(1).strip().title();days=int(days_match.group(1)) if days_match else 3
   people=int(people_match.group(1)) if people_match else 2
   budget=int(budget_match.group(1).replace(',','')) if budget_match else 15000
   if not 1<=days<=30 or not 1<=people<=30 or budget<=0:return 'Please use 1–30 days, 1–30 travelers and a positive budget.',trip
   start=date.today()+timedelta(days=7)
   origin=trip['inputs'].get('origin','Your city') if trip else 'Your city'
   p=generate_trip({'origin':origin,'destination':dest,'start':start,'end':start+timedelta(days=days-1),'travelers':people,'budget':budget,'style':'Budget','interests':[],'transport':'Train','accommodation':'Hostel'})
   return f'Created {days}-day trip to {dest} for {people} travelers. Estimated total ₹{p["total"]:,} against ₹{budget:,} budget. Open Trip Details to review.',p
 if not trip:return 'Create or load a trip first, or ask: Plan a 3-day trip to Goa for 2 people under ₹15,000.',trip
 if any(x in q for x in ('cheaper','save money','optimize','reduce budget')):
  p=optimize_trip(trip)
  return f'Applied illustrative budget optimization: ₹{trip["total"]:,} → ₹{p["total"]:,}; estimated savings ₹{trip["total"]-p["total"]:,}.',p
 if any(x in q for x in ('add one more day','add a day','extend by one day')):
  p=add_day(trip);return f'Added a day. Your itinerary now has {p["days"]} days; costs recalculated.',p
 if any(x in q for x in ('compare','comparison')) and any(x in q for x in ('flight','train','bus','car','transport')):
  return 'Illustrative transport comparison: '+', '.join(f'{x["mode"]}: ₹{x["estimated_roundtrip_inr"]:,} for your group ({x["convenience"]} convenience)' for x in transport_planner(trip))+'. Actual times and fares are not verified.',trip
 if re.search(r'\b(?:change|switch|use)\s+(?:transport\s+to\s+)?(flight|train|bus|car)\b',q):
  mode=re.search(r'\b(flight|train|bus|car)\b',q).group(1).title()
  inputs=trip['inputs'].copy();inputs['transport']=mode
  inputs['start']=date.fromisoformat(inputs['start']);inputs['end']=date.fromisoformat(inputs['end'])
  p=generate_trip(inputs)
  for i,old in enumerate(trip['itinerary']):
   for field in ('morning','afternoon','evening','food'):p['itinerary'][i][field]=old[field]
  return f'Changed transport to {mode}. Estimated total ₹{p["total"]:,} (illustrative).',p
 if 'packing' in q:return 'Packing list: '+', '.join(v for items in packing_list(trip).values() for v in items),trip
 if any(x in q for x in ('replace hotel','change hotel','cheaper hotel')):
  p=change_accommodation(trip,'Budget hotel');return 'Updated accommodation preference to Budget hotel. View hotel options in Trip Details; availability is not verified.',p
 if any(x in q for x in ('add a beach','add beach')):
  beach=next((x for x in trip['places'] if 'beach' in x.lower()),None)
  if beach:return f'Added {beach} to day 1 afternoon.',add_attraction(trip,beach)
  return 'No beach is included in this destination’s offline sample data.',trip
 if 'replace afternoon' in q:
  new=next((x for x in trip['places'] if x!=trip['itinerary'][0]['afternoon']),trip['itinerary'][0]['afternoon'])
  return f'Replaced day 1 afternoon with {new}.',add_attraction(trip,new)
 if 'vegetarian' in q or 'restaurant' in q or 'food' in q:
  food=restaurant_recommender(trip,'Vegetarian' if 'vegetarian' in q else 'Any')
  return 'Local food ideas (not verified restaurant listings): '+', '.join(x['dish'] for x in food),trip
 if 'hotel' in q or 'accommodation' in q or 'guesthouse' in q:return 'Illustrative accommodation options: '+', '.join(f'{x["name"]} ₹{x["nightly_inr"]}/night' for x in hotel_recommender(trip)),trip
 if any(x in q for x in ('rain','indoor','weather','forecast')):
  advice=weather_advisor(trip)
  return advice['status']+'. '+ ' '.join(advice['tips']),trip
 if 'route' in q:
  r=route_optimizer(trip);return 'Suggested visit order: '+(' → '.join(x['name'] for x in r['points']) if r['points'] else 'No coordinates available')+'. Route is illustrative, not verified driving directions.',trip
 if any(x in q for x in ('compare','comparison')) and any(x in q for x in ('flight','train','bus','car','transport')):
  return 'Illustrative transport comparison: '+', '.join(f'{x["mode"]}: ₹{x["estimated_roundtrip_inr"]:,} for your group ({x["convenience"]} convenience)' for x in transport_planner(trip))+'. Actual times and fares are not verified.',trip
 if 'transport' in q:return 'Illustrative round-trip options: '+', '.join(f'{x["mode"]} ₹{x["estimated_roundtrip_inr"]:,}' for x in transport_planner(trip)),trip
 if any(x in q for x in ('attraction','visit','places','day 2','second day','day 3','third day')):
  m=re.search(r'day\s*(\d+)',q)
  n=int(m.group(1)) if m else (2 if 'second day' in q else 3 if 'third day' in q else None)
  if n and 1<=n<=trip['days']:
   d=trip['itinerary'][n-1];return f'Day {n}: {d["morning"]}, {d["afternoon"]}, {d["evening"]}.',trip
  return 'Attractions: '+', '.join(x['name'] for x in attraction_recommender(trip)),trip
 if GEMINI_API_KEY:
  try:
   from google import genai
   client=genai.Client(api_key=GEMINI_API_KEY)
   r=client.models.generate_content(model='gemini-2.5-flash',contents=f'You are TripWise travel assistant. Never assert live prices, hotel availability, weather or verified routes. Trip: {str(trip)[:10000]}\nQuestion: {message}')
   if r.text:return r.text,trip
  except Exception:pass
 return 'I could not identify a supported trip action from that question. You can ask for attractions, rainy-day activities, transport comparison, hotels, restaurants, packing, routes, or a change to your current itinerary. For open-ended questions, check the Gemini connection in Settings.',trip
