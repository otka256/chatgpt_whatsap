import os
import sys
import time
import json
import logging
import platform
import psutil
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("WhatsAppGPT")

# Load environment configuration
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# WhatsApp / Message Gateway API Configuration
MESSAGE_WALL_API = os.getenv("MESSAGE_WALL_API", "")
MESSAGE_WALL_BASE_URL = os.getenv("MESSAGE_WALL_BASE_URL", "https://api.chat-api.com")
INSTANCE_ID = os.getenv("INSTANCE_ID", "")
POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", "3"))

SYSTEM_PROMPT = """You are an intelligent WhatsApp AI assistant. 
You provide concise, helpful, and natural responses in Persian or English based on the user's language.
When provided with system/environmental metrics, use them accurately if asked."""

def get_environmental_data() -> Dict[str, Any]:
    """Collects system metrics and environmental parameters."""
    try:
        cpu_usage = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        
        return {
            "os": platform.platform(),
            "python_version": platform.python_version(),
            "cpu_usage_percent": cpu_usage,
            "memory_usage_percent": mem.percent,
            "memory_available_gb": round(mem.available / (1024 ** 3), 2),
            "disk_free_gb": round(disk.free / (1024 ** 3), 2),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        logger.warning(f"Failed to gather full environmental metrics: {e}")
        return {
            "os": platform.platform(),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

def ask_chatgpt(user_message: str, env_context: Optional[Dict[str, Any]] = None) -> str:
    """Queries OpenAI API (or OpenAI-compatible endpoint) with message & environmental context."""
    if not OPENAI_API_KEY:
        return "⚠️ Error: OPENAI_API_KEY is not configured in environment variables or .env file."

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    context_str = json.dumps(env_context, indent=2, ensure_ascii=False) if env_context else "None"
    augmented_prompt = f"{SYSTEM_PROMPT}\n\n[Live Environmental & System Status]:\n{context_str}"

    payload = {
        "model": OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": augmented_prompt},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.7,
        "max_tokens": 800
    }

    try:
        response = requests.post(
            f"{OPENAI_BASE_URL.rstrip('/')}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logger.error(f"Error communicating with OpenAI: {e}")
        return f"⚠️ Service error while generating AI response: {str(e)}"

def fetch_incoming_messages() -> list:
    """Fetches incoming WhatsApp messages via Message Wall / Gateway API."""
    if not MESSAGE_WALL_API:
        return []

    url = f"{MESSAGE_WALL_BASE_URL.rstrip('/')}/{INSTANCE_ID}/messages"
    params = {"token": MESSAGE_WALL_API, "last": 10}

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("messages", [])
    except Exception as e:
        logger.error(f"Failed to fetch incoming messages from Message Wall: {e}")
    return []

def send_whatsapp_message(chat_id: str, body: str) -> bool:
    """Sends reply message back to user via WhatsApp Message Wall API."""
    if not MESSAGE_WALL_API:
        logger.info(f"[SIMULATED OUTBOX] To: {chat_id} | Message: {body}")
        return True

    url = f"{MESSAGE_WALL_BASE_URL.rstrip('/')}/{INSTANCE_ID}/sendMessage"
    payload = {
        "token": MESSAGE_WALL_API,
        "chatId": chat_id,
        "body": body
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            logger.info(f"Successfully delivered response to {chat_id}")
            return True
        else:
            logger.error(f"Failed to send message: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"Network error delivering message to {chat_id}: {e}")
    return False

def main_loop():
    """Continuous worker listening for incoming WhatsApp messages and auto-replying with GPT."""
    logger.info("=== Starting WhatsApp ChatGPT Bridge Service ===")
    logger.info(f"OpenAI Model: {OPENAI_MODEL} | Base URL: {OPENAI_BASE_URL}")
    
    processed_message_ids = set()

    while True:
        try:
            messages = fetch_incoming_messages()
            for msg in messages:
                msg_id = msg.get("id")
                from_me = msg.get("fromMe", False)
                sender = msg.get("chatId") or msg.get("from")
                text = msg.get("body", "").strip()

                if not msg_id or msg_id in processed_message_ids or from_me or not text:
                    continue

                processed_message_ids.add(msg_id)
                logger.info(f"Received query from {sender}: {text}")

                # Gather real-time system/environmental metrics
                env_data = get_environmental_data()

                # Generate AI response
                reply_text = ask_chatgpt(text, env_context=env_data)

                # Send response back to WhatsApp
                send_whatsapp_message(sender, reply_text)

            time.sleep(POLL_INTERVAL_SECONDS)

        except KeyboardInterrupt:
            logger.info("Service stopped by user.")
            break
        except Exception as e:
            logger.error(f"Unexpected loop exception: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main_loop()
