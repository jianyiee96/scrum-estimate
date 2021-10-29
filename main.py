from credentials import bot_token
from telegram import ParseMode, InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler, ConversationHandler
from pprint import pprint
import requests

scrum_members = dict()
scrum_master = dict()
modes = {"e": False, "u": False, "n": ""}

def check_id(id):

    print(f"Status:\n{scrum_master}")
    pprint(scrum_members)
    print("")
    
    return id in set(scrum_members.keys())

def start_command(update: Update, context: CallbackContext):
    chat_id = str(update.message.chat.id)

    if(chat_id in set(scrum_members.keys())):
        reply = f"Welcome to Scrum Estimator! registered liao"
    else:
        scrum_members[str(chat_id)] = {"name": update.message.chat.username, "estimate": ""}

        reply = f"Welcome to Scrum Estimator! I have registered you as a scrum member"
        if ('master' not in scrum_master.keys()) :
            reply += "\nNo one is scrum master at the moment."
        else:
            reply += f"\n{scrum_master} is the scrum master"

    update.message.reply_text(reply)

def be_master(update: Update, context: CallbackContext):
    chat_id = str(update.message.chat.id)
    if(not check_id(chat_id)):
        reply = "You are not in the scrum. register via /join"
        update.message.reply_text(reply)
        return

    scrum_master['master'] = chat_id
    reply = "You have become the scrum master!"
    update.message.reply_text(reply)

    message = f"Hi everyone! {scrum_members[scrum_master['master']]['name']} has become the scrum master"

    for cid in scrum_members.keys():
        api_req = f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={cid}&parse_mode=Markdown&text={message}'
        print(api_req)
        requests.get(api_req)

def who_master(update: Update, context: CallbackContext):
    chat_id = str(update.message.chat.id)
    if(not check_id(chat_id)):
        reply = "You are not in the scrum. register via /join"
        update.message.reply_text(reply)
        return
    if('master' not in scrum_master.keys()):
        reply = "No one is da scrum master"
    else:
        reply = f"{scrum_members[scrum_master['master']]['name']} is da scrum master"

    update.message.reply_text(reply)

def estimate(update: Update, context: CallbackContext):
    chat_id = str(update.message.chat.id)
    if(not check_id(chat_id)):
        reply = "You are not in the scrum. register via /join"
        update.message.reply_text(reply)
        return
    if('master' not in scrum_master.keys()):
        reply = "This feature is for the scrum master"
        update.message.reply_text(reply)
    else:
        if chat_id != scrum_master['master']:
            reply = "This feature is for the scrum master"
            update.message.reply_text(reply)
        else:
            reply = f"Request for estimate. input user story name:\n\n`/u [user story name]`"
            modes['u'] = True
            api_req = f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&parse_mode=Markdown&text={reply}'
            requests.get(api_req)


def estimate_2(update: Update, context: CallbackContext):
    chat_id = str(update.message.chat.id)

    if not modes['u']:
        return

    if(not check_id(chat_id)):
        reply = "You are not in the scrum. register via /join"
        update.message.reply_text(reply)
        return
    if('master' not in scrum_master.keys()):
        reply = "This feature is for the scrum master"
        update.message.reply_text(reply)
    else:
        if chat_id != scrum_master['master']:
            reply = "This feature is for the scrum master"
            update.message.reply_text(reply)
        else:
            reply = f"Asked scrum members for estimate of {update.message.text[3:]}. Waiting for everyone's reply"
            update.message.reply_text(reply)
            modes['u'] = False
            modes['e'] = True
            modes['n'] = update.message.text[3:]
            message = f"Scrum master wants your estimate for `{update.message.text[3:]}`.\nFibonacci suggestion: 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377\nReply with:\n\n`/e [estimatevalue]`"
            for cid in scrum_members.keys():
                scrum_members[cid]['estimate'] = ""
                api_req = f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={cid}&parse_mode=Markdown&text={message}'
                requests.get(api_req)

def give_estimate(update: Update, context: CallbackContext):
    
    chat_id = str(update.message.chat.id)

    if not modes['e']:
        return

    if(not check_id(chat_id)):
        reply = "You are not in the scrum. register via /join"
        update.message.reply_text(reply)
        return
    scrum_members[chat_id]['estimate'] = update.message.text[3:]
    reply =  f"Estimate for {modes['n']} submitted, waiting for others"
    update.message.reply_text(reply)

    for cid in scrum_members.keys():
        if(scrum_members[cid]['estimate'] == ""):
            return

    message = f"Everyone has submitted estimate!\n`{modes['n']}`\n"
    modes['e'] = False
    modes['n'] = ""
    for cid in scrum_members.keys():
        message += f"\n{scrum_members[cid]['name']}: {scrum_members[cid]['estimate']}"

    for cid in scrum_members.keys():
        api_req = f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={cid}&parse_mode=Markdown&text={message}'
        scrum_members[cid]['estimate'] = ""
        requests.get(api_req)

def scrum(update: Update, context: CallbackContext):
    chat_id = str(update.message.chat.id)
    if(not check_id(chat_id)):
        reply = "You are not in the scrum. register via /join"
        update.message.reply_text(reply)
        return
    reply = f"Scrum members:"
    for cid in scrum_members.keys():
        reply += f"\n{scrum_members[cid]['name']}"
    update.message.reply_text(reply)
    

if __name__ == '__main__':

    updater = Updater(bot_token, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("join", start_command))
    dispatcher.add_handler(CommandHandler("scrum", scrum))
    dispatcher.add_handler(CommandHandler("bemaster", be_master))
    dispatcher.add_handler(CommandHandler("whomaster", who_master))
    dispatcher.add_handler(CommandHandler("estimate", estimate))
    dispatcher.add_handler(CommandHandler("u", estimate_2))
    dispatcher.add_handler(CommandHandler("e", give_estimate))

    updater.start_polling()
    updater.idle()