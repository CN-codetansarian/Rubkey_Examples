import asyncio
import json
import os
import time
import random
import re
from rubkey import AsyncBot, Keypad, KeyButton, InlineKeypad, InlineButton

TOKEN = ""
bot = AsyncBot(token=TOKEN)

GROUPS_FILE = "G.json"
MESSAGES_FILE = "M.json"

def load_json(file):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_groups():
    return load_json(GROUPS_FILE)

def save_groups(data):
    save_json(GROUPS_FILE, data)

def load_messages():
    data = load_json(MESSAGES_FILE)
    now = time.time()
    cleaned = {}
    for chat_id, users in data.items():
        cleaned[chat_id] = {}
        for user_id, msgs in users.items():
            valid = [t for t in msgs if now - t < 54000]
            if valid:
                cleaned[chat_id][user_id] = valid
    save_json(MESSAGES_FILE, cleaned)
    return cleaned

def save_messages(data):
    save_json(MESSAGES_FILE, data)

def is_group_active(chat_id):
    data = load_groups()
    return data.get(chat_id, {}).get("active", False)

def is_owner(chat_id, user_id):
    data = load_groups()
    return data.get(chat_id, {}).get("owner") == user_id

def is_banned(chat_id, user_id):
    data = load_groups()
    return user_id in data.get(chat_id, {}).get("bans", [])

def is_link_locked(chat_id):
    data = load_groups()
    return data.get(chat_id, {}).get("link_lock", False)

def is_id_locked(chat_id):
    data = load_groups()
    return data.get(chat_id, {}).get("id_lock", False)

def get_active_count():
    data = load_groups()
    return sum(1 for g in data.values() if g.get("active", False))

def save_message(chat_id, user_id):
    data = load_messages()
    if chat_id not in data:
        data[chat_id] = {}
    if user_id not in data[chat_id]:
        data[chat_id][user_id] = []
    data[chat_id][user_id].append(time.time())
    data[chat_id][user_id] = [t for t in data[chat_id][user_id] if time.time() - t < 54000]
    save_messages(data)

def get_user_message_count(chat_id, user_id):
    data = load_messages()
    return len(data.get(chat_id, {}).get(user_id, []))

def get_top_users(chat_id):
    data = load_messages()
    chat_msgs = data.get(chat_id, {})
    sorted_users = sorted(chat_msgs.items(), key=lambda x: len(x[1]), reverse=True)
    return sorted_users[:3]

def get_user_nickname(chat_id, user_id):
    data = load_groups()
    return data.get(chat_id, {}).get("nicknames", {}).get(user_id, None)

def set_user_nickname(chat_id, user_id, nickname):
    data = load_groups()
    if chat_id not in data:
        return
    if "nicknames" not in data[chat_id]:
        data[chat_id]["nicknames"] = {}
    data[chat_id]["nicknames"][user_id] = nickname
    save_groups(data)

def has_link(text):
    patterns = [
        r'https?://[^\s]+', r'www\.[^\s]+', r't\.me/\S+',
        r'rubika\.ir/\S+', r'[a-zA-Z0-9]+\.(ir|com|net|org|info)'
    ]
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

def has_id(text):
    return '@' in text


@bot.command("start")
async def start(msg):
    if not msg.chat_id.startswith("b"):
        return
    
    uid = msg.sender_id
    
    chat_info = await bot.get_chat(msg.chat_id)
    data = chat_info.get("chat", {})
    first_name = data.get("first_name", "کاربر")
    
    active_count = get_active_count()
    
    inline_kp = InlineKeypad().add_row(
        InlineButton("active_groups", f"تعداد گروه های فعال: {active_count}")
    )
    
    await msg.reply(
        f"سلام {first_name} به بات مدیریت گروه CN خوش اومدی..\n\n"
        f"برای فعال سازی بات تو گروهت باید اینکارا رو بکنی:\n"
        f"1_بات رو بصورت کامل ادمین کنی\n"
        f"2_چند دقیقه صبر کنی و بعد تو گروه بگی:روشن\n"
        f"بعد بات روشن میشه و تو میتونی با دستور: دستورات\n"
        f"اینو تو گروه بفرستی دستور ها نمایش میده\n\n"
        f"🔰یک بات مدیریت گروه کاملا رایگان🔰",
        inline_keypad=inline_kp
    )


