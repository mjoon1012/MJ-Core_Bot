import discord
from discord import app_commands
from discord.ext import commands
from typing import Literal, Optional
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

# 직급 및 색상 정의
def get_role_data(xp: int):
    if xp >= 400: return "부장", discord.Color.gold()
    elif xp >= 300: return "과장", discord.Color.from_rgb(255, 165, 0) # 오렌지
    elif xp >= 200: return "대리", discord.Color.green()
    elif xp >= 100: return "사원", discord.Color.blue()
    else: return "인턴", discord.Color.light_gray()

async def check_role_upgrade(member: discord.Member, xp: int):
    role_name, _ = get_role_data(xp)
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
    print(f'{bot.user} v0.7.0 로그인 완료!')

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

@bot.tree.command(name="정보", description="나 혹은 다른 유저의 정보를 깔끔하게 확인합니다.")
async def 정보(interaction: discord.Interaction, member: Optional[discord.Member] = None):
    target = member or interaction.user
    row = database.get_user_xp(target.id)
    
    if not row:
        await interaction.response.send_message("데이터 없음", ephemeral=True)
        return

    xp, level = row
    role_name, color = get_role_data(xp)
    
    # 진행 바 계산 (100XP당 1레벨 가정)
    current_level_xp = xp % 100
    progress = int(current_level_xp / 10) # 10칸짜리 바
    bar = "█" * progress + "░" * (10 - progress)
    
    embed = discord.Embed(
        title=f"👤 {target.display_name}님의 정보",
        color=color
    )
    embed.set_thumbnail(url=target.display_avatar.url)
    embed.add_field(name="📈 레벨", value=f"{level} 레벨", inline=True)
    embed.add_field(name="✨ 경험치", value=f"{xp} XP", inline=True)
    embed.add_field(name="🎖️ 직급", value=f"**{role_name}**", inline=False)
    embed.add_field(name="진행 상황", value=f"{bar} ({current_level_xp}/100 XP)", inline=False)
    embed.set_footer(text=f"MJ-Core v0.7.0 | {interaction.user.display_name}님 요청")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="핑", description="봇의 응답 속도 확인")
async def 핑(interaction: discord.Interaction):
    await interaction.response.send_message('Pong!')

bot.run(TOKEN)