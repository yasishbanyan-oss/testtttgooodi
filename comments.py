# GoodiBot modular feature module
from core import *

async def handle_automatic_channel_comments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or not getattr(msg, "is_automatic_forward", False):
        return

    chat = update.effective_chat
    if not chat or chat.type not in ["group", "supergroup"]:
        return

    db = load_db()
    g_data = get_group_data(db, chat.id)
    comment_settings = g_data.get("comment", {})

    if not comment_settings.get("enabled", False):
        return

    msg_key = f"{chat.id}_{msg.message_id}"
    commented_posts = db.setdefault("commented_channel_posts", [])
    if msg_key in commented_posts:
        return

    payload = comment_settings.get("payload")
    if not payload:
        return

    success = await send_media_payload(context.bot, chat.id, payload, reply_to_message_id=msg.message_id)
    if success:
        commented_posts.append(msg_key)
        if len(commented_posts) > 500:
            commented_posts.pop(0)
        mark_db_dirty()
        save_db()
