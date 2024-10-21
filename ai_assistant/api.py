from fastapi import FastAPI, Depends, Query
from llama_index.core.agent import ReActAgent
from ai_assistant.agent import TravelAgent
from ai_assistant.models import AgentAPIResponse
from ai_assistant.tools import (
    reserve_flight,
    reserve_bus,
    reserve_hotel,
    reserve_restaurant
)



def get_agent() -> ReActAgent:
    return TravelAgent().get_agent()


app = FastAPI(title="AI Agent API")


# Recommendations
@app.get("/recommendations/cities")
def recommend_cities(
    notes: list[str] = Query(...), agent: ReActAgent = Depends(get_agent)
):
    prompt = f"recommend cities in bolivia with the following notes: {notes}"
    return AgentAPIResponse(status="OK", agent_response=str(agent.chat(prompt)))

@app.get("/recommendations/hotels")
def recommend_hotels(
    city: str, notes: list[str] = Query(None), agent: ReActAgent = Depends(get_agent)
    ):
    prompt = f"recommend hotels in {city} with the following notes: {notes or 'no specific notes'}"
    return AgentAPIResponse(status="OK", agent_response=str(agent.chat(prompt)))

@app.get("/recommendations/activities")
def recommend_activities(
    city: str, notes: list[str] = Query(None), agent: ReActAgent = Depends(get_agent)
    ):
    prompt = f"recommend activities in {city} with the following notes: {notes or 'no specific notes'}"
    return AgentAPIResponse(status="OK", agent_response=str(agent.chat(prompt)))


# Reservations
@app.post("/reservations/flight")
def book_flight(date: str, departure: str, destination: str):
    reservation = reserve_flight(date, departure, destination)
    return {
        "status": "OK",
        "reservation": reservation.dict()
    }

@app.post("/reservations/bus")
def book_bus(date: str, departure: str, destination: str):
    reservation = reserve_bus(date, departure, destination)
    return {
        "status": "OK",
        "reservation": reservation.dict()
        }


@app.post("/reservations/hotel")
def book_hotel(checkin_date: str, checkout_date: str, hotel_name: str, city: str):
    reservation = reserve_hotel(checkin_date, checkout_date, hotel_name, city)
    return {
        "status": "OK",
        "reservation": reservation.dict()
    }

@app.post("/reservations/restaurant")
def book_restaurant(reservation_time: str, restaurant: str, city: str, dish: str = "not specified"):
    reservation = reserve_restaurant(reservation_time, restaurant, city, dish)
    return {
        "status": "OK",
        "reservation": reservation.dict()
    }


@app.get("/report")
def generate_trip_report(agent: ReActAgent = Depends(get_agent)):
    prompt = "Generate a detailed trip summary based on the activities recorded in the trip log."
    response = agent.chat(prompt)
    return AgentAPIResponse(status="OK", agent_response=str(response))