@bot.on_button("active_groups")
async def active_groups(msg):
    active_count = get_active_count()
    inline_kp = InlineKeypad().add_row(
        InlineButton("active_groups", f"تعداد گروه های فعال: {active_count}")
    )
    await msg.edit(f"🔰 تعداد گروه های فعال: {active_count}", inline_keypad=inline_kp)


@bot.on_message()
async def handle(msg):
    chat_id = msg.chat_id
    user_id = msg.sender_id
    
    if not msg.text:
        return
    
    if hasattr(msg, 'button_id') and msg.button_id:
        return
    
    if not chat_id.startswith("g"):
        return
    
    text = msg.text.strip()
    
    if text == "روشن":
        data = load_groups()
        
        if chat_id in data:
            if data[chat_id].get("active"):
                await msg.reply("بات از قبل روشن بوده")
                return
            if data[chat_id].get("owner") and data[chat_id]["owner"] != user_id:
                await msg.reply("فقط مالک گروه میتونه بات رو روشن کنه")
                return
        
        group_info = await bot.get_chat(chat_id)
        gdata = group_info.get("chat", {})
        group_name = gdata.get("title", "گروه")
        
        data[chat_id] = {
            "name": group_name,
            "owner": user_id,
            "active": True,
            "link_lock": False,
            "id_lock": False,
            "bans": [],
            "nicknames": {}
        }
        save_groups(data)
        
        await msg.reply(f"بات روشن شد\nگروه:{group_name}\nمالک:{user_id}")
        return
    
    if text == "خاموش":
        if not is_owner(chat_id, user_id):
            return
        
        data = load_groups()
        if chat_id in data:
            data[chat_id]["active"] = False
            save_groups(data)
        
        await msg.reply(f"بات خاموش شد\nمالک:{user_id}")
        return
    
    if not is_group_active(chat_id):
        return
    
    save_message(chat_id, user_id)
    
    if is_owner(chat_id, user_id):
        if text == "حذف" and msg.reply_to_message_id:
            try:
                await bot.delete_message(chat_id, msg.reply_to_message_id)
                await bot.send_message(chat_id, "پیام حذف شد👌🦦")
            except:
                await bot.send_message(chat_id, "پیام حذف نشده احتمالا مشکلی پیش اومده")
            return
        
        if text == "بن" and msg.reply_to_message_id:
            target_id = bot.message_map.get(msg.reply_to_message_id)
            if target_id:
                if is_banned(chat_id, target_id):
                    await bot.send_message(chat_id, "🔫کاربر بن بودش...")
                    return
                
                data = load_groups()
                if chat_id in data:
                    if "bans" not in data[chat_id]:
                        data[chat_id]["bans"] = []
                    data[chat_id]["bans"].append(target_id)
                    save_groups(data)
                
                try:
                    await bot.ban_chat_member(chat_id, target_id)
                except:
                    pass
                
                await bot.send_message(chat_id, "🦦کاربر مورد نظر بن شد...")
            else:
                await bot.send_message(chat_id, "🦦کاربر مورد نظرت حذف نشده مشتی احتمالا مشکلی پیش اومده")
            return
        
        if text in ["انبن", "آنبن"] and msg.reply_to_message_id:
            target_id = bot.message_map.get(msg.reply_to_message_id)
            if target_id:
                if not is_banned(chat_id, target_id):
                    await bot.send_message(chat_id, "🫠کاربر بن نبود...")
                    return
                
                data = load_groups()
                if chat_id in data and target_id in data[chat_id].get("bans", []):
                    data[chat_id]["bans"].remove(target_id)
                    save_groups(data)
                
                try:
                    await bot.unban_chat_member(chat_id, target_id)
                except:
                    pass
                
                await bot.send_message(chat_id, "👌کاربر انبن شد...")
            else:
                await bot.send_message(chat_id, "🫠کاربر بن نبود...")
            return
        
        if text == "قفل لینک روشن":
            data = load_groups()
            if chat_id in data:
                if data[chat_id].get("link_lock"):
                    await msg.reply("👌مشتی قبلا قفل لینک روشن بود...")
                else:
                    data[chat_id]["link_lock"] = True
                    save_groups(data)
                    await msg.reply("قفل لینک روشن شد🦦")
            return
        
        if text == "قفل لینک خاموش":
            data = load_groups()
            if chat_id in data:
                if not data[chat_id].get("link_lock"):
                    await msg.reply("قبلا خاموشش کرده بودی سید...")
                else:
                    data[chat_id]["link_lock"] = False
                    save_groups(data)
                    await msg.reply("قفل لینک خاموش شد...")
            return
        
        if text == "قفل ایدی روشن":
            data = load_groups()
            if chat_id in data:
                if data[chat_id].get("id_lock"):
                    await msg.reply("🦦مشتی قبلا قفل ایدی روشن بود...")
                else:
                    data[chat_id]["id_lock"] = True
                    save_groups(data)
                    await msg.reply("🔰قفل ایدی روشن شد")
            return
        
        if text == "قفل ایدی خاموش":
            data = load_groups()
            if chat_id in data:
                if not data[chat_id].get("id_lock"):
                    await msg.reply("قفل ایدی خاموش بود")
                else:
                    data[chat_id]["id_lock"] = False
                    save_groups(data)
                    await msg.reply("قفل ایدی خاموش شد مشتی👌")
            return
    
    if is_link_locked(chat_id) and has_link(text):
        if not is_owner(chat_id, user_id):
            try:
                await bot.delete_message(chat_id, msg.message_id)
                await bot.send_message(chat_id, "🫠یکی لینک فرستاد پاکیدمش")
            except:
                pass
            return
    
    if is_id_locked(chat_id) and has_id(text):
        if not is_owner(chat_id, user_id):
            try:
                await bot.delete_message(chat_id, msg.message_id)
            except:
                pass
            return
    
    if text == "سلام":
        await msg.reply("🫡سلام مشتی چه خبرا چی کا مکنی؟")
        return
    
    if text == "خوبی؟":
        await msg.reply("چی بگم والا")
        return
    
    if text == "عجب":
        await msg.reply("چی عجب؟")
        return
    
    if text == "تاس":
        dice = random.choice(['⚀', '⚁', '⚂', '⚃', '⚄', '⚅'])
        await msg.reply(dice)
        return
    
    if text == "مقام":
        if is_owner(chat_id, user_id):
            await msg.reply("⚜️مقام شما:مالک گروه")
        else:
            await msg.reply("🔰مقام شما:عضو")
        return
    
    if text in ["امار", "آمار"]:
        msg_count = get_user_message_count(chat_id, user_id)
        rank = "⚜️مالک گروه" if is_owner(chat_id, user_id) else "🔰عضو"
        nickname = get_user_nickname(chat_id, user_id)
        nick_text = f"\n🔸️{nickname}" if nickname else "\n🔸️نداری"
        
        await msg.reply(
            f"📊امار شما:\n\n"
            f"مقام:{rank}{nick_text}\n\n"
            f"تعداد پیام امروز شما:\n{msg_count}"
        )
        return
    
    if text in ["تاپ", "رتبه"]:
        top_users = get_top_users(chat_id)
        
        if not top_users:
            await msg.reply("هیچ کسی نیست")
            return
        
        result = "📊رتبه نفراتی که بیشترین پیام رو توی گروه دادن:\n\n"
        
        for i, (uid, msgs) in enumerate(top_users, 1):
            data = load_groups()
            nickname = get_user_nickname(chat_id, uid)
            name = nickname if nickname else uid[:10]
            result += f"{i}_{name}\n"
        
        await msg.reply(result)
        return
    
    if text.startswith("تنظیم لقب "):
        nickname = text[10:].strip()
        if nickname:
            set_user_nickname(chat_id, user_id, nickname)
            await msg.reply(f"لقب {nickname} ثبت شد👌")
        return
    
    if text == "دستورات":
        help_text = """⚜️دستورات مالک:
روشن - روشن کردن بات تو گروه
خاموش - خاموش کردن بات تو گروه
حذف (باید ریپلای بزنی) - حذف پیام کاربر
بن (باید ریپلای بزنی) - مسدود کردن کاربر از گروه
انبن (باید ریپلای بزنی) - رفع کردن از گروه
آنبن (باید ریپلای بزنی) - رفع مسدودی

قفل لینک روشن - روشن کردن ضدلینک
قفل لینک خاموش - خاموش کردن ضدلینک
قفل ایدی روشن - فیلتر کردن ارسال ایدی
قفل ایدی خاموش - رفع فیلتر ارسال ایدی

🔰دستورات کاربران:
تاس - تاس اندازی
مقام - مشاده مقام
آمار _ امار - مشاهده امار کاربر
تنظیم لقب (نام لقب) - تنظیم کردن لقب توی گروه
تاپ_رتبه - نمایش 3 نفر که توی گروه بیشترین پیامو دادن"""
        await msg.reply(help_text)
        return


async def main():
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())