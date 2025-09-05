import discord
import opuslib
import os
import re
import asyncio
from typing import Optional, Dict, Deque
from collections import deque

import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load Opus for voice functionality
if not discord.opus.is_loaded():
    try:
        # Use the path we configured earlier for opuslib
        discord.opus.load_opus('/nix/store/0py9xncsn0s6vqxhvqblvhs2cqbb30s8-libopus-1.5.2/lib/libopus.so.0')
        print("✅ Opus loaded successfully!")
    except Exception as e:
        print(f"❌ Failed to load Opus: {e}")
        # Try alternative methods
        try:
            discord.opus.load_opus('libopus.so.0')
        except:
            try:
                discord.opus.load_opus('libopus')
            except:
                print("⚠️ Warning: Could not load Opus. Voice functionality may not work.")

import yt_dlp

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# -------- Intents & Bot --------
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# -------- YTDLP Options --------
YTDLP_OPTS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "default_search": "ytsearch",
    "source_address": "0.0.0.0",
    "extract_flat": False,
    "cachedir": False,
}

FFMPEG_BEFORE_OPTS = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
FFMPEG_OPTS = "-vn"

# -------- Queue --------
class Track:
    def __init__(self, title: str, url: str, webpage_url: str, requester: str, duration: Optional[int]):
        self.title = title
        self.url = url
        self.webpage_url = webpage_url
        self.requester = requester
        self.duration = duration

    def pretty_duration(self) -> str:
        if not self.duration:
            return "??:??"
        m, s = divmod(self.duration, 60)
        h, m = divmod(m, 60)
        return f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:d}:{s:02d}"

class GuildState:
    def __init__(self):
        self.queue: Deque[Track] = deque()
        self.now_playing: Optional[Track] = None
        self.next_event = asyncio.Event()
        self.loop = False

guild_states: Dict[int, GuildState] = {}

def get_state(guild: discord.Guild) -> GuildState:
    if guild.id not in guild_states:
        guild_states[guild.id] = GuildState()
    return guild_states[guild.id]

# -------- Helpers --------
YOUTUBE_URL_RE = re.compile(r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+', re.I)

async def ytdlp_search(query: str) -> Track:
    with yt_dlp.YoutubeDL(YTDLP_OPTS) as ydl:
        info = ydl.extract_info(query, download=False)
        if not info:
            raise ValueError(f"Could not extract info from: {query}")
        if "_type" in info and info["_type"] == "playlist" and info.get("entries"):
            info = info["entries"][0]
        title = info.get("title", "Unknown")
        duration = info.get("duration")
        webpage_url = info.get("webpage_url") or info.get("url") or ""
        formats = info.get("formats", [])
        audio_formats = [f for f in formats if f.get("acodec") != "none" and f.get("vcodec") == "none"]
        best = max(audio_formats, key=lambda f: f.get("abr", 0) or f.get("tbr", 0), default=None)
        stream_url = best["url"] if best else info.get("url", "")
        return Track(title=title, url=stream_url, webpage_url=webpage_url, requester="?", duration=duration)

def make_source(url: str) -> discord.PCMVolumeTransformer:
    source = discord.FFmpegPCMAudio(url, before_options=FFMPEG_BEFORE_OPTS, options=FFMPEG_OPTS)
    return discord.PCMVolumeTransformer(source, volume=0.5)

async def player_loop(guild: discord.Guild):
    state = get_state(guild)
    while True:
        state.next_event.clear()

        if state.loop and state.now_playing:
            track = state.now_playing
        else:
            if not state.queue:
                state.now_playing = None
                return
            track = state.queue.popleft()
            state.now_playing = track

        voice = guild.voice_client
        if not voice:
            return

        audio = make_source(track.url)

        def after_play(err):
            if err:
                print("FFmpeg error:", err)
            bot.loop.call_soon_threadsafe(state.next_event.set)

        voice.play(audio, after=after_play)

        await state.next_event.wait()

@bot.event
async def on_ready():
    print(f"Đã đăng nhập: {bot.user} (id: {bot.user.id})")

# -------- Commands --------

# Hát
@bot.command(name="hát")
async def hat_cmd(ctx: commands.Context, *, query: str):
    if ctx.author.voice is None or ctx.author.voice.channel is None:
        return await ctx.send("Mày vào kênh thoại đi rồi kêu tao hát.")

    if ctx.guild.voice_client is None:
        await ctx.author.voice.channel.connect()
    else:
        if ctx.guild.voice_client.channel != ctx.author.voice.channel:
            await ctx.guild.voice_client.move_to(ctx.author.voice.channel)

    state = get_state(ctx.guild)
    track = await ytdlp_search(query)
    track.requester = str(ctx.author)

    await ctx.send(f"🎵 Đã bỏ: **{track.title}** (`{track.pretty_duration()}`)")

    voice = ctx.guild.voice_client
    if not voice.is_playing() and not voice.is_paused() and state.now_playing is None:
        state.queue.appendleft(track)
        await player_loop(ctx.guild)
    else:
        state.queue.append(track)

# Dừng
@bot.command(name="dừng")
async def dung_cmd(ctx: commands.Context):
    vc = ctx.guild.voice_client
    if vc and vc.is_playing():
        vc.pause()
        await ctx.send("⏸️")
    else:
        await ctx.send("Không có hát")

# Qua bài
@bot.command(name="qua bài")
async def qua_bai_cmd(ctx: commands.Context):
    vc = ctx.guild.voice_client
    if vc and (vc.is_playing() or vc.is_paused()):
        vc.stop()
        await ctx.send("⏭️")
    else:
        await ctx.send("Có mở bài nào đâu mà bỏ qua.")

# Lặp lại
@bot.command(name="lặp lại")
async def lap_lai_cmd(ctx: commands.Context):
    state = get_state(ctx.guild)
    state.loop = not state.loop
    await ctx.send(f"🔁 Lặp lại: **{'BẬT' if state.loop else 'TẮT'}**")

# Im (thoát voice)
@bot.command(name="im")
async def im_cmd(ctx: commands.Context):
    vc = ctx.guild.voice_client
    state = get_state(ctx.guild)
    state.queue.clear()
    state.loop = False
    if vc:
        await vc.disconnect()
        await ctx.send("🤐 Bot đã im và thoát.")
    else:
        await ctx.send("Tao có hát đâu mà im được")

# Hàng chờ
@bot.command(name="hàng chờ")
async def hang_cho_cmd(ctx: commands.Context):
    state = get_state(ctx.guild)
    if not state.queue:
        return await ctx.send("Hàng chờ trống.")
    lines = []
    for i, t in enumerate(list(state.queue)[:10], start=1):
        lines.append(f"{i}. **{t.title}** (`{t.pretty_duration()}`) • {t.requester}")
    more = f"\n… và {len(state.queue)-10} bài nữa." if len(state.queue) > 10 else ""
    await ctx.send("**Hàng chờ:**\n" + "\n".join(lines) + more)

# Đang hát
@bot.command(name="đang hát")
async def dang_hat_cmd(ctx: commands.Context):
    state = get_state(ctx.guild)
    if not state.now_playing:
        return await ctx.send("Chưa phát bài nào.")
    t = state.now_playing
    await ctx.send(f"🎶 **Đang phát:** {t.title} (`{t.pretty_duration()}`)\n<{t.webpage_url}>")

# -------- Run --------
if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("Thiếu DISCORD_TOKEN trong .env/Secrets")
    bot.run(TOKEN)

