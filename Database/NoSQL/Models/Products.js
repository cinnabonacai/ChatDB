const mongoose = require('mongoose');

const variantSchema = new mongoose.Schema({
    variantId: {
       type: String,
       required: true
    },
    sku: {type: String},
    price: {type: Number},
    compareAtPrice: {type: Number},
    inventoryQuantity: {type: Number},
    requiresShipping: {
        type: Boolean,
        default: true
    },
    weight: {type: Number},
    weightUnit: {
        type: String,
        enum: ['kg', 'g', 'lb', 'oz'],
        default: 'kg'
    },
    selectedOptions: [{
        name: {type: String},
        value: {type: String}
    }],
    images: [{
        imageId: {type: String},
        src: {type: String},
        altText: {type: String}
    }],
    createdAt: {
        type: Date,
        default: Date.now
    },
    updatedAt: {
        type: Date,
        default: Date.now
    }
});

const imageSchema = new mongoose.Schema({
    imageId: {
       type: String,
       required: true,
    },
    src: {
      type: String,
      required: true
    },
    altText: {type: String}
});


const productSchema = new mongoose.Schema({
    shopifyId: {
        type: String,
        required: true,
        unique: true
    },
    title: {
        type: String,
        required: true
    },
    descriptionHTML: {
       type: String,
       required: true
    },
    handle: {
       type: String, 
       required: true
    },
    vendor: {
       type: String,
       required: true
    },
    productType: {
        type: String,
        enum: ['Clothing and Accessories', 'Electronics and Gadgets', 'Home and Garden', 'Beauty and Personal Care',
               'Health and Wellness', 'Food and Beverages', 'Toys and Hobbies', 'Automative', 'Sports and Outdoor Gear',
               'Office Supplies and Stationery', 'Jewelry and Accessories', 'Books and Media', 'Pet Supplies', 
               'Travel and Luggage', 'Baby and Kids Products', 'Tools and Hardware'],
        required: true,

    },
    tags: [String],
    options: [{
        id: String,
        name: String,
        values: [String]
    }],
    variants: [variantSchema],
    images: [imageSchema],
    createdAt: {
        type: Date,
        default: Date.now
    },
    updatedAt: {
        type: Date,
        default: Date.now,
    },
    publishedAt: {
        type: Date,
        default: Date.now
    }
});
productsCollection = mongoose.model('products', productSchema);
module.exports = productsCollection;