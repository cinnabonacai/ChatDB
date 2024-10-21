const express = require('express');
const app = express();
const productsCollection = require('./Models/Products');
const mongoose = require('mongoose');



app.use(express.json());

mongoose.connect('mongodb://localhost:27017/sampleCultureProduct', {
    useNewUrlParser: true,
    useUnifiedTopology: true
});

app.use('/api/products', productsCollection);

app.get('/', (req, res) => {
    res.send('Hello World');
});

const port = 3000;
app.listen(port, ()=>{
   console.log(`Server is running on port ${port}`);
});


