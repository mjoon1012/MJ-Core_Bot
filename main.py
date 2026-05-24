import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import database  # 위에서 만든 데이터베이스 모듈 불러오기

# .env 파일에서 토큰 로드
load_dotenv()
TOKEN = os.getenv('TOKEN')

# 인텐트 설정
intents = discord.Intents.default()
intents.message_content = True

# 봇 객체 생성
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    database.init_db()  # 봇이 켜질 때 DB 테이블 생성
    print(f'{bot.user}으로 로그인되었습니다!')
    print('데이터베이스가 연결되었습니다.')

# 간단한 명령어: !ping
@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

# 포인트 관리 명령어: !포인트 [@유저] [추가/제거] [XP]
@bot.command()
async def 포인트(ctx, member: discord.Member, action: str, amount: int):
    if action == "추가":
        database.update_xp(member.id, amount)
        await ctx.send(f"✅ {member.display_name}님에게 {amount} XP를 추가했습니다!")
    elif action == "제거":
        database.update_xp(member.id, -amount)
        await ctx.send(f"❌ {member.display_name}님의 XP를 {amount}만큼 차감했습니다.")
    else:
        await ctx.send("⚠️ 명령어 형식 오류: `!포인트 @유저 추가 100` 또는 `!포인트 @유저 제거 50`")

# 봇 실행
bot.run(TOKEN)