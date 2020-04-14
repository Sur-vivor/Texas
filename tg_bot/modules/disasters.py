import html
import json
import html
import os
from typing import List, Optional

from telegram import Bot, Update, ParseMode, TelegramError
from telegram.ext import CommandHandler, run_async
from telegram.utils.helpers import mention_html

from tg_bot import dispatcher, WHITELIST_USERS, B_USERS, SUPPORT_USERS, SUDO_USERS, DEV_USERS, OWNER_ID
from tg_bot.modules.helper_funcs.chat_status import whitelist_plus, dev_plus, sudo_plus
from tg_bot.modules.helper_funcs.extraction import extract_user
from tg_bot.modules.log_channel import gloggable

ELEVATED_USERS_FILE = os.path.join(os.getcwd(), 'tg_bot/elevated_users.json')


def check_user_id(user_id: int, bot: Bot) -> Optional[str]:
    if not user_id:
        reply = "That...is a chat! baka ka omae?"

    elif user_id == bot.id:
        reply = "This does not work that way."

    else:
        reply = None
    return reply

#I added extra new lines 
tiers = """ Texas has bot access levels we call as *"Tier Levels"*
\n*Penguin Logistics* - Devs who can access the bots server and can execute, edit, modify bot code. Can also manage other Tiers
\n*God* - Only one exists, bot owner. 
Owner has complete bot access, including bot adminship in chats Texas is at.
\n*S* - Have super user access, can gban, manage tiers lower than them and are admins in Texas.
\n*A* - Have access go globally ban users across Texas.
\n*B* - Same as C but can unban themselves if banned.
\n*C* - Cannot be banned, muted flood kicked but can be manually banned by admins.
\n*Disclaimer*: The tier levels in Texas are there for troubleshooting, support, banning potential scammers.
Report abuse or ask us more on these at [Heroes Association](https://t.me/texassupport).
"""
# do not async, not a handler 
def send_tiers(update):
   update.effective_message.reply_text(tiers, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

@run_async
@dev_plus
@gloggable
def addsudo(bot: Bot, update: Update, args: List[str]) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)
    rt = ""

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, 'r') as infile:
        data = json.load(infile)

    if user_id in SUDO_USERS:
        message.reply_text("This member is already a S Tier")
        return ""

    if user_id in SUPPORT_USERS:
        rt += "Requested HA to promote a Demon Tier to S."
        data['supports'].remove(user_id)
        SUPPORT_USERS.remove(user_id)

    if user_id in WHITELIST_USERS:
        rt += "Requested HA to promote a Wolf Tier to S."
        data['whitelists'].remove(user_id)
        WHITELIST_USERS.remove(user_id)

    data['sudos'].append(user_id)
    SUDO_USERS.append(user_id)

    with open(ELEVATED_USERS_FILE, 'w') as outfile:
        json.dump(data, outfile, indent=4)

    update.effective_message.reply_text(
        rt + "\nSuccessfully set Tier level of {} to S!".format(user_member.first_name))

    log_message = (f"#SUDO\n"
                   f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                   f"<b>User:</b> {mention_html(user_member.id, user_member.first_name)}")

    if chat.type != 'private':
        log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

    return log_message


@run_async
@sudo_plus
@gloggable
def addsupport(bot: Bot, update: Update, args: List[str]) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)
    rt = ""

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, 'r') as infile:
        data = json.load(infile)

    if user_id in SUDO_USERS:
        rt += "Requested HA to deomote this S to Demon"
        data['sudos'].remove(user_id)
        SUDO_USERS.remove(user_id)

    if user_id in SUPPORT_USERS:
        message.reply_text("This user is already a Demon Tier.")
        return ""

    if user_id in WHITELIST_USERS:
        rt += "Requested HA to promote this Wolf Tier to Demon"
        data['whitelists'].remove(user_id)
        WHITELIST_USERS.remove(user_id)

    data['supports'].append(user_id)
    SUPPORT_USERS.append(user_id)

    with open(ELEVATED_USERS_FILE, 'w') as outfile:
        json.dump(data, outfile, indent=4)

    update.effective_message.reply_text(rt + f"\n{user_member.first_name} was added as a Demon Tier!")

    log_message = (f"#SUPPORT\n"
                   f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                   f"<b>User:</b> {mention_html(user_member.id, user_member.first_name)}")

    if chat.type != 'private':
        log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

    return log_message


