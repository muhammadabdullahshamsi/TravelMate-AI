
import os
import ast
import operator
import json
import re
import requests

from datetime import date
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain.agents import create_agent

load_dotenv()

# LLM
llm = ChatOllama(
    model="qwen2.5:3b",
    temperature=0
)


AIRPORTS = {
    # Pakistan
    "karachi": "KHI",
    "lahore": "LHE",
    "islamabad": "ISB",
    "peshawar": "PEW",
    "quetta": "UET",
    "multan": "MUX",
    "faisalabad": "LYP",
    "sialkot": "SKT",
    "skardu": "KDU",
    "gwadar": "GWD",
    "sukkur": "SKZ",
    "bahawalpur": "BHV",
    "gilgit": "GIL",
    "turbat": "TUK",

    # Middle East
    "dubai": "DXB",
    "abu dhabi": "AUH",
    "sharjah": "SHJ",
    "doha": "DOH",
    "riyadh": "RUH",
    "jeddah": "JED",
    "makkah": "JED",
    "madinah": "MED",
    "muscat": "MCT",
    "kuwait": "KWI",
    "bahrain": "BAH",
    "amman": "AMM",
    "beirut": "BEY",
    "tel aviv": "TLV",

    # South Asia
    "delhi": "DEL",
    "mumbai": "BOM",
    "bangalore": "BLR",
    "chennai": "MAA",
    "hyderabad india": "HYD",
    "kolkata": "CCU",
    "dhaka": "DAC",
    "chittagong": "CGP",
    "kathmandu": "KTM",
    "colombo": "CMB",
    "male": "MLE",

    # East Asia
    "beijing": "PEK",
    "shanghai": "PVG",
    "guangzhou": "CAN",
    "shenzhen": "SZX",
    "hong kong": "HKG",
    "tokyo": "HND",
    "osaka": "KIX",
    "seoul": "ICN",
    "busan": "PUS",
    "taipei": "TPE",

    # Southeast Asia
    "bangkok": "BKK",
    "phuket": "HKT",
    "singapore": "SIN",
    "kuala lumpur": "KUL",
    "jakarta": "CGK",
    "bali": "DPS",
    "manila": "MNL",
    "cebu": "CEB",
    "hanoi": "HAN",
    "ho chi minh city": "SGN",
    "phnom penh": "PNH",

    # Europe
    "london": "LHR",
    "paris": "CDG",
    "frankfurt": "FRA",
    "munich": "MUC",
    "berlin": "BER",
    "amsterdam": "AMS",
    "brussels": "BRU",
    "zurich": "ZRH",
    "geneva": "GVA",
    "rome": "FCO",
    "milan": "MXP",
    "venice": "VCE",
    "madrid": "MAD",
    "barcelona": "BCN",
    "lisbon": "LIS",
    "vienna": "VIE",
    "prague": "PRG",
    "budapest": "BUD",
    "warsaw": "WAW",
    "athens": "ATH",
    "istanbul": "IST",
    "moscow": "SVO",
    "copenhagen": "CPH",
    "stockholm": "ARN",
    "oslo": "OSL",
    "helsinki": "HEL",

    # North America
    "new york": "JFK",
    "los angeles": "LAX",
    "chicago": "ORD",
    "san francisco": "SFO",
    "washington": "IAD",
    "boston": "BOS",
    "miami": "MIA",
    "dallas": "DFW",
    "houston": "IAH",
    "seattle": "SEA",
    "las vegas": "LAS",
    "toronto": "YYZ",
    "vancouver": "YVR",
    "montreal": "YUL",
    "calgary": "YYC",
    "mexico city": "MEX",

    # Africa
    "cairo": "CAI",
    "johannesburg": "JNB",
    "cape town": "CPT",
    "nairobi": "NBO",
    "lagos": "LOS",
    "addis ababa": "ADD",
    "casablanca": "CMN",
    "tunis": "TUN",
    "algiers": "ALG",

    # Oceania
    "sydney": "SYD",
    "melbourne": "MEL",
    "brisbane": "BNE",
    "perth": "PER",
    "auckland": "AKL",
    "wellington": "WLG",
    "christchurch": "CHC",
}


