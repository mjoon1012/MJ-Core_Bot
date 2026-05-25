import discord,os,asyncio,signal,database
from discord import app_commands
from discord.ext import commands
from typing import Literal,Optional
from dotenv import load_dotenv
load_dotenv()
TOKEN=os.getenv('TOKEN')
ROLE_IDS={"인턴":1505185632954220654,"사원":1505185660137377832,"대리":1505185684346896414,"과장":1505185702789382196,"부장":1505185721512755220}
intents=discord.Intents.default();intents.message_content=True;intents.members=True
bot=commands.Bot(command_prefix='!',intents=intents)
is_shutting_down=False;shutdown_event=asyncio.Event()
async def shutdown_bot():
 global is_shutting_down
 if is_shutting_down:return
 is_shutting_down=True;shutdown_event.set()
 print("\n[시스템] 봇을 안전하게 종료하는 중...")
 try:
  if hasattr(database,"close_connection"):database.close_connection()
  try:await asyncio.wait_for(bot.close(),timeout=5)
  except asyncio.TimeoutError:print("[경고] bot.close() timeout → 강제 종료 진행")
 except Exception as e:print(f"[시스템] 종료 중 오류 발생: {e}")
 finally:print("[시스템] 프로세스 종료");os._exit(0)
def get_role_data(xp:int):
 if xp>=400:return "부장",discord.Color.gold()
 elif xp>=300:return "과장",discord.Color.from_rgb(255,165,0)
 elif xp>=200:return "대리",discord.Color.green()
 elif xp>=100:return "사원",discord.Color.blue()
 else:return "인턴",discord.Color.light_gray()
def create_info_embed(target:discord.Member,xp:int,level:int):
 role_name,color=get_role_data(xp);current_level_xp=xp%100;progress=int(current_level_xp/10);bar="█"*progress+"░"*(10-progress)
 embed=discord.Embed(title=f"👤 {target.display_name}님의 정보",color=color);embed.set_thumbnail(url=target.display_avatar.url)
 embed.add_field(name="📈 레벨",value=f"{level} 레벨",inline=True);embed.add_field(name="✨ 경험치",value=f"{xp} XP",inline=True);embed.add_field(name="🎖️ 직급",value=role_name,inline=False);embed.add_field(name="진행 상황",value=f"{bar} ({current_level_xp}/100 XP)",inline=False)
 return embed
class InfoButtonView(discord.ui.View):
 def __init__(self,target_member:discord.Member):super().__init__(timeout=60);self.target_member=target_member
 @discord.ui.button(label="상세 정보 확인",style=discord.ButtonStyle.primary)
 async def get_info(self,interaction:discord.Interaction,button:discord.ui.Button):
  row=database.get_user_xp(self.target_member.id)
  if not row:await interaction.response.send_message("데이터 없음",ephemeral=False);return
  xp,level=row;await interaction.response.send_message(embed=create_info_embed(self.target_member,xp,level),ephemeral=False)
async def check_role_upgrade(member:discord.Member,xp:int):
 role_name,_=get_role_data(xp);target_id=ROLE_IDS[role_name];target_role=member.guild.get_role(target_id);all_role_ids=set(ROLE_IDS.values());roles_to_remove=[r for r in member.roles if r.id in all_role_ids and r.id!=target_id]
 if roles_to_remove:await member.remove_roles(*roles_to_remove)
 if target_role and target_role not in member.roles:await member.add_roles(target_role)
 return role_name
@bot.event
async def on_ready():database.init_db();await bot.tree.sync();print(f"{bot.user} v1.1.0 로그인 완료!")
@bot.tree.command(name="포인트",description="유저 경험치 수정")
async def 포인트(interaction:discord.Interaction,member:discord.Member,action:Literal["추가","제거"],amount:int):
 val=amount if action=="추가" else -amount;new_xp,level=database.update_xp(member.id,val);role_name=await check_role_upgrade(member,new_xp);embed=discord.Embed(title="💰 포인트 업데이트 완료",description=f"{member.mention}",color=discord.Color.green());embed.add_field(name="결과",value=f"{role_name} / {new_xp} XP");await interaction.response.send_message(embed=embed,view=InfoButtonView(member))
@bot.tree.command(name="순위",description="경험치 TOP 10")
async def 순위(interaction:discord.Interaction):
 top_users=database.get_top_users(limit=10)
 if not top_users:await interaction.response.send_message("데이터 없음",ephemeral=False);return
 embed=discord.Embed(title="🏆 MJ-Core 경험치 순위",color=discord.Color.gold())
 for i,(user_id,xp,level) in enumerate(top_users,1):
  member=interaction.guild.get_member(user_id);name=member.display_name if member else f"유저_{user_id}";role_name,_=get_role_data(xp);embed.add_field(name=f"{i}위 {name}",value=f"{role_name} | {xp} XP",inline=False)
 await interaction.response.send_message(embed=embed)
@bot.tree.command(name="정보",description="유저 정보")
async def 정보(interaction:discord.Interaction,member:Optional[discord.Member]=None):
 target=member or interaction.user;row=database.get_user_xp(target.id)
 if not row:await interaction.response.send_message("데이터 없음",ephemeral=False);return
 await interaction.response.send_message(embed=create_info_embed(target,row[0],row[1]),ephemeral=False)
@bot.tree.command(name="종료",description="봇 종료")
@app_commands.checks.has_permissions(administrator=True)
async def 종료(interaction:discord.Interaction):await interaction.response.send_message("종료 중...",ephemeral=False);await shutdown_bot()
async def terminal_input_listener():
 while not shutdown_event.is_set():
  try:
   user_input=await asyncio.to_thread(input,"")
   if user_input.strip().lower()=="stop":await shutdown_bot();break
  except Exception:break
async def main():
 loop=asyncio.get_running_loop();input_task=loop.create_task(terminal_input_listener())
 for sig in (signal.SIGINT,signal.SIGTERM):
  try:loop.add_signal_handler(sig,lambda:asyncio.create_task(shutdown_bot()))
  except NotImplementedError:pass
 try:await bot.start(TOKEN)
 except Exception as e:print(f"[시스템] 실행 중 오류 발생: {e}")
 finally:
  if not bot.is_closed():await bot.close()
if __name__=="__main__":
 try:asyncio.run(main())
 except KeyboardInterrupt:pass
 except Exception as e:print(f"[시스템] 치명적 오류: {e}")