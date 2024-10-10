const express = require('express');
const app = express();

const mongoose = require('mongoose');

const port = 3000;

app.use(express.json());

mongoose.connect('mongodb://localhost:27017/sampleCultureProduct', {
    useNewUrlParser: true,
    useUnifiedTopology: true
});




app.get('/', (req, res) => {
    res.send('Hello World');
});

app.listen(port, ()=>{
   console.log(`Server is running on port ${port}`);
});


