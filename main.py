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

def get_role_data(xp: int):
    if xp >= 400: return "부장", discord.Color.gold()
    elif xp >= 300: return "과장", discord.Color.from_rgb(255, 165, 0)
    elif xp >= 200: return "대리", discord.Color.green()
    elif xp >= 100: return "사원", discord.Color.blue()
    else: return "인턴", discord.Color.light_gray()

def create_info_embed(target: discord.Member, xp: int, level: int):
    role_name, color = get_role_data(xp)
    current_level_xp = xp % 100
    progress = int(current_level_xp / 10)
    bar = "█" * progress + "░" * (10 - progress)
    
    embed = discord.Embed(title=f"👤 {target.display_name}님의 정보", color=color)
    embed.set_thumbnail(url=target.display_avatar.url)
    embed.add_field(name="📈 레벨", value=f"{level} 레벨", inline=True)
    embed.add_field(name="✨ 경험치", value=f"{xp} XP", inline=True)
    embed.add_field(name="🎖️ 직급", value=f"**{role_name}**", inline=False)
    embed.add_field(name="진행 상황", value=f"{bar} ({current_level_xp}/100 XP)", inline=False)
    return embed

class InfoButtonView(discord.ui.View):
    def __init__(self, target_member: discord.Member):
        super().__init__(timeout=60)
        self.target_member = target_member

    @discord.ui.button(label="상세 정보 확인", style=discord.ButtonStyle.primary)
    async def get_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        row = database.get_user_xp(self.target_member.id)
        if not row:
            await interaction.response.send_message("데이터가 없습니다.", ephemeral=True)
            return
        xp, level = row
        embed = create_info_embed(self.target_member, xp, level)
        await interaction.response.send_message(embed=embed)

async def check_role_upgrade(member: discord.Member, xp: int):
    role_name, _ = get_role_data(xp)
    target_id = ROLE_IDS[role_name]
    target_role = member.guild.get_role(target_id)
    all_role_ids = list(ROLE_IDS.values())
    roles_to_remove = [r for r in member.roles if r.id in all_role_ids and r.id != target_id]
    await member.remove_roles(*roles_to_remove)
    if target_role and target_role not in member.roles:
        await member.add_roles(target_role)
    return role_name

@bot.event
async def on_ready():
    database.init_db()
    await bot.tree.sync()
    print(f'{bot.user} v1.0.0 로그인 완료!')

@bot.tree.command(name="포인트", description="유저의 경험치를 수정합니다.")
async def 포인트(interaction: discord.Interaction, member: discord.Member, action: Literal["추가", "제거"], amount: int):
    val = amount if action == "추가" else -amount
    new_xp, level = database.update_xp(member.id, val)
    role_name = await check_role_upgrade(member, new_xp)
    embed = discord.Embed(title="💰 포인트 업데이트 완료", description=f"{member.mention}님 포인트 적용 완료.", color=discord.Color.green())
    embed.add_field(name="결과", value=f"직급: **{role_name}** / XP: {new_xp}")
    await interaction.response.send_message(embed=embed, view=InfoButtonView(member))

@bot.tree.command(name="순위", description="서버 내 경험치 상위 10명을 확인합니다.")
async def 순위(interaction: discord.Interaction):
    top_users = database.get_top_users(limit=10)
    if not top_users:
        await interaction.response.send_message("아직 데이터가 없습니다.", ephemeral=True)
        return
    embed = discord.Embed(title="🏆 MJ-Core 서버 경험치 순위", color=discord.Color.gold())
    for i, (user_id, xp, level) in enumerate(top_users, start=1):
        member = interaction.guild.get_member(user_id)
        name = member.display_name if member else f"유저_{user_id}"
        role_name, _ = get_role_data(xp)
        embed.add_field(name=f"{i}위. {name}", value=f"직급: **{role_name}** | {xp} XP", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="정보", description="정보 조회")
async def 정보(interaction: discord.Interaction, member: Optional[discord.Member] = None):
    target = member or interaction.user
    row = database.get_user_xp(target.id)
    if not row:
        await interaction.response.send_message("데이터 없음", ephemeral=True)
        return
    await interaction.response.send_message(embed=create_info_embed(target, row[0], row[1]))

bot.run(TOKEN)