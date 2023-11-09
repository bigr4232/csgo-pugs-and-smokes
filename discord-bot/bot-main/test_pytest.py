import pytest
import command_sender

@pytest.mark.asyncio
async def testNumPlayers():
    numplayers = await command_sender.getNumPlayers()
    return