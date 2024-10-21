from random import randint
from datetime import date, datetime, time
from llama_index.core.tools import QueryEngineTool, FunctionTool, ToolMetadata
from ai_assistant.rags import TravelGuideRAG
from ai_assistant.prompts import travel_guide_qa_tpl, travel_guide_description
from ai_assistant.config import get_agent_settings
from ai_assistant.models import (
    TripReservation,
    TripType,
    HotelReservation,
    RestaurantReservation,
)
from ai_assistant.utils import save_reservation
from datetime import datetime
import json
from datetime import datetime
from ai_assistant.utils import load_trip_data

def parse_date(date_str: str) -> date:
    """
    Parses a date string in various common formats and converts it to a date object.
    Supported formats:
    - DD/MM/YYYY
    - MM-DD-YYYY
    - YYYY/MM/DD
    - YYYY-MM-DD (ISO format)
    """
    for fmt in ("%d/%m/%Y", "%m-%d-%Y", "%Y/%m/%d", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    raise ValueError("Invalid date format. Please provide the date in one of the following formats: DD/MM/YYYY, MM-DD-YYYY, YYYY/MM/DD, or YYYY-MM-DD.")

def parse_datetime(datetime_str: str) -> datetime:
    """
    Parses a datetime string in various common formats and converts it to a datetime object.
    Supported formats:
    - DD/MM/YYYY HH:MM
    - MM-DD-YYYY HH:MM
    - YYYY/MM/DD HH:MM
    - YYYY-MM-DDTHH:MM:SS (ISO format)
    """
    for fmt in ("%d/%m/%Y %H:%M", "%m-%d-%Y %H:%M", "%Y/%m/%d %H:%M", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(datetime_str, fmt)
        except ValueError:
            continue
    raise ValueError("Invalid datetime format. Please provide the datetime in one of the following formats: DD/MM/YYYY HH:MM, MM-DD-YYYY HH:MM, YYYY/MM/DD HH:MM, or YYYY-MM-DDTHH:MM:SS.")




SETTINGS = get_agent_settings()

travel_guide_tool = QueryEngineTool(
    query_engine=TravelGuideRAG(
        store_path=SETTINGS.travel_guide_store_path,
        data_dir=SETTINGS.travel_guide_data_path,
        qa_prompt_tpl=travel_guide_qa_tpl,
    ).get_query_engine(),
    metadata=ToolMetadata(
        name="travel_guide", description=travel_guide_description, return_direct=False
    ),
)


# Tool functions
def reserve_flight(date_str: str, departure: str, destination: str) -> TripReservation:
    """
    Reserve a flight given the date, departure location, and destination.
    This function creates a `TripReservation` object for a flight and saves it to the reservation log.
    Parameters:
    - date_str (str): The date of the flight (flexible format: DD/MM/YYYY, MM-DD-YYYY, YYYY/MM/DD, or YYYY-MM-DD).
    - departure (str): The city where the flight will depart.
    - destination (str): The destination city of the flight.
    Returns:
    - TripReservation: The reservation details including trip type, date, departure, destination, and cost.
    """
    try:
        reservation_date = parse_date(date_str)
    except ValueError as e:
        raise ValueError(str(e))
    
    print(f"Making flight reservation from {departure} to {destination} on date: {reservation_date}")
    reservation = TripReservation(
        trip_type=TripType.flight,
        departure=departure,
        destination=destination,
        date=reservation_date,
        cost=randint(200, 700),
    )

    save_reservation(reservation)
    return reservation


def reserve_hotel(checkin_date: str, checkout_date: str, hotel_name: str, city: str) -> HotelReservation:
    """
    Reserve a hotel given the check-in date, check-out date, hotel name, and city.
    This function creates a `HotelReservation` object and saves it to the reservation log.
    Parameters:
    - checkin_date (str): The check-in date (flexible format: DD/MM/YYYY, MM-DD-YYYY, YYYY/MM/DD, or YYYY-MM-DD).
    - checkout_date (str): The check-out date (flexible format: DD/MM/YYYY, MM-DD-YYYY, YYYY/MM/DD, or YYYY-MM-DD).
    - hotel_name (str): The name of the hotel.
    - city (str): The city where the hotel is located.
    Returns:
    - HotelReservation: The reservation details including check-in, check-out dates, hotel name, city, and cost.
    """
    try:
        checkin = parse_date(checkin_date)
        checkout = parse_date(checkout_date)
    except ValueError as e:
        raise ValueError(str(e))
    
    print(f"Making hotel reservation at {hotel_name} in {city} from {checkin} to {checkout}")
    reservation = HotelReservation(
        checkin_date=checkin,
        checkout_date=checkout,
        hotel_name=hotel_name,
        city=city,
        cost=randint(300, 1500),
    )

    save_reservation(reservation)
    return reservation



def reserve_bus(date_str: str, departure: str, destination: str) -> TripReservation:
    """
    Reserve a bus ticket given the date, departure location, and destination.
    This function creates a `TripReservation` object for a bus and saves it to the reservation log.
    Parameters:
    - date_str (str): The date of the bus trip (flexible format: DD/MM/YYYY, MM-DD-YYYY, YYYY/MM/DD, or YYYY-MM-DD).
    - departure (str): The departure city.
    - destination (str): The destination city.
    Returns:
    - TripReservation: The reservation details including trip type, date, departure, destination, and cost.
    """
    try:
        reservation_date = parse_date(date_str)
    except ValueError as e:
        raise ValueError(str(e))
    
    print(f"Making bus reservation from {departure} to {destination} on date: {reservation_date}")
    reservation = TripReservation(
        trip_type=TripType.bus,
        departure=departure,
        destination=destination,
        date=reservation_date,
        cost=randint(50, 300),
    )

    save_reservation(reservation)
    return reservation



def reserve_restaurant(reservation_time: str, restaurant: str, city: str, dish: str = "not specified") -> RestaurantReservation:
    """
    Reserve a table at a restaurant given the reservation time, restaurant name, city, and optional dish.
    This function creates a `RestaurantReservation` object and saves it to the reservation log.
    Parameters:
    - reservation_time (str): The time of the reservation (flexible format: DD/MM/YYYY HH:MM, MM-DD-YYYY HH:MM, YYYY/MM/DD HH:MM, or YYYY-MM-DDTHH:MM:SS).
    - restaurant (str): The name of the restaurant.
    - city (str): The city where the restaurant is located.
    - dish (str, optional): The dish to order. Defaults to 'not specified'.
    Returns:
    - RestaurantReservation: The reservation details including time, restaurant name, city, dish, and cost.
    """
    try:
        reservation_datetime = parse_datetime(reservation_time)
    except ValueError as e:
        raise ValueError(str(e))
    
    print(f"Making restaurant reservation at {restaurant} in {city} at {reservation_datetime}")
    reservation = RestaurantReservation(
        reservation_time=reservation_datetime,
        restaurant=restaurant,
        city=city,
        dish=dish,
        cost=randint(20, 200),
    )

    save_reservation(reservation)
    return reservation




def generate_trip_summary() -> str:
    """
    Generate a detailed summary of the trip based on activities recorded in the trip log (trip.json).
    This function reads the trip data, organizes activities by date and place, and returns a detailed report.
    Returns:
    - str: A formatted report of the trip activities, including all booked activities organized by place and date,
           total budget summary, and comments on the places and activities.
    """
    try:
        trip_data = load_trip_data()
        organized_data = {}

        for entry in trip_data:
            city = entry.get("destination") if entry.get("trip_type") in ["FLIGHT", "BUS"] else entry.get("city")
            date_str = entry.get("date") or entry.get("checkin_date") or entry.get("reservation_time")

            if not city or not date_str:
                continue

            date_obj = datetime.fromisoformat(date_str.split("T")[0])
            formatted_date = date_obj.strftime("%Y-%m-%d")

            if city not in organized_data:
                organized_data[city] = {}

            if formatted_date not in organized_data[city]:
                organized_data[city][formatted_date] = []

            organized_data[city][formatted_date].append(entry)

        report = "Trip Summary Report:\n"
        total_cost = 0

        for city, dates in organized_data.items():
            report += f"\nCity: {city}\n"
            for date, activities in dates.items():
                report += f"  Date: {date}\n"
                for activity in activities:
                    activity_type = activity.get("trip_type") or activity.get("reservation_type")
                    activity_details = f"    - {activity_type}: "

                    if activity_type in ["FLIGHT", "BUS"]:
                        activity_details += f"from {activity.get('departure')} to {activity.get('destination')}, Cost: {activity.get('cost')} Bs."
                    elif activity_type == "HotelReservation":
                        activity_details += f"Hotel: {activity.get('hotel_name')}, Check-in: {activity.get('checkin_date')}, Check-out: {activity.get('checkout_date')}, Cost: {activity.get('cost')} Bs."
                    elif activity_type == "RestaurantReservation":
                        activity_details += f"Restaurant: {activity.get('restaurant')}, Reservation Time: {activity.get('reservation_time')}, Dish: {activity.get('dish')}, Cost: {activity.get('cost')} Bs."

                    report += activity_details + "\n"
                    total_cost += activity.get("cost", 0)

        report += f"\nTotal Trip Cost: {total_cost} Bs.\n"
        return report

    except Exception as e:
        return f"Error generating trip summary: {str(e)}"


trip_summary_tool = FunctionTool.from_defaults(fn=generate_trip_summary, return_direct=True)
flight_tool = FunctionTool.from_defaults(fn=reserve_flight, return_direct=True)
hotel_tool = FunctionTool.from_defaults(fn=reserve_hotel, return_direct=True)
bus_tool = FunctionTool.from_defaults(fn=reserve_bus, return_direct=True)
restaurant_tool = FunctionTool.from_defaults(fn=reserve_restaurant, return_direct=True)
