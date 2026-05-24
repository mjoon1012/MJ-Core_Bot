import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
import database  # 데이터베이스 모듈

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
    # DB 초기화 및 슬래시 명령어 동기화
    database.init_db()
    await bot.tree.sync() 
    print(f'{bot.user}으로 로그인 완료 및 슬래시 명령어 동기화 성공!')

# 슬래시 명령어: /포인트 (관리자용)
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
    if action == "추가":
        database.update_xp(member.id, amount)
        await interaction.response.send_message(f"✅ {member.display_name}님에게 {amount} XP를 추가했습니다!")
    elif action == "제거":
        database.update_xp(member.id, -amount)
        await interaction.response.send_message(f"❌ {member.display_name}님의 XP를 {amount}만큼 차감했습니다.")

# 슬래시 명령어: /내정보 (사용자용)
@bot.tree.command(name="내정보", description="나의 현재 레벨과 경험치를 확인합니다.")
async def 내정보(interaction: discord.Interaction):
    user_id = interaction.user.id
    row = database.get_user_xp(user_id)
    
    if row is None:
        await interaction.response.send_message(
            "⚠️ 아직 적립된 포인트가 없습니다! 서버 활동을 통해 경험치를 쌓아보세요.", 
            ephemeral=True
        )
    else:
        xp, level = row
        await interaction.response.send_message(
            f"👤 **{interaction.user.display_name}님의 정보**\n"
            f"📈 레벨: {level}\n"
            f"✨ 현재 경험치: {xp} XP"
        )

# 슬래시 명령어: /핑
@bot.tree.command(name="핑", description="봇의 응답 속도를 확인합니다.")
async def 핑(interaction: discord.Interaction):
    await interaction.response.send_message('Pong!')

# 봇 실행
bot.run(TOKEN)