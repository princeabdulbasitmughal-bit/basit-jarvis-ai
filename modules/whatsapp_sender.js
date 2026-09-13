/**
 * ====================================================
 * 👑 BASIT JARVIS AI — WHATSAPP SENDER (whatsapp-web.js)
 * ====================================================
 * Usage: node modules/whatsapp_sender.js <phone> <message>
 * Phone format: 923001234567 (international, no +)
 *
 * First run: QR code dikhega — scan karo WhatsApp se.
 * Baad mein: session save ho jaata hai, auto-connect.
 */

const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const path = require('path');
const fs = require('fs');

const SESSION_DIR = path.join(__dirname, '..', 'data', 'whatsapp_session');
fs.mkdirSync(SESSION_DIR, { recursive: true });

const phone = process.argv[2];
const message = process.argv[3] || '';

if (!phone) {
    console.error('Usage: node whatsapp_sender.js <phone> <message>');
    process.exit(1);
}

const client = new Client({
    authStrategy: new LocalAuth({ dataPath: SESSION_DIR }),
    puppeteer: {
        headless: true,
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-accelerated-2d-canvas',
            '--no-first-run',
            '--no-zygote',
            '--single-process',
            '--disable-gpu'
        ]
    }
});

let qrShown = false;
let sent = false;

client.on('qr', (qr) => {
    if (!qrShown) {
        qrShown = true;
        console.log('\n📱 WhatsApp QR Code — Apne phone se scan karo:\n');
        qrcode.generate(qr, { small: true });
        console.log('\nScan karne ke baad yeh window automatically proceed karegi...\n');
    }
});

client.on('ready', async () => {
    console.log('WhatsApp connected!');
    try {
        const chatId = `${phone}@c.us`;
        await client.sendMessage(chatId, message);
        console.log(`sent: Message to ${phone} delivered!`);
        sent = true;
    } catch (err) {
        console.error(`error: Could not send message — ${err.message}`);
    }
    client.destroy();
    process.exit(sent ? 0 : 1);
});

client.on('auth_failure', (msg) => {
    console.error('auth_failure: ' + msg);
    process.exit(1);
});

client.on('disconnected', (reason) => {
    console.log('Disconnected: ' + reason);
    process.exit(1);
});

// Timeout after 90 seconds
setTimeout(() => {
    if (!sent) {
        console.error('timeout: WhatsApp did not connect in 90 seconds.');
        client.destroy();
        process.exit(1);
    }
}, 90000);

client.initialize();
