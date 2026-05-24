import discord
from discord import app_commands
from discord.ext import commands
from typing import Literal, Optional # 추가
import os
from dotenv import load_dotenv
import database

load_dotenv()
TOKEN = os.getenv('TOKEN')

ROLE_IDS = {
    "인턴": 1505185632954220654,
    "사원": 1505185660137377832,
    "대리": 1505185684346896414,
    "과장": 1505185702789382196,
    "부장": 1505185721512755220
}

intents = discord.Intents.default()
intents.message_content = True
intents.members = True 

bot = commands.Bot(command_prefix='!', intents=intents)

# 직급 계산 로직을 별도 함수로 분리 (유지보수 용이)
def get_role_name(xp: int):
    if xp >= 400: return "부장"
    elif xp >= 300: return "과장"
    elif xp >= 200: return "대리"
    elif xp >= 100: return "사원"
    else: return "인턴"

async def check_role_upgrade(member: discord.Member, xp: int):
    role_name = get_role_name(xp)
    target_id = ROLE_IDS[role_name]
    
    target_role = member.guild.get_role(target_id)
    all_role_ids = list(ROLE_IDS.values())
    roles_to_remove = [r for r in member.roles if r.id in all_role_ids and r.id != target_id]
    
    await member.remove_roles(*roles_to_remove)
    if target_role not in member.roles:
        await member.add_roles(target_role)
    return role_name

@bot.event
async def on_ready():
    database.init_db()
    await bot.tree.sync()
    print(f'{bot.user} v0.6.0 로그인 완료!')

@bot.tree.command(name="포인트", description="유저의 경험치를 수정합니다.")
@app_commands.describe(action="추가 또는 제거를 선택하세요.", amount="변경할 포인트 양")
async def 포인트(interaction: discord.Interaction, member: discord.Member, action: Literal["추가", "제거"], amount: int):
    val = amount if action == "추가" else -amount
    new_xp, level = database.update_xp(member.id, val)
    role_name = await check_role_upgrade(member, new_xp)
    
    await interaction.response.send_message(
        f"✅ {member.display_name}님 업데이트 완료!\n"
        f"📈 레벨: {level} ({new_xp} XP) / 직급: **{role_name}**"
    )

@bot.tree.command(name="정보", description="나 혹은 다른 유저의 정보를 확인합니다.")
@app_commands.describe(member="정보를 확인할 유저 (생략 시 본인)")
async def 정보(interaction: discord.Interaction, member: Optional[discord.Member] = None):
    target = member or interaction.user
    row = database.get_user_xp(target.id)
    
    if not row:
        await interaction.response.send_message(f"{target.display_name}님은 아직 포인트 데이터가 없습니다.", ephemeral=True)
    else:
        xp, level = row
        role_name = get_role_name(xp)
        await interaction.response.send_message(
            f"👤 **{target.display_name}님의 정보**\n"
            f"📈 레벨: {level}\n"
            f"✨ 경험치: {xp} XP\n"
            f"🎖️ 직급: **{role_name}**"
        )

@bot.tree.command(name="핑", description="봇의 응답 속도 확인")
async def 핑(interaction: discord.Interaction):
    await interaction.response.send_message('Pong!')

bot.run(TOKEN)