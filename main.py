import asyncio
import logging
import threading
import time
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler

from pyrogram import Client

from info import API_ID, API_HASH, BOT_TOKEN, ADMIN_ID, FREE_PROPERTY_DURATION_HOURS
from database.db import db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

app = Client(
    "SpideyShareBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="plugins"),
    workers=200,
)


# Health check server for Koyeb
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress health check logs
        if '/health' not in format:
            logging.info(f"Health check: {format % args}")


def run_health_server():
    """Run a simple HTTP server for health checks on port 8000"""
    try:
        server = HTTPServer(('0.0.0.0', 8000), HealthCheckHandler)
        logging.info("🩺 Health check server running on port 8000")
        server.serve_forever()
    except Exception as e:
        logging.error(f"Health check server error: {e}")


# Auto-cleanup function for expired free properties
def auto_cleanup_expired_properties():
    """Background thread to remove expired free listings"""
    while True:
        try:
            # Delete expired free properties
            deleted_count = asyncio.run_coroutine_threadsafe(
                db.delete_expired_properties(FREE_PROPERTY_DURATION_HOURS),
                app.loop
            ).result()
            
            if deleted_count > 0:
                logging.info(f"🗑️ Auto-removed {deleted_count} expired free listings")
                
                # Notify admin about auto-removal
                asyncio.run_coroutine_threadsafe(
                    app.send_message(
                        ADMIN_ID,
                        f"🗑️ **Auto-Cleanup Report**\n\n"
                        f"Removed {deleted_count} expired free listings.\n"
                        f"⏰ Expiry period: {FREE_PROPERTY_DURATION_HOURS} hours\n"
                        f"🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    ),
                    app.loop
                ).result()
            
            # Also check for premium expirations and notify users
            asyncio.run_coroutine_threadsafe(
                check_premium_expirations(),
                app.loop
            ).result()
            
            time.sleep(3600)  # Check every hour
            
        except Exception as e:
            logging.error(f"Auto-cleanup error: {e}")
            time.sleep(60)


async def check_premium_expirations():
    """Check for users whose premium is about to expire"""
    try:
        # Get users whose premium expires in less than 3 days
        three_days_later = datetime.utcnow() + timedelta(days=3)
        cursor = db.users.find({
            "premium_until": {"$gt": datetime.utcnow(), "$lt": three_days_later}
        })
        
        async for user in cursor:
            user_id = user.get('user_id')
            if user_id:
                try:
                    await app.send_message(
                        user_id,
                        f"⚠️ **Premium Expiring Soon!**\n\n"
                        f"Your premium subscription will expire on:\n"
                        f"📅 {user['premium_until'].strftime('%Y-%m-%d %H:%M')}\n\n"
                        f"Renew now to continue enjoying premium benefits!\n"
                        f"Contact @Spidey2189 to renew."
                    )
                except Exception:
                    pass
    except Exception as e:
        logging.error(f"Premium expiration check error: {e}")


async def boot():
    """Initialize bot on startup"""
    await db.ensure_default_categories()
    
    me = await app.get_me()
    logging.info(f"{me.first_name} (@{me.username}) is up and running — dev @Spidey2189")
    
    # Send startup notification to admin
    try:
        await app.send_message(
            ADMIN_ID,
            f"🤖 **Bot Started Successfully!**\n\n"
            f"📌 Name: {me.first_name}\n"
            f"📌 Username: @{me.username}\n"
            f"📌 ID: {me.id}\n\n"
            f"⚙️ **Features Active:**\n"
            f"✅ Verification system\n"
            f"✅ Premium subscriptions\n"
            f"✅ Auto-removal ({FREE_PROPERTY_DURATION_HOURS} hours)\n"
            f"✅ Admin approval system\n"
            f"✅ Auto-cleanup thread running\n\n"
            f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
    except Exception as e:
        logging.error(f"Failed to send startup message to admin: {e}")


if __name__ == "__main__":
    # Start the health check server in a separate thread
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()
    logging.info("🩺 Health check server thread started")
    
    # Start the auto-cleanup thread
    cleanup_thread = threading.Thread(target=auto_cleanup_expired_properties, daemon=True)
    cleanup_thread.start()
    logging.info("🔄 Auto-cleanup thread started")
    
    async def main():
        await app.start()
        await boot()
        await asyncio.Event().wait()  # run forever

    try:
        asyncio.get_event_loop().run_until_complete(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped")
