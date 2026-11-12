# ✈️ TravelMate AI

**Your AI-powered travel assistant.**

TravelMate AI is a Python-based travel assistant powered by a local LLM using Ollama and LangChain. It uses custom tools and external APIs to help users with travel-related information, currency conversions, weather updates, flight searches, and budget calculations.

## Features

- 🌦️ **Weather Updates:** Retrieve current weather information for destination cities.
- ✈️ **Flight Search:** Search flight schedules using airport codes and travel dates.
- 💱 **Currency Conversion:** Convert currencies using live exchange rates from ExchangeRate-API.
- 🧮 **Travel Calculator:** Calculate travel expenses and budgets.
- 🤖 **AI Agent:** Uses LangChain to decide when to call available tools.
- 🖥️ **Local LLM:** Runs using Ollama with the Qwen 2.5 3B model.
- 📄 **Structured Responses:** Returns responses in a consistent JSON format.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| LangChain | AI agent and tool integration |
| Ollama | Local LLM execution |
| Qwen 2.5 3B | Language model |
| Requests | API communication |
| python-dotenv | Environment variable management |
| WeatherAPI | Weather information |
| Aviationstack | Flight information |
| ExchangeRate-API | Currency conversion |

## Project Structure

```text
TravelMate-AI/
│
├── main.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Getting Started

### 1. Clone the repository

```bash
git clone YOUR_REPOSITORY_URL
cd TravelMate-AI
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Ollama and download the model

Install [Ollama](https://ollama.com/) and run:

```bash
ollama pull qwen2.5:3b
```

### 5. Configure API keys

Create a `.env` file in the project directory:

```env
WEATHER_API_KEY=your_weatherapi_key
AVIATIONSTACK_API_KEY=your_aviationstack_key
EXCHANGERATE_API_KEY=your_exchangerate_api_key
```

Obtain API keys from:

- [WeatherAPI](https://www.weatherapi.com/)
- [Aviationstack](https://aviationstack.com/)
- [ExchangeRate-API](https://www.exchangerate-api.com/)

### 6. Run TravelMate

```bash
python main.py
```

## Example Usage

```text
✈️ TravelMate AI is ready!
Type 'exit' to quit.

You: Convert 20 USD to PKR

TravelMate:
20 USD = 5,539.64 PKR

You: What's the weather in Dubai?

TravelMate:
[Weather information retrieved from WeatherAPI]

You: Calculate my travel budget: 500 + 250 + 150

TravelMate:
900
```

*Example outputs are illustrative; actual results depend on API responses and agent execution.*

## Security

- Keep API keys inside your local `.env` file.
- Never commit `.env` to GitHub.
- Use `.env.example` to document required environment variables.
- The `.gitignore` file excludes secrets and virtual environments.

## Future Improvements

- Interactive web interface.
- Better conversation memory.
- More travel-related tools.
- Improved error handling and tool-call reliability.
- Travel itinerary generation.
- More structured and user-friendly responses.

## License

This project is available under the MIT License. Add a `LICENSE` file if you intend to distribute it under that license.

---

**Developed by Muhammad Abdullah**