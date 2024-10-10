const mongoose = require('mongoose');

const productSchema = new mongoose.Schema({

});

productsCollection = mongoose.model('Products', productSchema);
module.exports = productsCollection;