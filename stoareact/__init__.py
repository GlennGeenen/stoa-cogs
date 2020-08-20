"""Package for Stoa-Cogs."""
from .stoareact import StoaReact

async def setup(bot):
    """Load StoaReact."""
    bot.add_cog(StoaReact(bot))
