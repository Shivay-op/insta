import json
import os
import threading
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from telebot.apihelper import ApiTelegramException

from config import ADMIN_ID, DATA_DIR

USERS_FILE = os.path.join(DATA_DIR, "users.json")
REMOVED_FILE = os.path.join(DATA_DIR, "removed.json")

broadcast_running = False
broadcast_stop = False

broadcast_stats = {
    "total": 0,
    "success": 0,
    "failed": 0,
    "removed": 0,
    "pending": 0
}


def register(bot):

    @bot.message_handler(commands=["broadcast"])
    def broadcast(message):

        global broadcast_running
        global broadcast_stop
        global broadcast_stats

        if message.from_user.id != ADMIN_ID:
            bot.reply_to(
                message,
                "❌ You are not authorized."
            )
            return


        args = message.text.split()


        # /broadcast stop
        if len(args) > 1 and args[1].lower() == "stop":

            broadcast_stop = True

            bot.reply_to(
                message,
                "⏸ Broadcast stopping..."
            )
            return



        # /broadcast status
        if len(args) > 1 and args[1].lower() == "status":

            bot.reply_to(
                message,
                f"""
📊 Broadcast Status

👥 Total: {broadcast_stats['total']}

✅ Success: {broadcast_stats['success']}
🚫 Removed: {broadcast_stats['removed']}
❌ Failed: {broadcast_stats['failed']}
⏳ Pending: {broadcast_stats['pending']}

Running: {broadcast_running}
"""
            )
            return



        if broadcast_running:

            bot.reply_to(
                message,
                "⚠️ Broadcast already running."
            )
            return



        if not message.reply_to_message:

            bot.reply_to(
                message,
                "⚠️ Reply to a message and type /broadcast"
            )
            return



        try:

            with open(
                USERS_FILE,
                "r",
                encoding="utf-8"
            ) as f:

                users = json.load(f)


        except Exception as e:

            bot.reply_to(
                message,
                f"❌ active.json error:\n{e}"
            )
            return



        broadcast_running = True
        broadcast_stop = False


        broadcast_stats["total"] = len(users)
        broadcast_stats["success"] = 0
        broadcast_stats["failed"] = 0
        broadcast_stats["removed"] = 0
        broadcast_stats["pending"] = len(users)



        status = bot.reply_to(
            message,
            f"""
🚀 Broadcast Started

👥 Total: {len(users)}

✅ Success: 0
🚫 Removed: 0
❌ Failed: 0
"""
        )



        stop_live_update = threading.Event()


        def live_update():

            last_text = None

            while not stop_live_update.is_set():

                stop_live_update.wait(4)

                text = f"""
🚀 Broadcast Running

👥 Total: {broadcast_stats['total']}

✅ Success: {broadcast_stats['success']}
🚫 Removed: {broadcast_stats['removed']}
❌ Failed: {broadcast_stats['failed']}
⏳ Pending: {broadcast_stats['pending']}
"""

                if text == last_text:
                    continue

                try:
                    bot.edit_message_text(
                        text,
                        message.chat.id,
                        status.message_id
                    )

                    last_text = text

                except Exception as e:
                    print("Live update error:", e)


        updater_thread = threading.Thread(
            target=live_update,
            daemon=True
        )

        updater_thread.start()



        def move_removed(user, reason):

            try:

                with open(
                    REMOVED_FILE,
                    "r",
                    encoding="utf-8"
                ) as f:

                    removed = json.load(f)

            except:

                removed = []



            user["reason"] = reason
            user["date"] = str(datetime.now())


            if not any(
                u["id"] == user["id"]
                for u in removed
            ):

                removed.append(user)



            with open(
                REMOVED_FILE,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    removed,
                    f,
                    indent=4,
                    ensure_ascii=False
                )



        def send_copy(user):

            while True:


                if broadcast_stop:

                    return False



                try:

                    bot.copy_message(
                        chat_id=user["id"],
                        from_chat_id=message.chat.id,
                        message_id=message.reply_to_message.message_id
                    )


                    broadcast_stats["success"] += 1
                    broadcast_stats["pending"] -= 1


                    time.sleep(0.05)


                    return True



                except ApiTelegramException as e:


                    error = str(e).lower()



                    # Rate limit
                    if e.error_code == 429:
                        wait = (
                            e.result_json
                            .get(
                                "parameters",
                                {}
                            )
                            .get(
                                "retry_after",
                                5
                            )
                        )


                        time.sleep(
                            wait + 1
                        )


                        continue



                    # Blocked / deleted user

                    if (
                        "blocked" in error
                        or
                        "deactivated" in error
                        or
                        "chat not found" in error
                    ):


                        move_removed(
                            user,
                            error
                        )


                        broadcast_stats["removed"] += 1
                        broadcast_stats["pending"] -= 1


                        return False



                    broadcast_stats["failed"] += 1
                    broadcast_stats["pending"] -= 1

                    return False



                except Exception as e:

                    print(
                        "Broadcast error:",
                        e
                    )

                    broadcast_stats["failed"] += 1
                    broadcast_stats["pending"] -= 1

                    return False




        with ThreadPoolExecutor(
            max_workers=5
        ) as bcast_executor:


            jobs = []


            for user in users:


                if broadcast_stop:
                    break


                jobs.append(
                    bcast_executor.submit(
                        send_copy,
                        user
                    )
                )


                # avoid creating 25k jobs at once
                if len(jobs) >= 100:


                    for job in as_completed(jobs):

                        job.result()


                    jobs.clear()



        broadcast_running = False

        stop_live_update.set()
        updater_thread.join(timeout=5)



        bot.edit_message_text(
            f"""
✅ Broadcast Completed

👥 Total: {broadcast_stats['total']}

✅ Success: {broadcast_stats['success']}
🚫 Removed: {broadcast_stats['removed']}
❌ Failed: {broadcast_stats['failed']}
""",
            message.chat.id,
            status.message_id
        )
