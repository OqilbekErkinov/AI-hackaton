// server/api/order.post.ts
export default defineEventHandler(async (event) => {
  const body = await readBody<{name:string; phone:string; source?:string}>(event)
  if (!body?.phone) {
    throw createError({ statusCode: 400, statusMessage: 'phone required' })
  }

  const config = useRuntimeConfig()
  const token = process.env.TELEGRAM_BOT_TOKEN || config.telegramBotToken
  const chatId = process.env.TELEGRAM_CHAT_ID || config.telegramChatId

  const text = [
    '🆕 Yangi buyurtma',
    `👤 Ism: ${body.name || '-'}`,
    `📞 Telefon: ${body.phone}`,
    `🔖 Manba: ${body.source || 'landing'}`
  ].join('\n')

  if (token && chatId) {
    const url = `https://api.telegram.org/bot${token}/sendMessage`
    await $fetch(url, { method:'POST', body:{ chat_id: chatId, text } })
  } else {
    // Dev rejimida konsolga chiqaramiz
    console.log(text)
  }

  return { ok:true }
})
