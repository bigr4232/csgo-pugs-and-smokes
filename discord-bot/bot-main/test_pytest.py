import pytest
import command_sender
import databaseHandler
import asyncio

@pytest.mark.asyncio
async def testNumPlayers():
    numplayers = await command_sender.getNumPlayers()
    return

@pytest.mark.asyncio
async def testAddServer():
    await databaseHandler.addServer('70.1.1.1', 'Arizona', '***REMOVED***')