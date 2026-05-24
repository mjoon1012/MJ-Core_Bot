import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# .env 파일에서 토큰 로드
load_dotenv()
TOKEN = os.getenv('TOKEN')

# 인텐트 설정 (봇이 서버의 메시지를 읽기 위해 필요)
intents = discord.Intents.default()
intents.message_content = True

# 봇 객체 생성
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user}으로 로그인되었습니다!')

# 간단한 명령어: !ping 입력 시 Pong! 응답
@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

# 봇 실행
bot.run(TOKEN)