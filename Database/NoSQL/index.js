const express = require('express');
const app = express();
const productsRoute = require('./Routes/Products');



app.use(express.json());

app.use('/api/products', productsRoute);

app.get('/', (req, res) => {
    res.send('Hello World');
});

const port = 7500;
app.listen(port, ()=>{
   console.log(`Server is running on port ${port}`);
});