def get_airport_code(city):
    city = city.strip()
    return AIRPORTS.get(city.lower(), city.upper())


# Weather Tool
@tool
def weather(city: str):
    """Get real-time weather information for a destination city."""

    url = "https://api.weatherapi.com/v1/current.json"

    params = {
        "key": os.getenv("WEATHER_API_KEY"),
        "q": city
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        data = response.json()

        if response.status_code != 200:
            return json.dumps({
                "error": data.get("error", {}).get("message")
            })

        return json.dumps({
            "city": data["location"]["name"],
            "temperature": data["current"]["temp_c"],
            "condition": data["current"]["condition"]["text"],
            "humidity": data["current"]["humidity"]
        })

    except requests.RequestException:
        return json.dumps({"error": "Weather service unavailable"})


# Flight Search Tool
@tool
def search_flights(origin: str, destination: str, travel_date: str):
    """Search scheduled flights between two cities on a specific date.
    Use city names or three-letter airport IATA codes.
    Date format must be YYYY-MM-DD.
    """

    api_key = os.getenv("AVIATIONSTACK_API_KEY")

    if not api_key:
        return json.dumps({"error": "Aviationstack API key missing"})

    try:
        flight_date = date.fromisoformat(travel_date)

        if flight_date < date.today():
            return json.dumps({
                "error": "Past flight searches are not supported by this tool."
            })

        dep = get_airport_code(origin)
        arr = get_airport_code(destination)

        if len(dep) != 3 or len(arr) != 3:
            return json.dumps({
                "error": "Please provide valid three-letter airport codes."
            })

        if flight_date == date.today():
            url = "https://api.aviationstack.com/v1/flights"

            params = {
                "access_key": api_key,
                "dep_iata": dep,
                "arr_iata": arr,
                "flight_date": travel_date,
                "limit": 10
            }

            future = False

        else:
            url = "https://api.aviationstack.com/v1/flightsFuture"

            params = {
                "access_key": api_key,
                "iataCode": dep,
                "type": "departure",
                "date": travel_date
            }

            future = True

        response = requests.get(url, params=params, timeout=20)
        data = response.json()

        if "error" in data:
            return json.dumps({
                "error": data["error"].get("info", "Flight API error")
            })

        flights = data.get("data", [])

        if future:
            flights = [
                f for f in flights
                if f.get("arrival", {}).get("iataCode") == arr
            ]

        results = []

        for f in flights[:10]:
            if future:
                results.append({
                    "airline": f.get("airline", {}).get("name"),
                    "flight": f.get("flight", {}).get("iataNumber"),
                    "departure": f.get("departure", {}).get("scheduledTime"),
                    "arrival": f.get("arrival", {}).get("scheduledTime"),
                    "status": "Scheduled"
                })
            else:
                results.append({
                    "airline": f.get("airline", {}).get("name"),
                    "flight": f.get("flight", {}).get("iata"),
                    "departure": f.get("departure", {}).get("scheduled"),
                    "arrival": f.get("arrival", {}).get("scheduled"),
                    "status": f.get("flight_status")
                })

        return json.dumps({
            "origin": dep,
            "destination": arr,
            "date": travel_date,
            "flights": results,
            "message": "No matching flights found." if not results else "Flight data retrieved."
        })

    except ValueError:
        return json.dumps({"error": "Invalid date. Use YYYY-MM-DD."})

    except requests.RequestException:
        return json.dumps({"error": "Flight service unavailable."})


# Calculator Tool
@tool
def calculator(expression: str):
    """Calculate mathematical expressions for travel budgets and expenses."""

    operations = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Mod: operator.mod
    }

    def calculate(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value

        if isinstance(node, ast.BinOp) and type(node.op) in operations:
            return operations[type(node.op)](
                calculate(node.left),
                calculate(node.right)
            )

        if isinstance(node, ast.UnaryOp):
            if isinstance(node.op, ast.USub):
                return -calculate(node.operand)

        raise ValueError("Invalid expression")

    try:
        result = calculate(ast.parse(expression, mode="eval").body)

        return json.dumps({
            "expression": expression,
            "result": result
        })

    except Exception:
        return json.dumps({"error": "Invalid calculation"})



# Currency Exchange Tool
@tool
def currency_exchange(from_currency: str, to_currency: str, amount: float):
    """Convert an amount between two currencies using ExchangeRate-API."""

    api_key = os.getenv("EXCHANGERATE_API_KEY")

    if not api_key:
        return json.dumps({"error": "EXCHANGERATE_API_KEY is missing."})

    from_currency = from_currency.strip().upper()
    to_currency = to_currency.strip().upper()

    if not re.fullmatch(r"[A-Z]{3}", from_currency):
        return json.dumps({"error": "Invalid source currency code."})

    if not re.fullmatch(r"[A-Z]{3}", to_currency):
        return json.dumps({"error": "Invalid target currency code."})

    if amount <= 0:
        return json.dumps({"error": "Amount must be greater than zero."})

    url = (
        f"https://v6.exchangerate-api.com/v6/"
        f"{api_key}/pair/{from_currency}/{to_currency}/{amount}"
    )

    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()

        if data.get("result") != "success":
            return json.dumps({
                "error": data.get("error-type", "Currency conversion failed.")
            })

        return json.dumps({
            "from": data["base_code"],
            "to": data["target_code"],
            "amount": amount,
            "rate": data["conversion_rate"],
            "converted_amount": data["conversion_result"],
            "last_updated": data.get("time_last_update_utc")
        })

    except requests.RequestException as e:
        return json.dumps({"error": f"Request failed: {str(e)}"})

    except (ValueError, KeyError):
        return json.dumps({"error": "Invalid response from ExchangeRate-API."})


# Travel Agent
agent = create_agent(
    model=llm,
    tools=[
        weather,
        search_flights,
        calculator,
        currency_exchange
    ],
    
system_prompt = """
You are TravelMate, an AI travel assistant.

Your responsibilities:

1. Help users plan trips and itineraries.
2. Use the weather tool for real-time destination weather.
3. Use search_flights for flight schedules and status.
4. Use calculator for travel expenses and budgets.
5. Use currency_exchange for live currency conversions.
6. Answer general travel questions using your knowledge.
7. Ask for missing information when necessary.

IMPORTANT RULES:

- Never invent flight information.
- Never invent ticket prices or booking availability.
- Clearly distinguish estimated costs from verified prices.
- Do not claim that a flight is bookable.
- Use actual tool results for live information.
- Do not call tools unnecessarily.

CURRENCY CONVERSION RULES:

- ALWAYS call currency_exchange when the user requests a currency conversion.
- Extract the amount, source currency, and target currency.
- Example: "Convert 20 USD to PKR"
  means:
  from_currency = "USD"
  to_currency = "PKR"
  amount = 20
- Do not ask the user to repeat information already provided.
- If the amount or either currency is missing, ask for the missing information.
- Use the actual tool response to provide the conversion.
- If the tool returns an error, explain the actual error.
- Never invent exchange rates or converted amounts.

TOOL RULES:

- Call the appropriate tool when live information is required.
- Wait for the tool response before answering.
- Do not pretend a tool was successful if it returned an error.
- Include the tools actually used in tools_used.

RESPONSE FORMAT:

Always return valid JSON with exactly these keys:

{
    "destination": "",
    "tools_used": [],
    "results": {},
    "recommendations": [],
    "answer": ""
}
"""

)


# Chat Interface
print("\n✈️ TravelMate AI is ready!")
print("Type 'exit' to quit.")

while True:

    question = input("\nYou: ")

    if question.lower() == "exit":
        break

    response = agent.invoke({
        "messages": [
            {"role": "user", "content": question}
        ]
    })

    print("\nTravelMate:")
    print(response["messages"][-1].content)
