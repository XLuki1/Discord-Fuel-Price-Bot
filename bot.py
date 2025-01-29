import discord
from discord.ext import commands
import requests

# Bot-Einstellungen
TOKEN = "DISCORD BOT TOKEN"
TANKERKOENIG_API_KEY = "API KEY"

# Erstelle den Bot
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="&", intents=intents)

# Funktion zum Abrufen der Spritpreise
def get_fuel_prices(postal_code, fuel_type="e5"):
    url = f"https://creativecommons.tankerkoenig.de/json/list.php"
    params = {
        "lat": 0,
        "lng": 0,
        "rad": 3,  # Radius auf 3 km gesetzt
        "type": fuel_type,
        "apikey": TANKERKOENIG_API_KEY,
        "sort": "price"
    }
    headers = {"accept": "application/json"}

    # Geocodierung der PLZ
    geocode_url = f"https://nominatim.openstreetmap.org/search?postalcode={postal_code}&country=de&format=json"
    
    # User-Agent setzen
    headers = {
        "User-Agent": "DeinBotName/1.0 (https://deine-website.com; Kontakt: deine-email@example.com)"
    }

    print(f"Geocode URL: {geocode_url}")  
    response = requests.get(geocode_url, headers=headers)  
    
    if response.status_code == 200 and response.json():
        location = response.json()[0]
        params["lat"] = location["lat"]
        params["lng"] = location["lon"]
        print(f"Koordinaten für PLZ {postal_code}: {location['lat']}, {location['lon']}")  #
    else:
        print(f"Geocode Fehler: {response.status_code}")  
        return f"Postleitzahl {postal_code} nicht gefunden."

    # Anfrage an die Tankerkönig-API
    print(f"TankerKoenig URL: {url} mit Parametern: {params}")  # Debug-Ausgabe für die Tankerkönig-API-Anfrage
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"API Antwort: {data}")  # API Antwort-Debugging
        if data.get("ok"):
            stations = data.get("stations", [])
            if not stations:
                return f"Keine Tankstellen im Umkreis gefunden."

            # Formatierte Ausgabe für die Tankstellen 
            result = "🚗 **Spritpreise in deinem Umkreis (3 km):**\n\n"
            for station in stations:
                address = f"{station['street']} {station['houseNumber']}, {station['place']}" if 'street' in station else "Adresse nicht verfügbar"
                result += (
                    f"**{station['name']}** ({station['brand']})\n"
                    f"📍 Adresse: {address}\n"
                    f"⛽ Preis: {station['price']} €/L\n\n"  
                )
            return result
        else:
            return "Fehler bei der Anfrage an die Tankerkönig-API."
    else:
        print(f"TankerKoenig API Fehler: {response.status_code}")  # Fehlerausgabe bei API-Anfrage
        return "Fehler bei der Verbindung zur Tankerkönig-API."


# Event: Bot ist bereit
@bot.event
async def on_ready():
    print(f"{bot.user} ist bereit und online!")

# Command: Spritpreise abfragen 
@bot.command()
async def spritpreise(ctx, plz: str, fuel_type: str = "e5"):
    """Gibt die Spritpreise für eine Postleitzahl und einen Treibstofftyp aus (e5, e10, diesel)."""
    await ctx.send("Hole die aktuellen Spritpreise... Bitte einen Moment Geduld.")
    prices = get_fuel_prices(plz, fuel_type)
    await ctx.send(prices)

# Abkürzung des Commands: sp für Spritpreise
@bot.command()
async def sp(ctx, plz: str, fuel_type: str = "e5"):
    """Abkürzung für den Spritpreise-Befehl."""
    await spritpreise(ctx, plz, fuel_type)  # Verweist auf den ursprünglichen Befehl

# Bot starten
bot.run(TOKEN)