@run_async
@sudo_plus
@gloggable
def addwhitelist(bot: Bot, update: Update, args: List[str]) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)
    rt = ""

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, 'r') as infile:
        data = json.load(infile)

    if user_id in SUDO_USERS:
        rt += "This member is a S Tier, Demoting to Wolf."
        data['sudos'].remove(user_id)
        SUDO_USERS.remove(user_id)

    if user_id in SUPPORT_USERS:
        rt += "This user is already a Demon Tier, Demoting to Wolf."
        data['supports'].remove(user_id)
        SUPPORT_USERS.remove(user_id)

    if user_id in WHITELIST_USERS:
        message.reply_text("This user is already a Wolf Tier.")
        return ""

    data['whitelists'].append(user_id)
    WHITELIST_USERS.append(user_id)

    with open(ELEVATED_USERS_FILE, 'w') as outfile:
        json.dump(data, outfile, indent=4)

    update.effective_message.reply_text(
        rt + f"\nSuccessfully promoted {user_member.first_name} to a Wolf Tier!")

    log_message = (f"#WHITELIST\n"
                   f"<b>Admin:</b> {mention_html(user.id, user.first_name)} \n"
                   f"<b>User:</b> {mention_html(user_member.id, user_member.first_name)}")

    if chat.type != 'private':
        log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

    return log_message


@run_async
@sudo_plus
@gloggable
def addB(bot: Bot, update: Update, args: List[str]) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)
    rt = ""

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, 'r') as infile:
        data = json.load(infile)

    if user_id in SUDO_USERS:
        rt += "This member is a S Tier, Demoting to B."
        data['sudos'].remove(user_id)
        SUDO_USERS.remove(user_id)

    if user_id in SUPPORT_USERS:
        rt += "This user is already a Demon Tier, Demoting to B."
        data['supports'].remove(user_id)
        SUPPORT_USERS.remove(user_id)

    if user_id in WHITELIST_USERS:
        rt += "This user is already a Wolf Tier, Demoting to B."
        data['whitelists'].remove(user_id)
        WHITELIST_USERS.remove(user_id)

    if user_id in B_USERS:
        message.reply_text("This user is already a B.")
        return ""

    data['B'].append(user_id)
    B_USERS.append(user_id)

    with open(ELEVATED_USERS_FILE, 'w') as outfile:
        json.dump(data, outfile, indent=4)

    update.effective_message.reply_text(
        rt + f"\nSuccessfully promoted {user_member.first_name} to a B Tier!")

    log_message = (f"#B\n"
                   f"<b>Admin:</b> {mention_html(user.id, user.first_name)} \n"
                   f"<b>User:</b> {mention_html(user_member.id, user_member.first_name)}")

    if chat.type != 'private':
        log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

    return log_message


@run_async
@dev_plus
@gloggable
def addB(bot: Bot, update: Update, args: List[str]) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)
    rt = ""

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, 'r') as infile:
        data = json.load(infile)

    if user_id in SUDO_USERS:
        rt += "This member is a S Tier, Demoting to B."
        data['sudos'].remove(user_id)
        SUDO_USERS.remove(user_id)

    if user_id in SUPPORT_USERS:
        rt += "This user is already a Demon Tier, Demoting to B."
        data['supports'].remove(user_id)
        SUPPORT_USERS.remove(user_id)

    if user_id in WHITELIST_USERS:
        rt += "This user is already a Wolf Tier, Demoting to B."
        data['whitelists'].remove(user_id)
        WHITELIST_USERS.remove(user_id)

    if user_id in B_USERS:
        message.reply_text("This user is already a B.")
        return ""

    data['B'].append(user_id)
    B_USERS.append(user_id)

    with open(ELEVATED_USERS_FILE, 'w') as outfile:
        json.dump(data, outfile, indent=4)

    update.effective_message.reply_text(
        rt + f"\nSuccessfully promoted {user_member.first_name} to a B Tier!")

    log_message = (f"#B\n"
                   f"<b>Admin:</b> {mention_html(user.id, user.first_name)} \n"
                   f"<b>User:</b> {mention_html(user_member.id, user_member.first_name)}")

    if chat.type != 'private':
        log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

    return log_message


