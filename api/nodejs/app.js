const express = require('express');
const axios = require('axios');
const app = express();
const port = 3000;

app.get('/', (req, res) => {
  res.json({ message: 'Welcome to the API platform!' });
});

app.get('/bing-wallpaper', async (req, res) => {
  const itx = req.query.itx || 0;
  try {
    const response = await axios.get(`https://cn.bing.com/HPImageArchive.aspx?format=js&idx=${itx}&n=1&mkt=zh-CN`);
    const data = response.data;
    const bgUri = data.images[0].urlbase + '_1920x1080.jpg';
    const bgUrl = 'https://cn.bing.com' + bgUri;
    const bgName = bgUrl.match(/\/th\?id=OHR\.(.*?\.jpg)/)[1];
    const bgText = data.images[0].copyright;
    res.json({ url: bgUrl, name: bgName, text: bgText });
  } catch (error) {
    res.status(500).json({ error: 'An error occurred while fetching the data.' });
  }
});

app.get('/google-translate', async (req, res) => {
  const q = req.query.q;
  const sl = req.query.sl || 'auto';
  const tl = req.query.tl || 'zh';
  const url = `http://translate.google.com/translate_a/single?client=gtx&dt=t&dj=1&ie=UTF-8&sl=${sl}&tl=${tl}&q=${q}`;
  
  try {
    const response = await axios.get(url);
    const data = response.data;
    let result_text = '';
    for (const sentence of data.sentences) {
      result_text += sentence.trans + ' ';
    }
    res.json({ result: result_text });
  } catch (error) {
    res.status(500).json({ error: 'An error occurred while fetching the data.' });
  }
});

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
