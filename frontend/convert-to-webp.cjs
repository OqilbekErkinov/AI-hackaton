const fs = require('fs');
const sharp = require('sharp');
const path = require('path');

const inputDir = './public/images';    
const outputDir = './public/images-webp'; 


if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir);
}

fs.readdir(inputDir, (err, files) => {
    if (err) {
        console.error('Katalogni o‘qib bo‘lmadi:', err);
        return;
    }

    files.forEach((file) => {
        const inputFile = path.join(inputDir, file);
        const outputFile = path.join(outputDir, file.replace(/\.(png|jpg|jpeg)$/i, '.webp'));

        sharp(inputFile)
            .resize(800, 600, {
                fit: 'inside'
                withoutEnlargement: true,
            })
            .webp({ quality: 80 })
            .toFile(outputFile)
            .then(() => {
                console.log(`Konvertatsiya qilindi: ${file} → ${outputFile}`);
            })
            .catch((err) => {
                console.error(`Xato: ${file} konvertatsiya bo‘lmadi`, err);
            });
    });
});