@run_async
@dev_plus
@gloggable
def removesudo(bot: Bot, update: Update, args: List[str]) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, 'r') as infile:
        data = json.load(infile)

    if user_id in SUDO_USERS:
        message.reply_text("Requested HA to demote this user to Civilian")
        SUDO_USERS.remove(user_id)
        data['sudos'].remove(user_id)

        with open(ELEVATED_USERS_FILE, 'w') as outfile:
            json.dump(data, outfile, indent=4)

        log_message = (f"#UNSUDO\n"
                       f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                       f"<b>User:</b> {mention_html(user_member.id, user_member.first_name)}")

        if chat.type != 'private':
            log_message = "<b>{}:</b>\n".format(html.escape(chat.title)) + log_message

        return log_message

    else:
        message.reply_text("This user is not a S Tier!")
        return ""


@run_async
@sudo_plus
@gloggable
def removesupport(bot: Bot, update: Update, args: List[str]) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, 'r') as infile:
        data = json.load(infile)

    if user_id in SUPPORT_USERS:
        message.reply_text("Requested HA to demote this user to Civilian")
        SUPPORT_USERS.remove(user_id)
        data['supports'].remove(user_id)

        with open(ELEVATED_USERS_FILE, 'w') as outfile:
            json.dump(data, outfile, indent=4)

        log_message = (f"#UNSUPPORT\n"
                       f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                       f"<b>User:</b> {mention_html(user_member.id, user_member.first_name)}")

        if chat.type != 'private':
            log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

        return log_message

    else:
        message.reply_text("This user is not a Demon level Tier!")
        return ""


@run_async
@sudo_plus
@gloggable
def removewhitelist(bot: Bot, update: Update, args: List[str]) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, 'r') as infile:
        data = json.load(infile)

    if user_id in WHITELIST_USERS:
        message.reply_text("Demoting to normal user")
        WHITELIST_USERS.remove(user_id)
        data['whitelists'].remove(user_id)

        with open(ELEVATED_USERS_FILE, 'w') as outfile:
            json.dump(data, outfile, indent=4)

        log_message = (f"#UNWHITELIST\n"
                       f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                       f"<b>User:</b> {mention_html(user_member.id, user_member.first_name)}")

        if chat.type != 'private':
            log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

        return log_message
    else:
        message.reply_text("This user is not a Wolf Tier!")
        return ""


@run_async
@sudo_plus
@gloggable
def removeB(bot: Bot, update: Update, args: List[str]) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, 'r') as infile:
        data = json.load(infile)

    if user_id in B_USERS:
        message.reply_text("Demoting to normal user")
        B_USERS.remove(user_id)
        data['B'].remove(user_id)

        with open(ELEVATED_USERS_FILE, 'w') as outfile:
            json.dump(data, outfile, indent=4)

        log_message = (f"#UNB\n"
                       f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                       f"<b>User:</b> {mention_html(user_member.id, user_member.first_name)}")

        if chat.type != 'private':
            log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

        return log_message
    else:
        message.reply_text("This user is not a B Tier!")
        return ""


@run_async
@whitelist_plus
def whitelistlist(bot: Bot, update: Update):
    reply = "<b>Known Wolf Tiers 🐺:</b>\n"
    for each_user in WHITELIST_USERS:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)

            reply += f"• {mention_html(user_id, user.first_name)}\n"
        except TelegramError:
            pass
    update.effective_message.reply_text(reply, parse_mode=ParseMode.HTML)


@run_async
@whitelist_plus
def Blist(bot: Bot, update: Update):
    reply = "<b>Known B Tiers 🐯:</b>\n"
    for each_user in B_USERS:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, user.first_name)}\n"
        except TelegramError:
            pass
    update.effective_message.reply_text(reply, parse_mode=ParseMode.HTML)


