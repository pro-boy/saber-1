
import nude
import html
import asyncio
from pymongo import MongoClient
from tg_bot import MONGO_DB_URI
from tg_bot.events import register
from telethon import types, events
from telethon.tl import *
from telethon.tl.types import *
from tg_bot import *
import better_profanity
from better_profanity import profanity
from textblob import TextBlob

client = MongoClient()
client = MongoClient(MONGO_DB_URI)
db = client["saberbot"]
approved_users = db.approve
spammers = db.spammer
cleanservices = db.cleanservice
globalchat = db.globchat

CMD_STARTERS = '/'
profanity.load_censor_words_from_file('./profanity_wordlist.txt')


async def is_register_admin(chat, user):
    if isinstance(chat, (types.InputPeerChannel, types.InputChannel)):

        return isinstance(
            (
                await client(functions.channels.GetParticipantRequest(chat, user))
            ).participant,
            (types.ChannelParticipantAdmin, types.ChannelParticipantCreator),
        )
    if isinstance(chat, types.InputPeerChat):

        ui = await client.get_peer_id(user)
        ps = (
            await tbot(functions.messages.GetFullChatRequest(chat.chat_id))
        ).full_chat.participants.participants
        return isinstance(
            next((p for p in ps if p.user_id == ui), None),
            (types.ChatParticipantAdmin, types.ChatParticipantCreator),
        )
    return None



@register(pattern="^/profanity(?: |$)(.*)")
async def profanity(event):
    if event.fwd_from:
        return
    if event.is_private:
        return
    if MONGO_DB_URI is None:
        return
    if not await can_change_info(message=event):
        return
    input = event.pattern_match.group(1)
    chats = spammers.find({})
    if not input:
        for c in chats:
            if event.chat_id == c["id"]:
                await event.reply(
                    "Please provide some input yes or no.\n\nCurrent setting is : **on**"
                )
                return
        await event.reply(
            "Please provide some input yes or no.\n\nCurrent setting is : **off**"
        )
        return
    if input == "on":
        if event.is_group:
            chats = spammers.find({})
            for c in chats:
                if event.chat_id == c["id"]:
                    await event.reply(
                        "Profanity filter is already activated for this chat.")
                    return
            spammers.insert_one({"id": event.chat_id})
            await event.reply("Profanity filter turned on for this chat.")
    if input == "off":
        if event.is_group:  
            chats = spammers.find({})
            for c in chats:
                if event.chat_id == c["id"]:
                    spammers.delete_one({"id": event.chat_id})
                    await event.reply(
                        "Profanity filter turned off for this chat.")
                    return
        await event.reply(
                    "Profanity filter isn't turned on for this chat.")
    if not input == "on" and not input == "off":
        await event.reply("I only understand by on or off")
        return

@register(pattern="^/globalmode(?: |$)(.*)")
async def profanity(event):
    if event.fwd_from:
        return
    if event.is_private:
        return
    if MONGO_DB_URI is None:
        return
    if not await can_change_info(message=event):
        return
    input = event.pattern_match.group(1)
    chats = globalchat.find({})
    if not input:
        for c in chats:
            if event.chat_id == c["id"]:
                await event.reply(
                    "Please provide some input yes or no.\n\nCurrent setting is : **on**"
                )
                return
        await event.reply(
            "Please provide some input yes or no.\n\nCurrent setting is : **off**"
        )
        return
    if input == "on":
        if event.is_group:
            chats = globalchat.find({})
            for c in chats:
                if event.chat_id == c["id"]:
                    await event.reply(
                        "Global mode is already activated for this chat.")
                    return
            globalchat.insert_one({"id": event.chat_id})
            await event.reply("Global mode turned on for this chat.")
    if input == "off":
        if event.is_group:  
            chats = globalchat.find({})
            for c in chats:
                if event.chat_id == c["id"]:
                    globalchat.delete_one({"id": event.chat_id})
                    await event.reply(
                        "Global mode turned off for this chat.")
                    return
        await event.reply(
                    "Global mode isn't turned on for this chat.")
    if not input == "on" and not input == "off":
        await event.reply("I only understand by on or off")
        return


@tbot.on(events.NewMessage(pattern=None))
async def del_profanity(event):
    if event.is_private:
        return
    if MONGO_DB_URI is None:
        return
    msg = str(event.text)
    sender = await event.get_sender()
    let = sender.username
    if event.is_group:
        if (await is_register_admin(event.input_chat, event.message.sender_id)):
            return
        pass
    chats = spammers.find({})
    for c in chats:
        if event.text:
            if event.chat_id == c['id']:
                if better_profanity.profanity.contains_profanity(msg):
                    await event.delete()
                    if sender.username is None:
                        st = sender.first_name
                        hh = sender.id
                        final = f"[{st}](tg://user?id={hh}) **{msg}** is detected as a slang word and your message has been deleted"
                    else:
                        final = f'@{let} **{msg}** is detected as a slang word and your message has been deleted'
                    dev = await event.respond(final)
                    await asyncio.sleep(10)
                    await dev.delete()
        if event.photo:
            if event.chat_id == c['id']:
                await event.client.download_media(event.photo, "nudes.jpg")
                if nude.is_nude('./nudes.jpg'):
                    await event.delete()
                    if sender.username is None:
                        st = sender.first_name
                        hh = sender.id
                        final = f"[{st}](tg://user?id={hh}) your message has been deleted due to pornographic content"
                    else:
                        final = f'@{let} your message has been deleted due to pornographic content'
                    dev = await event.respond(final)
                    await asyncio.sleep(10)
                    await dev.delete()
                    os.remove("nudes.jpg")

@tbot.on(events.NewMessage(pattern=None))
async def del_profanity(event):
    if event.is_private:
        return
    if MONGO_DB_URI is None:
        return
    msg = str(event.text)
    sender = await event.get_sender()
    let = sender.username
    if event.is_group:
        if (await is_register_admin(event.input_chat, event.message.sender_id)):
            return
        pass
    chats = globalchat.find({})
    for c in chats:
        if event.text:
            if event.chat_id == c['id']:
                a = TextBlob(msg)
                b = a.detect_language()
                if not b == "en":
                    await event.delete()
                    if sender.username is None:
                        st = sender.first_name
                        hh = sender.id
                        final = f"[{st}](tg://user?id={hh}) you should only speak in english here !"
                    else:
                        final = f'@{let} you should only speak in english here !'
                    dev = await event.respond(final)
                    await asyncio.sleep(10)
                    await dev.delete()



file_help = os.path.basename(__file__)
file_help = file_help.replace(".py", "")
file_helpo = file_help.replace("_", " ")


