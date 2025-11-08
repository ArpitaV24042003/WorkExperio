from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer

# Optional: spaCy for preprocessing
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    USE_SPACY = True
except Exception as e:
    print("spaCy not loaded:", e)
    USE_SPACY = False

# Initialize FastAPI
app = FastAPI()

# Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ChatterBot with fallback response
chatbot = ChatBot(
    'WorkExperioBot',
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    database_uri='sqlite:///workexperio_db.sqlite3',
    logic_adapters=[
        {
            'import_path': 'chatterbot.logic.BestMatch',
            'default_response': "Sorry, I can only answer questions about WorkExperio. Can you rephrase?",
            'maximum_similarity_threshold': 0.75
        }
    ]
)

# Custom WorkExperio-related training
trainer = ListTrainer(chatbot)
trainer.train([
    # Greetings
    "Hi",
    "Hello! Welcome to WorkExperio. How can I help you today?",
    "Hello",
    "Hi! How can I assist you with your team or project?",

    # About WorkExperio
    "What is WorkExperio?",
    "WorkExperio is a platform to manage teams, projects, and individual tasks efficiently.",
    "Tell me about WorkExperio",
    "WorkExperio helps you track tasks, chat with your team, and generate AI-based project reports.",

    # Team & Tasks
    "I need clarification on my team lead",
    "You can ask your team lead directly in the chat interface, or I can guide you on how to report queries.",
    "How do I assign tasks?",
    "You can assign tasks using the project dashboard under the 'Tasks' section.",
    "How can I track progress?",
    "You can monitor team progress via the 'Team Dashboard', which shows task status and completion rates.",

    # Chat interface
    "How does chat work?",
    "The chat interface allows team members to communicate with each other in real-time.",
    "Can I talk to the AI bot?",
    "Yes! You can ask me any WorkExperio-related question here, and I will assist you.",

    # Reporting
    "How do I generate reports?",
    "Reports can be generated from the 'Reports' section for each project or team.",
    "Can I get AI-generated insights?",
    "Yes! WorkExperio can analyze team data and provide AI-based insights for your project.",

    # Closing / Politeness
    "Thank you",
    "You're welcome! Happy to help with WorkExperio.",
    "Bye",
    "Goodbye! Have a productive day with WorkExperio."
])

# Request model
class ChatRequest(BaseModel):
    message: str

# Chat endpoint
@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    user_message = request.message

    # Optional spaCy preprocessing
    if USE_SPACY:
        doc = nlp(user_message)
        user_message = " ".join([token.text.lower() for token in doc if not token.is_punct])

    response = chatbot.get_response(user_message)
    return {"response": str(response)}