@run_async
@whitelist_plus
def supportlist(bot: Bot, update: Update):
    reply = "<b>Known Demon Tiers 👹:</b>\n"
    for each_user in SUPPORT_USERS:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, user.first_name)}\n"
        except TelegramError:
            pass
    update.effective_message.reply_text(reply, parse_mode=ParseMode.HTML)


@run_async
@whitelist_plus
def sudolist(bot: Bot, update: Update):
    true_sudo = list(set(SUDO_USERS) - set(DEV_USERS))
    reply = "<b>Known S Tiers 🐉:</b>\n"
    for each_user in true_sudo:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, user.first_name)}\n"
        except TelegramError:
            pass
    update.effective_message.reply_text(reply, parse_mode=ParseMode.HTML)


@run_async
@whitelist_plus
def devlist(bot: Bot, update: Update):
    true_dev = list(set(DEV_USERS) - {OWNER_ID})
    reply = "<b>Hero Association Members ⚡️:</b>\n"
    for each_user in true_dev:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, user.first_name)}\n"
        except TelegramError:
            pass
    update.effective_message.reply_text(reply, parse_mode=ParseMode.HTML)


__help__ = """
 - /heroes - Lists all Hero Association members.
 - /S - Lists all S tiers.
 - /A - Lists all Demon tiers.
 - /B - Lists all B tiers.
 - /C - Lists all Wolf tiers.
 Note: These commands list users with special bot priveleges and can only be used by them.
 You can visit @texassupport to query more about these.
"""

SUDO_HANDLER = CommandHandler(("addsudo", "addS"), addsudo, pass_args=True)
SUPPORT_HANDLER = CommandHandler(("addsupport", "adddemon"), addsupport, pass_args=True)
B_HANDLER = CommandHandler(("addB"), addB, pass_args=True)
WHITELIST_HANDLER = CommandHandler(("addwhitelist", "addwolf"), addwhitelist, pass_args=True)
UNSUDO_HANDLER = CommandHandler(("removesudo", "removeS"), removesudo, pass_args=True)
UNSUPPORT_HANDLER = CommandHandler(("removesupport", "removedemon"), removesupport, pass_args=True)
UNB_HANDLER = CommandHandler(("removeB"), removeB, pass_args=True)
UNWHITELIST_HANDLER = CommandHandler(("removewhitelist", "removewolf"), removewhitelist, pass_args=True)

WHITELISTLIST_HANDLER = CommandHandler(["whitelistlist", "C"], whitelistlist)
BLIST_HANDLER = CommandHandler(["B"], Blist)
SUPPORTLIST_HANDLER = CommandHandler(["supportlist", "A"], supportlist)
SUDOLIST_HANDLER = CommandHandler(["sudolist", "S"], sudolist)
DEVLIST_HANDLER = CommandHandler(["devlist", "heroes"], devlist)

dispatcher.add_handler(SUDO_HANDLER)
dispatcher.add_handler(SUPPORT_HANDLER)
dispatcher.add_handler(B_HANDLER)
dispatcher.add_handler(WHITELIST_HANDLER)
dispatcher.add_handler(UNSUDO_HANDLER)
dispatcher.add_handler(UNSUPPORT_HANDLER)
dispatcher.add_handler(UNB_HANDLER)
dispatcher.add_handler(UNWHITELIST_HANDLER)

dispatcher.add_handler(WHITELISTLIST_HANDLER)
dispatcher.add_handler(BLIST_HANDLER)
dispatcher.add_handler(SUPPORTLIST_HANDLER)
dispatcher.add_handler(SUDOLIST_HANDLER)
dispatcher.add_handler(DEVLIST_HANDLER)

__mod_name__ = "Tiers"
__handlers__ = [SUDO_HANDLER, SUPPORT_HANDLER, B_HANDLER, WHITELIST_HANDLER, 
                UNSUDO_HANDLER, UNSUPPORT_HANDLER, UNB_HANDLER, UNWHITELIST_HANDLER,
                WHITELISTLIST_HANDLER, BLIST_HANDLER, SUPPORTLIST_HANDLER,
                SUDOLIST_HANDLER, DEVLIST_HANDLER]
