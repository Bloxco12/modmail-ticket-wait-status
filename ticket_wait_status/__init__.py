from .ticket_wait_status import BotWaitStatus

async def setup(bot):
    await bot.add_cog(BotWaitStatus(bot))
