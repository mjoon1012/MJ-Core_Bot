import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
import database  # 기존에 만든 데이터베이스 모듈을 그대로 사용합니다.

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
    # 봇이 켜질 때 DB 초기화 및 슬래시 명령어 동기화
    database.init_db()
    await bot.tree.sync() 
    print(f'{bot.user}으로 로그인 완료 및 슬래시 명령어 동기화 성공!')

# 슬래시 명령어: /포인트
@bot.tree.command(name="포인트", description="유저의 경험치를 추가하거나 제거합니다.")
@app_commands.describe(
    member="대상 유저를 선택하세요",
    action="추가 또는 제거를 선택하세요",
    amount="수정할 경험치 양을 입력하세요"
)
@app_commands.choices(action=[
    app_commands.Choice(name="추가", value="추가"),
    app_commands.Choice(name="제거", value="제거")
])
async def 포인트(interaction: discord.Interaction, member: discord.Member, action: str, amount: int):
    # DB 작업 수행
    if action == "추가":
        database.update_xp(member.id, amount)
        await interaction.response.send_message(f"✅ {member.display_name}님에게 {amount} XP를 추가했습니다!")
    elif action == "제거":
        database.update_xp(member.id, -amount)
        await interaction.response.send_message(f"❌ {member.display_name}님의 XP를 {amount}만큼 차감했습니다.")

# 슬래시 명령어: /핑 (기존 !ping 대체)
@bot.tree.command(name="핑", description="봇의 응답 속도를 확인합니다.")
async def 핑(interaction: discord.Interaction):
    await interaction.response.send_message('Pong!')

# 봇 실행
bot.run(TOKEN)