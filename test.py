from tools.tavily_tool import tavily_search
from tools.flight_tool import search_flights

# res = tavily_search("best hotels in Bragança Paulista")
# print(res)

res = search_flights("plan a 7 days Campinas trip from California")
print(res)