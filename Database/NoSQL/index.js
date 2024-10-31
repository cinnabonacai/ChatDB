const express = require('express');
const app = express();
const productsRoute = require('./Routes/Products');
const mongoose = require('mongoose');



app.use(express.json());

mongoose.connect('mongodb://localhost:27017/sampleCultureProduct', {
    useNewUrlParser: true,
    useUnifiedTopology: true
}).then(() => console.log('Connected to MongoDB'))
  .catch(err => console.error('Failed to connect to MongoDB', err));

app.use('/api/products', productsRoute);

app.get('/', (req, res) => {
    res.send('Hello World');
});

const port = 7500;
app.listen(port, ()=>{
   console.log(`Server is running on port ${port}`);
});


