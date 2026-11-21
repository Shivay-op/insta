## 🚀 Social Media Downloader Bot

### One Bot • 21 Platforms • Easy Downloads

A powerful Telegram bot for downloading videos and media from your favorite social media platforms.

<br/>

![Platforms](https://img.shields.io/badge/Platforms-21-8A2BE2?style=for-the-badge)
![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?style=for-the-badge&logo=telegram)
![Media](https://img.shields.io/badge/Media-Downloader-success?style=for-the-badge)
![API](https://img.shields.io/badge/API-Third--Party-orange?style=for-the-badge)

</div>

---

## ✨ About

**Social Media Downloader Bot** is a multi-platform Telegram bot that makes downloading social media videos and media simple and convenient.

Just send a supported media link to the bot, and it will process your request using third-party downloading services.

**No complicated steps. Just send a link and download!**

## 🌟 Features

- 🌐 Support for 21 social media platforms.
- 📥 Easy video and media downloading.
- 🎵 Audio extraction where supported.
- ⚡ Fast processing through external services.
- 🤖 Simple Telegram bot interface.
- 🔗 Easy URL-based downloading.
- 🔄 Integration with multiple media tools.

## 🌍 Supported Platforms

| # | Platform | # | Platform |
|:---:|---|:---:|---|
| 01 | Bilibili | 12 | SoundCloud |
| 02 | Bluesky | 13 | Streamable |
| 03 | Dailymotion | 14 | TikTok |
| 04 | Facebook | 15 | Tumblr |
| 05 | Instagram | 16 | Twitch |
| 06 | Loom | 17 | Twitter / X |
| 07 | OK.ru | 18 | Vimeo |
| 08 | Pinterest | 19 | VK |
| 09 | Reddit | 20 | YouTube |
| 10 | Rutube | 21 | Spotify |
| 11 | Snapchat | | |

## 🔌 Third-Party API

This project integrates an externally available API for media downloading.

**API Endpoint:**

```text
https://tele-social.vercel.app/down
```

### Example API Request

```http
GET https://tele-social.vercel.app/down?url=VIDEO_URL
```

### cURL Example

```bash
curl "https://tele-social.vercel.app/down?url=https://www.youtube.com/watch?v=VIDEO_ID"
```

Replace `VIDEO_URL` with the supported media URL.

> **Important:** This API is a third-party service discovered online. It is not owned, developed, or maintained by this project. Its availability and functionality depend on the API provider.

## ⚙️ Technologies & Services

| Technology | Purpose |
|---|---|
| Cobalt | Media downloading |
| APIOR | Third-party API integration |
| yt-dlp | Video and audio extraction |
| Telegram Bot API | Telegram integration |
| Vercel | Hosting of the discovered API |

## 🔄 How It Works

```text
       👤 USER
          |
          v
    🤖 TELEGRAM BOT
          |
          v
   🔌 THIRD-PARTY API
          |
          v
    ⚡ MEDIA PROCESSING
          |
          v
     📥 DOWNLOAD
          |
          v
    ✅ USER RECEIVES MEDIA
```

## 📸 Screenshots

Add screenshots of your Telegram bot here.

```md
![Bot Screenshot](screenshots/demo.png)
```

## ⚠️ Disclaimer

- This is an independent Telegram bot project.
- The third-party API is not owned or maintained by this project.
- Cobalt, APIOR, and yt-dlp are external tools or services.
- All social media platforms belong to their respective owners.
- This project is not affiliated with or endorsed by any supported platform.
- API availability and supported features may change without notice.
- Users are responsible for respecting copyright laws, privacy, and platform terms of service.

## 🤝 Contributing

Contributions are welcome!

1. Fork this repository.
2. Create a new branch.
3. Make your changes.
4. Commit your changes.
5. Submit a Pull Request.

## ⭐ Support

If you like this project:

- ⭐ Star this repository.
- 🐛 Report bugs.
- 💡 Suggest new features.
- 🤝 Contribute to development.

---

## 🙏 Credits & Acknowledgements

This project is made possible thanks to these amazing open-source projects and services.

- **[Cobalt](https://github.com/imputnet/cobalt)** – An open-source media downloader. Special thanks to the Cobalt developers and contributors.
- **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** – An excellent command-line audio/video downloader maintained by its developers and contributors.
- **[APIOR](https://apior.com/)** – Third-party API service used in the project, where applicable.
- **[Telegram Bot API](https://core.telegram.org/bots/api)** – For providing the Telegram bot platform.

A huge thank you to all the developers and contributors who build and maintain these tools.

### 📜 Open-Source Licenses

Please refer to the original repositories for their respective licenses:

- [Cobalt License](https://github.com/imputnet/cobalt/blob/main/LICENSE)
- [yt-dlp License](https://github.com/yt-dlp/yt-dlp/blob/master/LICENSE)

**Note:** Cobalt and yt-dlp are independent projects. We are not their developers or maintainers and are not affiliated with them.

</div>
