from tools.tavily_tool import tavily_search
from tools.flight_tool import search_flights
from backend import run_travel_agent

# res = tavily_search("best hotels in Bragança Paulista")
# print(res)

# res = search_flights("plan a 7 days Campinas trip from California")
# print(res)

user_input = input("Enter travel request: ")

response = run_travel_agent(
    user_input=user_input,
    thread_id="test_user"
)

print("\nFinal Response: \n")
print(response["answer"])
