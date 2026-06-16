import os
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import edge_tts
from pydub import AudioSegment

# লগিং চালু করা (ব্যাকএন্ডে কোনো সমস্যা হলে ট্র্যাক করার জন্য)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# আপনার দেওয়া টেলিগ্রাম বটের টোকেন
BOT_TOKEN = "8747528780:AAFMHdPAf-UIrUg_XmEVU9K2CLvavtkQApo"

async def generate_horror_audio(script_text, chat_id):
    temp_voice = f"voice_{chat_id}.mp3"
    output_audio = f"horror_audio_{chat_id}.mp3"
    bg_music_path = "horror_bg.m4a"
    
    # ব্যাকগ্রাউন্ড মিউজিক ফাইল আছে কি না চেক করা
    if not os.path.exists(bg_music_path):
        return None, "Error: 'horror_bg.m4a' ফাইলটি সার্ভারে পাওয়া যায়নি!"

    try:
        # ১. edge-tts দিয়ে ক্রিস্টোফার ভয়েসে প্রিমিয়াম ইউএসএ মেইল ভয়েস তৈরি
        voice_name = "en-US-ChristopherNeural"
        communicate = edge_tts.Communicate(script_text, voice_name)
        await communicate.save(temp_voice)
        
        # ২. Pydub দিয়ে ভয়েস এবং ব্যাকগ্রাউন্ড মিউজিক লোড করা
        voice_audio = AudioSegment.from_mp3(temp_voice)
        bg_music = AudioSegment.from_file(bg_music_path, format="m4a")
        
        # ব্যাকগ্রাউন্ড মিউজিকের ভলিউম ২২ ডেসিবেল কমিয়ে দেওয়া, যেন কথা স্পষ্ট শোনা যায়
        bg_music = bg_music - 22  
        
        # মিউজিকের দৈর্ঘ্যকে স্ক্রিপ্টের ভয়েসের সমান করা
        final_bg = bg_music * (int(len(voice_audio) / len(bg_music)) + 1)
        final_bg = final_bg[:len(voice_audio)]
        
        # দুটি অডিও একসাথে মিক্স করা
        combined_audio = voice_audio.overlay(final_bg)
        combined_audio.export(output_audio, format="mp3")
        
        # অস্থায়ী ভয়েস ফাইলটি মুছে ফেলা
        if os.path.exists(temp_voice): 
            os.remove(temp_voice)
        
        return output_audio, "Success"
        
    except Exception as e:
        if os.path.exists(temp_voice): 
            os.remove(temp_voice)
        return None, str(e)

# বটের /start কমান্ড হ্যান্ডলার
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎃 স্বাগতম সাজ্জাদ!\n\nযেকোনো ইংরেজি হরর স্ক্রিপ্ট এখানে মেসেজ হিসেবে পাঠিয়ে দিন। "
        "আমি সাথে সাথে ভয়েস ওভার তৈরি করে ব্যাকগ্রাউন্ড মিউজিকে মিক্সড করে আপনাকে রেডি .mp3 ফাইল পাঠিয়ে দেব।"
    )

# বটের টেক্সট মেসেজ হ্যান্ডলার
async def handle_script(update: Update, context: ContextTypes.DEFAULT_TYPE):
    script_text = update.message.text
    chat_id = update.message.chat_id
    
    # ইউজারকে প্রসেসিং মেসেজ দেওয়া
    status_message = await update.message.reply_text("🎙️ আপনার অডিওটি তৈরি হচ্ছে... দয়া করে কয়েক সেকেন্ড অপেক্ষা করুন...")
    
    # অডিও জেনারেট করা
    audio_file, status = await generate_horror_audio(script_text, chat_id)
    
    if status == "Success" and audio_file:
        await status_message.edit_text("🚀 অডিও মিক্সিং শেষ! এখন ইনবক্সে পাঠানো হচ্ছে...")
        
        # সরাসরি টেলিগ্রামে অডিও ফাইল হিসেবে পাঠানো
        with open(audio_file, 'rb') as audio:
            await update.message.reply_audio(audio=audio, caption="Here is your ready horror audio! 🎉")
        
        # কাজ শেষে সার্ভারের স্পেস বাঁচাতে ফাইল ডিলিট করা
        if os.path.exists(audio_file):
            os.remove(audio_file)
    else:
        await status_message.edit_text(f"❌ অডিও তৈরিতে সমস্যা হয়েছে। এরর: {status}")

def main():
    # টেলিগ্রাম অ্যাপ্লিকেশন বিল্ড করা
    application = Application.builder().token(BOT_TOKEN).build()
    
    # হ্যান্ডলারগুলো যুক্ত করা
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_script))
    
    # পোলিং মোডে বট চালু করা
    print("টেলিগ্রাম হরর অডিও মেকার বট সফলভাবে চালু হয়েছে...")
    application.run_polling()

if __name__ == "__main__":
    main()
        
