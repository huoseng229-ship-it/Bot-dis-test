# Overview

This is a Discord music bot built with Python that allows users to play audio from YouTube and other sources in Discord voice channels. The bot uses discord.py for Discord integration and yt-dlp for extracting audio streams from various platforms. It features a queue system for managing multiple tracks and includes a keep-alive mechanism for continuous operation on hosting platforms.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Bot Framework
- **Discord.py**: Core Discord bot framework handling commands, events, and voice channel interactions
- **Command System**: Uses Discord.py's command extension with "!" prefix for user interactions
- **Intents**: Configured with message content intent to read user commands

## Audio Processing
- **yt-dlp**: Primary audio extraction library supporting YouTube and multiple other platforms
- **FFmpeg Integration**: Audio processing and streaming with reconnection capabilities for stable playback
- **Audio Options**: Configured for best audio quality with fallback options and no playlist expansion

## Queue Management
- **Track Class**: Custom data structure storing track metadata including title, URL, webpage URL, requester, and duration
- **Deque-based Queue**: Uses Python's deque for efficient queue operations (add/remove from both ends)
- **Duration Formatting**: Helper method for human-readable time display

## Infrastructure
- **Flask Keep-Alive**: Simple HTTP server running on port 8080 to prevent hosting platform timeouts
- **Threading**: Multi-threaded architecture separating bot operations from keep-alive server
- **Environment Configuration**: Uses python-dotenv for secure token management

## Error Handling & Reliability
- **Connection Resilience**: FFmpeg configured with reconnection parameters for unstable network conditions
- **Search Fallback**: Default search set to YouTube when direct URLs aren't provided
- **Resource Management**: Disabled caching to prevent storage issues on limited hosting environments

# External Dependencies

## Core Libraries
- **discord.py**: Discord API wrapper and bot framework
- **yt-dlp**: YouTube and media downloader/extractor
- **python-dotenv**: Environment variable management
- **Flask**: Lightweight web server for keep-alive functionality

## System Dependencies
- **FFmpeg**: Required for audio processing and streaming (system-level dependency)

## External Services
- **Discord API**: Bot hosting and voice channel integration
- **YouTube/Media Platforms**: Content source via yt-dlp extraction
- **Hosting Platform**: Requires HTTP endpoint for uptime monitoring (keep-alive server)

## Configuration Files
- **Environment Variables**: Discord bot token stored in .env file
- **cookies.txt**: YouTube session cookies for enhanced access (optional authentication)