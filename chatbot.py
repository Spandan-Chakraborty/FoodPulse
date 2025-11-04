import os
import requests
import time
from difflib import SequenceMatcher
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from the .env file
load_dotenv()

class FoodPulseChatbot:
    def __init__(self):
        # -------------------------------
        # Step 1: Secure API Configuration
        # -------------------------------
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        if not self.GROQ_API_KEY or self.GROQ_API_KEY == "YOUR_GROQ_API_KEY_HERE":
            raise ValueError("ERROR: Groq API Key not found in .env file!")

        self.GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

        # Rate limiting
        self.last_request_time = 0
        self.rate_limit_delay = 1.0  # seconds between requests
        self.request_count = 0
        self.daily_limit = 100

        # Conversation memory (last 6 exchanges)
        self.conversation_history = []
        self.max_history_length = 6

        # User session
        self.session_start = datetime.now()

        # -------------------------------
        # Step 2: Enhanced FAQ Data with Categories
        # -------------------------------
        self.faq_categories = {
            "platform_overview": {
                "what is food pulse": {
                    "answer": "Food Pulse is a platform that bridges the gap between restaurants with surplus food (raw or cooked) and NGOs working to feed people in need. It ensures that good food never goes to waste and reaches those who truly need it.",
                    "keywords": ["what is", "explain", "tell me about", "purpose"]
                },
                "how does food pulse work": {
                    "answer": "Restaurants list their available surplus food on the platform. Once listed, NGOs can view these items and request to collect them. All transactions are verified and approved by an admin to ensure safety, quality, and fair distribution.",
                    "keywords": ["how does it work", "process", "workflow", "operation"]
                },
                "mission and vision": {
                    "answer": "Our mission is to eliminate food waste and hunger by creating an efficient bridge between food donors and organizations serving communities in need. We envision a world where no edible food is wasted while people go hungry.",
                    "keywords": ["mission", "vision", "goal", "purpose"]
                }
            },
            "registration": {
                "who can register on food pulse": {
                    "answer": "Currently, registered NGOs and licensed restaurants or food providers can join the platform. Both parties need to go through a quick verification and approval process by the admin before they can start using the service.",
                    "keywords": ["who can join", "registration", "sign up", "eligible"]
                },
                "how to register as a restaurant": {
                    "answer": "Restaurants can register on our website by providing business details, license information, and contact details. After submission, our admin team verifies the details and approves the account typically within 24-48 hours.",
                    "keywords": ["restaurant registration", "join as restaurant", "food provider signup"]
                },
                "how to register as an ngo": {
                    "answer": "NGOs can register by providing their registration certificate, area of operation, and beneficiary details. Our team verifies the NGO credentials before activating the account for food requests.",
                    "keywords": ["ngo registration", "join as ngo", "charity signup"]
                }
            },
            "restaurant_operations": {
                "how can restaurants list their extra food": {
                    "answer": "After logging into their dashboard, restaurants can add details such as food type (raw/cooked), quantity/weight, best-before time, and pickup location. Once submitted, the admin reviews and approves the listing before it becomes visible to NGOs.",
                    "keywords": ["list food", "add surplus", "donate food", "post listing"]
                },
                "what types of food can be donated": {
                    "answer": "Both raw ingredients and cooked meals can be donated, provided they are within safe consumption period. Perishable items, non-vegetarian food, and prepared meals are all acceptable with proper storage instructions.",
                    "keywords": ["food types", "what can be donated", "acceptable food"]
                },
                "is there a cost for restaurants": {
                    "answer": "No, Food Pulse is completely free for restaurants to list and donate surplus food. There are no listing fees, transaction charges, or subscription costs.",
                    "keywords": ["cost", "fee", "payment", "charges"]
                }
            },
            "ngo_operations": {
                "how can ngos request food donations": {
                    "answer": "NGOs can browse approved listings, filter based on their needs, and click 'Request' to claim an item. The restaurant receives a notification, and upon confirmation, pickup or delivery arrangements can be made.",
                    "keywords": ["request food", "how to get food", "claim donation"]
                },
                "what are ngo responsibilities": {
                    "answer": "NGOs are responsible for timely pickup, proper transportation with food safety measures, and distributing food to beneficiaries within safe consumption time. They should also provide basic feedback on the distribution.",
                    "keywords": ["ngo duties", "responsibilities", "requirements"]
                }
            },
            "logistics_safety": {
                "who handles food pickup or transportation": {
                    "answer": "In most cases, NGOs handle the collection of the food from the restaurant. However, Food Pulse may collaborate with logistics partners in the future to support large-scale deliveries.",
                    "keywords": ["pickup", "transportation", "delivery", "logistics"]
                },
                "is the food safety verified before delivery": {
                    "answer": "Yes. Every food listing is reviewed by an admin, and restaurants must comply with basic food safety standards before donation. NGOs are also encouraged to double-check food conditions during pickup.",
                    "keywords": ["food safety", "quality", "verification", "standards"]
                },
                "what are the food safety guidelines": {
                    "answer": "We follow basic food safety protocols: proper storage temperatures, clear labeling of preparation times, hygienic packaging, and adherence to best-before dates. Both restaurants and NGOs receive safety guidelines.",
                    "keywords": ["safety guidelines", "protocols", "standards", "hygiene"]
                }
            },
            "benefits_impact": {
                "what are the benefits for restaurants": {
                    "answer": "Restaurants reduce food waste costs, fulfill CSR objectives, get tax benefits in some regions, enhance brand reputation, and contribute positively to community welfare.",
                    "keywords": ["benefits", "advantages", "why participate", "value"]
                },
                "environmental impact": {
                    "answer": "By diverting surplus food from landfills, we reduce methane emissions, conserve resources used in food production, and promote sustainable consumption patterns in the community.",
                    "keywords": ["environment", "sustainability", "eco-friendly", "green"]
                }
            }
        }

        # -------------------------------
        # Step 3: Enhanced Document Data
        # -------------------------------
        self.document_text = """Food Pulse is an innovative digital platform designed to bridge the gap between restaurants with surplus food and NGOs dedicated to feeding the underprivileged, ensuring that no edible food goes to waste. The platform's mission aligns directly with the United Nations Sustainable Development Goals (SDGs) — particularly SDG 2: Zero Hunger, SDG 12: Responsible Consumption and Production, and SDG 17: Partnerships for the Goals.

The process begins with restaurants registering and undergoing admin verification to ensure authenticity and adherence to basic food safety and hygiene standards. Once approved, they can list surplus food items, specifying details such as type (raw or cooked), quantity, best-before time, and pickup location. Verified NGOs can then browse these listings and request the items they require. Every request passes through an admin approval system to maintain transparency and traceability. After approval, NGOs coordinate with restaurants for food pickup or delivery, minimizing logistical confusion and ensuring safe handling.

Food Pulse's unique admin-mediated model ensures trust, accountability, and compliance throughout the process. Future expansions aim to integrate smart logistics partnerships, AI-based food matching, and real-time donation tracking to enhance efficiency. By transforming surplus into sustenance, Food Pulse promotes social responsibility, community welfare, and environmental sustainability.

Ultimately, Food Pulse is not just a platform — it's a movement towards eradicating hunger, reducing food waste, and fostering collaboration across sectors to build a more equitable and sustainable world."""

        # -------------------------------
        # Step 4: Response Templates
        # -------------------------------
        self.response_templates = {
            "welcome": "🌍 Welcome to Food Pulse Chatbot! I'm here to help you understand how we connect surplus food with people in need.",
            "farewell": "Thank you for using Food Pulse Chatbot! Together we can reduce food waste and fight hunger. 🌱❤️",
            "off_topic": "I specialize in Food Pulse, food donations, and hunger relief topics. How can I help you with these?",
            "rate_limit": "I'm receiving many requests right now. Please wait a moment and try again.",
            "api_error": "I'm having trouble accessing information right now. Please try again in a moment.",
            "daily_limit": "I've reached my daily request limit. Please try again tomorrow or contact support.",
            "fallback": "I'm not sure about that specific detail. Could you try rephrasing or ask about our platform features, registration process, or food safety guidelines?"
        }

    def find_best_faq_match(self, query, threshold=0.65):
        """Enhanced FAQ matching with similarity scoring"""
        query = query.lower().strip()
        best_match = None
        best_score = 0
        best_category = None

        # Flatten all FAQ questions
        all_questions = {}
        for category, questions in self.faq_categories.items():
            for question, data in questions.items():
                all_questions[question] = (data["answer"], category)

        # Check direct matches first
        for question, (answer, category) in all_questions.items():
            if query == question.lower():
                return answer, category, 1.0

        # Check keyword matches
        for question, (answer, category) in all_questions.items():
            data = self.faq_categories[category][question]
            for keyword in data.get("keywords", []):
                if keyword in query:
                    return answer, category, 0.9

        # Check similarity matches
        for question, (answer, category) in all_questions.items():
            score = SequenceMatcher(None, query, question.lower()).ratio()
            if score > best_score and score > threshold:
                best_score = score
                best_match = answer
                best_category = category

        return best_match, best_category, best_score

    def enforce_rate_limit(self):
        """Rate limiting to prevent API abuse"""
        current_time = time.time()

        # Check daily limit
        if self.request_count >= self.daily_limit:
            raise Exception("daily_limit")

        # Enforce delay between requests
        if current_time - self.last_request_time < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - (current_time - self.last_request_time))

        self.last_request_time = time.time()
        self.request_count += 1

    def is_food_pulse_related(self, query):
        """Check if query is related to Food Pulse topics"""
        related_keywords = [
            'food', 'donation', 'restaurant', 'ngo', 'surplus', 'waste', 'hunger',
            'donate', 'leftover', 'charity', 'meal', 'feed', 'hungry', 'poor',
            'distribution', 'logistics', 'safety', 'register', 'sign up', 'list',
            'request', 'pickup', 'delivery', 'volunteer', 'help', 'support'
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in related_keywords)

    def get_conversation_context(self):
        """Build conversation context from history"""
        if not self.conversation_history:
            return ""

        context = "Previous conversation:\n"
        for i, exchange in enumerate(self.conversation_history[-3:], 1):  # Last 3 exchanges
            context += f"User: {exchange['user']}\n"
            context += f"Assistant: {exchange['assistant']}\n"
        return context

    def call_groq_api(self, user_input):
        """Enhanced API call with better error handling and context"""
        self.enforce_rate_limit()

        # Build conversation context
        conversation_context = self.get_conversation_context()

        system_prompt = f"""You are a helpful, accurate assistant for Food Pulse platform.

CONTEXT INFORMATION:
{self.document_text}

GUIDELINES:
- Answer based ONLY on the context provided above
- If information isn't in context, say you don't know
- Keep responses concise (2-3 paragraphs maximum)
- Be factual and helpful
- Focus on Food Pulse operations, registration, food safety, and impact
- If asked about unrelated topics, politely redirect to Food Pulse topics

{conversation_context}

Current user question: {user_input}"""

        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ],
            "max_tokens": 500,
            "temperature": 0.3,
            "top_p": 0.9
        }

        headers = {
            "Authorization": f"Bearer {self.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(
                self.GROQ_API_URL,
                json=payload,
                headers=headers,
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"].strip()
            elif response.status_code == 429:
                return "rate_limit"
            else:
                # For more detailed error logging on the server
                print(f"Groq API Error: Status {response.status_code}, Body: {response.text}")
                return "api_error"

        except requests.exceptions.Timeout:
            return "api_error"
        except requests.exceptions.RequestException:
            return "api_error"
        except Exception:
            return "api_error"

    def generate_response(self, user_input):
        """Main response generation with enhanced logic"""
        user_input = user_input.strip()

        if not user_input:
            return "Please ask me a question about Food Pulse! 🌍"

        # Check for greetings
        greetings = ["hello", "hi", "hey", "greetings"]
        if any(user_input.lower().startswith(greet) for greet in greetings):
            return f"{self.response_templates['welcome']} What would you like to know about Food Pulse?"
        
        # Check for farewells
        farewells = ["exit", "quit", "bye", "goodbye"]
        if user_input.lower() in farewells:
            return self.response_templates['farewell']

        # Check if related to Food Pulse
        if not self.is_food_pulse_related(user_input):
            return self.response_templates['off_topic']

        # Try FAQ matching first
        faq_answer, category, confidence = self.find_best_faq_match(user_input)

        if faq_answer and confidence > 0.7:
            response = faq_answer
            if confidence < 0.9:
                response += "\n\nIf you need more specific details, feel free to ask!"
        else:
            # Fall back to Groq API
            api_response = self.call_groq_api(user_input)

            if api_response in ["rate_limit", "api_error", "daily_limit"]:
                response = self.response_templates[api_response]
            else:
                response = api_response

        # Store in conversation history
        self.conversation_history.append({
            "user": user_input,
            "assistant": response,
            "timestamp": datetime.now().isoformat(),
            "category": category if category else "api"
        })

        # Keep history manageable
        if len(self.conversation_history) > self.max_history_length:
            self.conversation_history.pop(0)

        return response
