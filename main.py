import requests
import random
import time
from telegram import Bot, InputMediaPhoto
from telegram.error import TelegramError
from datetime import datetime

# Configuration
TELEGRAM_BOT_TOKEN = '8062649272:AAFkPK3avG4EtjIZKuut8dgq0cv1_F3aihA'
CHANNEL_ID = -1002641339979  # or CHANNEL_ID if numeric
IMAGE_URL = 'https://ibb.co/DXrGXMz'  # Set your image URL here
RAW_FILE_URL = 'https://raw.githubusercontent.com/BL4CKH4T336/num/refs/heads/main/vbvbin.txt'
CC_GENERATOR_URL = 'https://drlabapis.onrender.com/api/ccgenerator?bin={bin}&count=1'
XCHECKER_URL = 'https://xchecker.cc/api.php?cc={cc}'
BIN_LOOKUP_URL = 'https://bins.antipublic.cc/bins/{bin}'

# Initialize bot
bot = Bot(token=TELEGRAM_BOT_TOKEN)

def get_3d_false_bins():
    try:
        response = requests.get(RAW_FILE_URL)
        response.raise_for_status()
        lines = response.text.split('\n')

        false_bins = []
        for line in lines:
            if "3D FALSE" in line and "✅" in line:
                bin_part = line.split('|')[0].strip()
                if len(bin_part) >= 6:  # Ensure it's a valid BIN
                    false_bins.append(bin_part[:6])  # Take first 6 digits
                    status_text = line.split('|')[-1].strip()

        return false_bins, status_text
    except Exception as e:
        print(f"Error getting 3D false bins: {e}")
        return [], ""

def generate_cc(bin):
    try:
        response = requests.get(CC_GENERATOR_URL.format(bin=bin))
        response.raise_for_status()
        return response.text.strip()  # Assuming the response is plain text CC
    except Exception as e:
        print(f"Error generating CC: {e}")
        return None

def check_cc(cc):
    try:
        response = requests.get(XCHECKER_URL.format(cc=cc))
        response.raise_for_status()
        data = response.json()
        return data.get('details', '').split('\n')[0]  # Get first line of details
    except Exception as e:
        print(f"Error checking CC: {e}")
        return "Check failed"

def get_bin_info(bin):
    try:
        response = requests.get(BIN_LOOKUP_URL.format(bin=bin))
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error getting BIN info: {e}")
        return {}

def format_message(cc, auth_response, bin_status, bin_info):
    # Extract CC components
    cc_parts = cc.split('|')
    cc_number = cc_parts[0]
    month = cc_parts[1] if len(cc_parts) > 1 else 'XX'
    year = cc_parts[2] if len(cc_parts) > 2 else 'XXXX'
    cvv = cc_parts[3] if len(cc_parts) > 3 else 'XXX'

    # Create extrapolated CC
    extrap_cc = f"{cc_number[:12]}xxxx|{month}|{year}"

    # Format BIN info
    brand = bin_info.get('brand', 'UNKNOWN')
    bank = bin_info.get('bank', 'UNKNOWN')
    country = bin_info.get('country_name', 'UNKNOWN')
    flag = bin_info.get('country_flag', '🏳')
    card_type = bin_info.get('type', 'UNKNOWN')

    message = f"""
✜━━━━━━━━━━━━━━━━━━━━✜
[✜] CC: <code>{cc}</code>
[✜] EXTRAP: <code>{extrap_cc}</code>
[✜] CC: <code>{cc_number}</code>
-----------------------------
[✜] Auth : <i>{auth_response}</i>
[✜] 3DS : <i>{bin_status} ✅</i>
-----------------------------
[✜] BIN: #{bin_info.get('bin', '')}
[✜] BANK: {bank}
[✜] DATA: {brand} - {card_type}
[✜] COUNTRY: {country} {flag}
✜━━━━━━━━━━━━━━━━━━━━✜
"""
    return message.strip()

async def send_to_channel():
    while True:
        try:
            # Get 3D FALSE bins
            false_bins, status_text = get_3d_false_bins()

            if not false_bins:
                print("No 3D FALSE bins found")
                await asyncio.sleep(300)  # Wait 5 minutes before trying again
                continue

            # Select a random BIN
            selected_bin = random.choice(false_bins)

            # Generate CC
            cc = generate_cc(selected_bin)
            if not cc:
                await asyncio.sleep(300)
                continue

            # Check CC
            auth_response = check_cc(cc)

            # Get BIN info
            bin_info = get_bin_info(selected_bin)

            # Format message
            message = format_message(cc, auth_response, status_text, bin_info)

            # Send message with photo
            try:
                await bot.send_photo(
                    chat_id=CHANNEL_ID,
                    photo=IMAGE_URL,
                    caption=message,
                    parse_mode='HTML'
                )
                print(f"Message sent at {datetime.now()}")
            except TelegramError as e:
                print(f"Error sending message: {e}")

            # Wait 5 minutes before next check
            await asyncio.sleep(180)

        except Exception as e:
            print(f"Error in main loop: {e}")
            await asyncio.sleep(180)  # Wait before retrying

if __name__ == '__main__':
    import asyncio
    asyncio.run(send_to_channel())
