import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
import database

load_dotenv()
TOKEN = os.getenv('TOKEN')

# 역할 ID 설정
ROLE_IDS = {
    "인턴": 1505185632954220654,
    "사원": 1505185660137377832,
    "대리": 1505185684346896414,
    "과장": 1505185702789382196,
    "부장": 1505185721512755220
}

# 인텐트 설정 (멤버 권한 필수!)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True 

bot = commands.Bot(command_prefix='!', intents=intents)

# 승급 체크 함수 (여기에 정의해야 합니다)
async def check_role_upgrade(member: discord.Member, xp: int):
    if xp >= 400: target_id = ROLE_IDS["부장"]
    elif xp >= 300: target_id = ROLE_IDS["과장"]
    elif xp >= 200: target_id = ROLE_IDS["대리"]
    elif xp >= 100: target_id = ROLE_IDS["사원"]
    else: target_id = ROLE_IDS["인턴"]
    
    target_role = member.guild.get_role(target_id)
    # 기존 역할 제거 (모든 직급 역할)
    all_role_ids = list(ROLE_IDS.values())
    roles_to_remove = [r for r in member.roles if r.id in all_role_ids and r.id != target_id]
    
    await member.remove_roles(*roles_to_remove)
    if target_role not in member.roles:
        await member.add_roles(target_role)
    return target_role.name

@bot.event
async def on_ready():
    database.init_db()
    await bot.tree.sync()
    print(f'{bot.user} 로그인 완료!')

@bot.tree.command(name="포인트", description="유저의 경험치를 수정하고 자동 승급합니다.")
async def 포인트(interaction: discord.Interaction, member: discord.Member, action: str, amount: int):
    val = amount if action == "추가" else -amount
    new_xp, level = database.update_xp(member.id, val)
    role_name = await check_role_upgrade(member, new_xp)
    
    await interaction.response.send_message(
        f"✅ {member.display_name}님 업데이트 완료!\n"
        f"📈 레벨: {level} ({new_xp} XP) / 직급: **{role_name}**"
    )

@bot.tree.command(name="내정보", description="나의 현재 레벨과 직급을 확인합니다.")
async def 내정보(interaction: discord.Interaction):
    row = database.get_user_xp(interaction.user.id)
    if not row:
        await interaction.response.send_message("아직 포인트가 없습니다.", ephemeral=True)
    else:
        xp, level = row
        # 현재 직급 이름 찾기
        role_name = "인턴"
        if xp >= 400: role_name = "부장"
        elif xp >= 300: role_name = "과장"
        elif xp >= 200: role_name = "대리"
        elif xp >= 100: role_name = "사원"
        
        await interaction.response.send_message(f"👤 **{interaction.user.display_name}님의 정보**\n📈 레벨: {level}\n✨ 경험치: {xp} XP\n🎖️ 직급: **{role_name}**")

@bot.tree.command(name="핑", description="봇의 응답 속도 확인")
async def 핑(interaction: discord.Interaction):
    await interaction.response.send_message('Pong!')

bot.run(TOKEN)