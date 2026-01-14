# Colibri Catering Telegram Bot

Bu Telegram bot **Colibri Catering** uchun ishlaydi. Bot quyidagi vazifalarni bajaradi:  

- Har kuni soat 9:00 da obunachilarga menyuni yuborish  
- Mijoz savollariga **ChatGPT orqali aqlli javob berish**  
- Buyurtmalarni qabul qilish va **guruhga yuborish**  
- 3 soatdan keyin taklif va etirozlarni yig‘ish  
- To‘lov turlarini qayd etish (Click/Karta yoki Naqd)

---

## ⚡ Deploy qilish (Render.com)

1. Render.com-da yangi **Web Service** yaratish  
2. GitHub repository bilan bog‘lash yoki fayllarni upload qilish  
3. Environment Variables qo‘yish:  
   - `BOT_TOKEN` = Telegram bot token  
   - `OPENAI_API_KEY` = OpenAI API key  
   - `ADMIN_ID` = admin Telegram ID (mas: 7968827951)  
   - `GROUP_URL` = buyurtmalar yuboriladigan guruh linki  

4. Build Command:  
