import os
import asyncio
import requests
import edge_tts
from pydub import AudioSegment

# আপনার টেলিগ্রাম বটের টোকেন
BOT_TOKEN = "8747528780:AAFMHdPAf-UIrUg_XmEVU9K2CLvavtkQApo"

async def generate_horror_audio():
    if not os.path.exists("script.txt"):
        print("Error: script.txt ফাইলটি পাওয়া যায়নি!")
        return
        
    with open("script.txt", "r", encoding="utf-8") as f:
        script_text = f.read().strip()
        
    if not script_text:
        print("script.txt ফাইলে কোনো গল্প লেখা নেই!")
        return

    temp_voice = "voice.mp3"
    output_audio = "final_horror_audio.mp3"
    bg_music_path = "horror_bg.m4a"
    
    print("১. এআই ভয়েস তৈরি হচ্ছে...")
    voice_name = "en-US-ChristopherNeural"
    communicate = edge_tts.Communicate(script_text, voice_name)
    await communicate.save(temp_voice)
    
    print("২. ভয়েস ও হরর মিউজিক মিক্সিং হচ্ছে...")
    voice_audio = AudioSegment.from_mp3(temp_voice)
    bg_music = AudioSegment.from_file(bg_music_path, format="m4a")
    
    bg_music = bg_music - 22  # ব্যাকগ্রাউন্ড মিউজিকের ভলিউম কমানো
    final_bg = bg_music * (int(len(voice_audio) / len(bg_music)) + 1)
    final_bg = final_bg[:len(voice_audio)]
    
    combined_audio = voice_audio.overlay(final_bg)
    combined_audio.export(output_audio, format="mp3")
    
    # টেম্পোরারি ভয়েস ফাইল ডিলিট
    if os.path.exists(temp_voice): 
        os.remove(temp_voice)
    
    print("🚀 অডিও মিক্সিং শেষ! এখন টেলিগ্রামে পাঠানো হচ্ছে...")
    return output_audio

def send_audio_to_telegram(audio_path):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    try:
        response = requests.get(url).json()
        chat_id = response['result'][-1]['message']['chat']['id']
    except:
        print("টেলিগ্রাম চ্যাট আইডি পাওয়া যায়নি! দয়া করে বটে একটি হাই/হ্যালো লিখে রাখুন।")
        return

    # অডিও ফাইল পাঠানো
    audio_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendAudio"
    with open(audio_path, 'rb') as audio_file:
        files = {'audio': audio_file}
        data = {'chat_id': chat_id, 'caption': 'Here is your ready horror audio! 🎙️'}
        requests.post(audio_url, data=data, files=files)
    print("সাফল্যের সাথে অডিও আপনার টেলিগ্রামে পাঠানো হয়েছে!")

if __name__ == "__main__":
    audio = asyncio.run(generate_horror_audio())
    if audio and os.path.exists(audio):
        send_audio_to_telegram(audio)
        # কাজ শেষে ফাইনাল ফাইল ক্লিয়ার করা
        if os.path.exists(audio): 
            os.remove(audio)
  
