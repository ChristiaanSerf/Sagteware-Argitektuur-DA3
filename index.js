const express = require('express');

const app = express();

app.get('/', (req, res) => {
    res.json({ message: 'Hello almal' });
});

app.get('/NSARG', (req, res) => {
    res.json({ message: 'Hello NSARG' });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});