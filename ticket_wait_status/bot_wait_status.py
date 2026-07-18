import datetime
import discord
from discord.ext import commands, tasks

class BotWaitStatus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Start the background task to update the status every 60 seconds
        self.update_status_loop.start()

    def cog_unload(self):
        self.update_status_loop.cancel()

    @tasks.loop(seconds=60)
    async def update_status_loop(self):
        """Calculates average wait time for open tickets and sets it as the bot status."""
        await self.bot.wait_until_ready()
        
        active_threads = list(self.bot.thread_manager.cache.values())
        wait_times = []
        now = datetime.datetime.now(datetime.timezone.utc)

        for thread in active_threads:
            if not thread.channel:
                continue

            # Check the last message in each thread
            async for message in thread.channel.history(limit=1):
                # If a bot or staff member spoke last, the user isn't waiting.
                # Modmail checks changed_roles to identify staff members.
                if message.author.bot or any(role.id in [r.id for r in thread.channel.changed_roles] for role in message.author.roles):
                    continue
                
                # If a user spoke last, they are waiting for a response
                elapsed_seconds = (now - message.created_at).total_seconds()
                wait_times.append(elapsed_seconds)

        # Determine the activity text based on calculations
        if wait_times:
            avg_seconds = sum(wait_times) / len(wait_times)
            avg_minutes = int(avg_seconds / 60)
            
            # Format nicely (e.g., "Avg Wait: 14m" or "Avg Wait: <1m")
            wait_text = f"{avg_minutes}m" if avg_minutes > 0 else "<1m"
            status_message = f"Avg Wait: {wait_text} | {len(wait_times)} pending"
        else:
            status_message = "All tickets caught up! ✅"

        # Apply the activity to the bot's presence
        try:
            # Using CustomActivity to show text cleanly on the profile
            activity = discord.CustomActivity(name=status_message)
            await self.bot.change_presence(activity=activity)
        except Exception as e:
            self.bot.logger.error(f"Failed to update bot presence: {e}")

async def setup(bot):
    await bot.add_cog(BotWaitStatus(bot))
