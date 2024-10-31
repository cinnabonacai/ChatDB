const express = require('express');
const router = express.Router();

const productsCollection = require('../Models/Products');


/* GET Endpoints */

/* General Cases */
// logic:(1) obtain the parameters from each endpoint via the request method
//       (2) use the parameters at step 1 to query the database for specific product or products
//       (3) 1. If the product or products cannot be found, return a 404 status code with a message
//           2. If the product or products can be found, return a 200 status code with the product or products
//       (4) return a 500 status code with an error message if an error occurs 

// get a specific product based on the shopifyID
router.get('/:shopifyID', async (req, res) => {
     try {
        const shopifyIDSelected = req.params.shopifyID;
        const product = await productsCollection.findOne({shopifyId: shopifyIDSelected});
        if (!product) {
            return res.status(404).json({'message': 'The shopifyID selected is not found. Please try again.'});
        }
        return res.status(200).json(product);

     }catch(err) {
        return res.status(500).json({
            'message': 'Internal Server Error',
            'error': err.message,
   });
     }
});

// get a specific product based on title and vendor
router.get('/title/:title/vendor/:vendor', async (req, res) => {
    try {
        const titleSelected = req.params.title;
        const vendorSelected = req.params.vendor;
        const product = await productsCollection.findOne({title: titleSelected, vendor: vendorSelected});
        if (!product) {
            return res.status(404).json({'message': 'The title and/or vendor selected are not found. Please try again later!'});
        }
        return res.status(200).json(product);

    }catch (err) {
        res.status(500).json({
            "message": "Internal Server Error",
            "error": err.message
        });
    }
});

// retrieve all qualified products based on the title
router.get('/title/:title', async (req, res) => {
    try {
        const titleSelected = req.params.title;
        const productsList = await productsCollection.find({title: titleSelected});
        if (productsList.length === 0) {
            return res.status(404).json({'message': 'The name of the product you typed is not found. Please try again later!'});
        }
        return res.status(200).json(productsList);

    }catch(err) {
        res.status(500).json({
            'message': 'Internal Server Error',
            'error': err.message
        })
    }
});

// retrieve all qualified products based on the vendor
router.get('/vendor/:vendor', async (req, res) => {
    try {
        const vendor = req.params.vendor;
        const productsList = await productsCollection.find({vendor: vendor});
        if (productsList.length === 0) {
            return res.status(404).json({'message': 'The vendor you selected is not found. Please try again later!'});
        }
        return res.status(200).json(productsList);

    }catch(err) {
        return res.status(500).json({
            'message': 'Internal Server Error',
            'error': err.message
        });
    }
});

// retrieve all products based on the product type
router.get('/productType/:productType', async (req, res) => {
    try {
        const productType = req.params.productType;
        const productsList = await productsCollection.find({productType: productType});
        if (productsList.length === 0) {
            return res.status(404).json({'message': 'There exists no products associated with this producy type. Please try again later!'});
        }
        return res.status(200).json(productsList);

    }catch(err) {
        return res.status(500).json({
            'message': 'Internal Server Error',
            'error': err.message
        });
    }

});

// retrieve all options of the product based on the title and the vendor
router.get('/title/:title/vendor/:vendor/options', async (req, res) => {
    try {
        const {title, vendor} = req.params;
        const product = await productsCollection.findOne({title: title, vendor: vendor});
        if (!product) {
            return res.status(404).json({'message': 'The title and the vendor associated with this product cannot be found. Please try again later!'});
        }
        const optionsList = product.options;
        if (!optionsList || optionsList.length === 0) {
            return res.status(404).json({'message': 'The product is currently invented, and the options are still pending.'});
        }
        return res.status(200).json(optionsList);

    }catch (err) {
       return res.status(500).json({
            'message': 'Internal Server Error',
            'error': err.message
       })
    }
});

// retrieve a specific option of the product based on the title, vendor, and optionID, such as size, color, and materials
router.get('/title/:title/vendor/:vendor/options/:optionID', async (req, res) => {
    try {
        const {title, vendor} = req.params;
        const product = await productsCollection.findOne({title: title, vendor: vendor});
        if (!product) {
            return res.status(404).json({'message': 'The title and the vendor associated with this product cannot be found. Please try again later!'});
        }
        const optionIDSelected = req.params.optionID;
        const optionSelected = product.options.find(option => option.id === optionIDSelected);
        // const optionSelected = product.options.findOne({id: optionIDSelected});
        if (!optionSelected) {
            return res.status(404).json({'message': 'The option selected is not found. Please try again later!'});
        }
        return res.status(200).json(optionSelected);

    }catch(err) {
        return res.status(500).json({
            'message':  'Internal Server Error',
            'error': err.message
        })
    }
});

// retrieve all tags of the product based on the title and the vendor
router.get('/title/:title/vendor/:vendor/tags', async (req, res) => {
    try {
        const {title, vendor} = req.params;
        const product = await productsCollection.findOne({title: title, vendor: vendor});
        if (!product) {
            return res.status(404).json({'message': 'The title and/or the vendor associated this product cannot be found. Please try again later! '});
        }
        const tagsList = product.tags;
        if (!tagsList || tagsList.length === 0) {
            return res.status(404).json({'message': 'The product is currently invented, and the tags are still pending.'});
        }
        return res.status(200).json(tagsList);
    }catch(err) {
        return res.status(500).json({
            'message': 'Internal Server Error',
            'error': err.message
        });
    }
});


/* Variant Cases  */

// retrieve all variants of the product based on the title and the vendor
router.get('/title/:title/vendor/:vendor/variants', async (req, res) => {
    try {
        const {title, vendor} = req.params;
        const product = await productsCollection.findOne({title: title, vendor: vendor});
        if (!product) {
            return res.status(404).json({'message': 'The title and/or the vendor associated with this product cannot be found. Please try again later!'});
        }
        const variantsList = product.variants;
        if (!variantsList || variantsList.length === 0) {
            return res.status(404).json({'message': 'The variants of this product are still working. Please try again later!'});
        }
        return res.status(200).json(variantsList);
    }catch(err) {
        return res.status(500).json({
            'message': 'Internal Server Error',
            'error': err.message
        });
    }
});

// retrieve all variants of the product based on the title, the vendor, and the variantID
router.get('/title/:title/vendor/:vendor/variants/:variantID', async (req, res) => {
    try {
        const {title, vendor, variantID} = req.params;
        const product = await productsCollection.findOne({title: title, vendor: vendor});
        if (!product) {
            return res.status(404).json({'message': 'The title and/or the vendor associated with this product cannot be found. Please try again later!'});
        }
        const variantSelected = await product.variants.find(variant => variant.variantId === variantID);
        if (!variantSelected) {
            return res.status(404).json({'message': 'The variant associated with this product has not been published yet. Please be patient!'});
        }
        return res.status(200).json(variantSelected);
    }catch(err) {
        return res.status(500).json({
            'message': 'Internal Server Error',
            'error': err.message
        });
    }
});

// retrieve all options of the variant based on the title, the vendor, and the variantID
router.get('/title/:title/vendor/:vendor/variants/:variantID/options', async (req, res) => {
    try {
        const {title, vendor, variantID} = req.params;
        const product = await productsCollection.findOne({title: title, vendor: vendor});
        if (!product) {
            return res.status(404).json({'message': 'The title and/or the vendor associated with this product cannot be found. Please try again later!'});
        }
      
        const variantsSelected = product.variants.find(variant => variant.variantId === variantID);
        if (!variantsSelected) {
            return res.status(404).json({'message': 'The variants associated with this product have not been published yet.Please try again later!'});
        }
        const variantOptionsList = variantsSelected.selectedOptions;
        if(!variantOptionsList || variantOptionsList.length === 0) {
            return res.status(404).json({'message': 'The options of this variant are still pending. Please try again later!'});
        }
        return res.status(200).json(variantOptionsList);
    }catch(err) {
        return res.status(500).json({
            'message': 'Internal Server Error',
            'error': err.message
        });
    }
});

// retrieve a specific option of the variant based on the title, vendor, variantID, and optionID
router.get('/title/:title/vendor/:vendor/variants/:variantID/options/:name', async (req, res) => {
    try {
        const {title, vendor, variantID, name} = req.params;
        const product = await productsCollection.findOne({title: title, vendor: vendor});
        if (!product) {
            return res.status(404).json({'message': 'The title and/or the vendor associated with this product cannot be found. Please try again later!'});
        }
        
        const variantSelected = product.variants.find(variant => variant.variantId === variantID);
        if (!variantSelected) {
            return res.status(404).json({'message': 'The variant associated with this product has not been published yet. Please be patient!'});
        }

        const optionSelected = variantSelected.selectedOptions.find(option => option.name === name);
        if(!optionSelected) {
            return res.status(404).json({'message': 'The option selected is not found. Please try again later!'});
        }
        return res.status(200).json(optionSelected);
    }catch(err) {
        return res.status(500).json({
            'message': 'Internal Server Error',
            'error': err.message
        });
    }
});


// retrieve all images of the variant based on the title, vendor, and variantID
router.get('/title/:title/vendor/:vendor/variants/:variantID/images', async (req, res) => {
    try {
        const {title, vendor, variantID} = req.params;
        const product = await productsCollection.findOne({title: title, vendor: vendor});
        if (!product) {
            return res.status(404).json({'message': 'The title and the vendor associated with this product cannot be found. Please try again later!'});
        }

   
        const variantSelected = product.variants.find(variant => variant.variantId === variantID);
        if (!variantSelected) {
            return res.status(404).json({'message': 'The variant associated with this product has not been published yet. Please be patient!'});
        }

        const imagesList = variantSelected.images;
        if (!imagesList || imagesList.length === 0) {
            return res.status(404).json({'message': 'All images associated with this variant are still uploading'});
        }
        return res.status(200).json(imagesList);
    }catch(err) {
        return res.status(500).json({
           'message': 'Internal Server Error',
           'error': err.message
        });
    }
});

// retrieve the specific image of the variant based on title, vendor, variantID, and imageID
router.get('/title/:title/vendor/:vendor/variants/:variantID/images/:imageID', async (req, res) => {
    try {
        const {title, vendor, variantID, imageID} = req.params;
        const product = await productsCollection.findOne({title: title, vendor: vendor});
        if (!product) {
            return res.status(404).json({'message': 'The title and the vendor associated with this product cannot be found. Please try again later!'});
        }

  
        const variantSelected = product.variants.find(variant => variant.variantId === variantID);
        if (!variantSelected) {
            return res.status(404).json({'message': 'The variant associated with this product has not been published yet. Please be patient!'})
        }
        const variantImageSelected = variantSelected.images.find(image => image.imageId === imageID);
        if (!variantImageSelected) {
            return res.status(404).json({'message': 'The image of the variant is still determined,'});
        }
        return res.status(200).json(variantImageSelected);

    }catch(err) {
        return res.status(500).json({
            'message': 'Internal Server Error',
            'error': err.message
        });
    }
});

/* Image Case */

// retrieve all images of the product based on the title and the vendor
router.get('/title/:title/vendor/:vendor/images', async (req, res) => {
    try {
        const {title, vendor} = req.params;
        const product = await productsCollection.findOne({title: title, vendor: vendor});
        if (!product) {
           return res.status(404).json({'message': 'The title and the vendor associated with this product cannot be found. Please try again later!'});
        }
        const imagesList = product.images;
        if (!imagesList || imagesList.length == 0) {
           return res.status(404).json({'message': 'The images of this product are still pending. Please try again later!'});
        }
        return res.status(200).json(imagesList);
    }catch(err) {
        return res.status(500).json({
            'message': 'Internal Server Error',
            'error': err.message
        })
    }
});

// retrieve the specific image of the product based on the title, the vendor, and the imageID
router.get('/title/:title/vendor/:vendor/images/:imageID', async (req, res) => {
    try {
        const {title, vendor, imageID} = req.params;
        const product = await productsCollection.findOne({title: title, vendor: vendor});
        if (!product) {
            return res.status(404).json({'message': 'The title and the vendor associated with this product cannot be found. Please try again later!'});
        }

        const imageSelected = product.images.find(image => image.imageId === imageID);
        if(!imageSelected) {
            return res.status(404).json({'message': 'The image selected is not found. Please try again later!'});
        }
        return res.status(200).json(imageSelected);

    }catch(err) {
        return res.status(500).json({
            'message': 'Internal Server Error',
            'error': err.message
        })
    }
});


/* POST Endpoints */
router.post('/', async (req, res) => {
    try {
        const bodyInserted = req.body
        const productDetermined = new productsCollection(bodyInserted);
        await productDetermined.save();
        return res.status(201).json(productDetermined);
    }catch(err) {
        return res.status(500).json({
            'message': 'Internal Server Error',
            'error': err.message
        });
    }
    
});

/* PUT Endpoints */

/* General Case */
// update a specific product based on the shopifyID selected
router.put('/:shopifyID', async (req, res) => {
   try {
      const shopifyIDSelected = req.params.shopifyID;
      const bodyUpdated = req.body;

      if (Object.keys(bodyUpdated).length === 0) {
        return res.status(400).json({'message': 'No data provided to be updated!'});
      }
    
      const productUpdated = await productsCollection.findOneAndUpdate(
        {shopifyId: shopifyIDSelected},
        {$set: bodyUpdated},
        {new: true, runValidators: true}
      );
      if (!productUpdated) {
         return res.status(404).json({'message': 'The shopifyID selected is not found! Please try again later!'});
      }
      return res.status(200).json(productUpdated);

   }catch(err) {
       return res.status(500).json({
            'message': 'Internal Server Error',
            'error': err.message
       });
   }
});


// update a specific product based on the title and the vendor selected
router.put('/title/:title/vendor/:vendor', async (req, res) => {
    try {
        const {title, vendor} = req.params;
        const bodyUpdated = req.body;
        if (Object.keys(bodyUpdated).length === 0) {
            return res.status(400).json({'message': 'No data provided to be updated!'});
        }
        const productUpdated = await productsCollection.findOneAndUpdate(
            {title: title, vendor: vendor},
            {$set: bodyUpdated},
            {new: true, runValidators: true}
        );
        if (!productUpdated) {
            return res.status(404).json({'message': 'The title and/or the vendor selected are not found. Please try again later!'});
        }
        return res.status(200).json(productUpdated);
    }catch(err) {
        return res.status(500).json({
           'message': 'Internal Server Error',
           'error': err.message
        })
    }
});

// append a new tag into a specific product based on the title and the vendor selected
router.put('/title/:title/vendor/:vendor/tags', async (req, res) => {
    try {
        const {title, vendor} = req.params;
        const bodyUpdated = req.body;
        if (Object.keys(bodyUpdated).length === 0) {
            return res.status(400).json({'message': 'No data provided to be updated!'});
        }
        const productUpdated = await productsCollection.findOneAndUpdate(
            {title: title, vendor: vendor},
            {$push: {tags: bodyUpdated}}, 
            {new: true, runValidators: true}
        );
        if (!productUpdated) {
            return res.status(404).json({'message': 'The title and/or the vendor selected are not found. Please try again later!'});
        }
        return res.statu(200).json(productUpdated);
    }catch(err) {
        return res.status(500).json({
            "message": "Internal Server Error",
            "error": err.message
        });
    }
});

// append a new option into a specific product based on the title and the vendor selected
router.put('/title/:title/vendor/:vendor/options', async (req, res) => {
    try {
        const {title, vendor} = req.params;
        const bodyUpdated = req.body;
        if (Object.keys(bodyUpdated).length === 0) {
            return res.status(400).json({'message': 'No data provided to be updated!'});
        }
        const productUpdated = await productsCollection.findOneAndUpdate(
            {title: title, vendor: vendor}, 
            {$push: {options: bodyUpdated}}, 
            {$new: true, runValidators: true}
        );
        if (!productUpdated) {
            return res.status(404).json({'message': 'The title and/or the vendor selected are not found. Please try again later!'});
        }
        return res.status(200).json(productUpdated);
    }catch(err) {
        return res.status(500).json({
            'message': 'Internal Server Error',
            'error': err.message
        });
    }
});

// update the option of a specific product based on the title, vendor, and optionID selected
router.put('/title/:title/vendor/:vendor/options/:optionID', async (req, res) => {
    try {
        const {title, vendor, optionID} = req.params;
        const bodyUpdated = req.body;
        if (Object.keys(bodyUpdated).length === 0) {
            return res.status(400).json({'message': 'No data provided to be updated!'});
        }
        const productUpdated = await productsCollection.findOneAndUpdate(
            {title: title, vendor: vendor, 'options.id': optionID}, 
            {$set: {'options.$': bodyUpdated}}, 
            {$new: true, runValidators: true}
        );
        if (!productUpdated) {
            return res.status(404).json({'message': 'The title, vendor, and/or optionID selected are not found. Please try again later!'});
        }
        return res.status(200).json(productUpdated);
    }catch(err) {
        return res.status(500).json({
            'message': 'Internal Server Error',
            'error': err.message
        });
    }
});

//append the value to one of the options of a specific product based on title, vendor, and optionID selected
router.put('/title/:title/vendor/:vendor/options/:optionID/values', async (req, res) => {
    try {
        const {title, vendor, optionID} = req.params;
        const bodyUpdated = req.body;
        if (Object.keys(bodyUpdated).length === 0) {
            return res.status(400).json({'message': 'No data updated to be provided!'})
        }
        const productUpdated = await productsCollection.findOneAndUpdate(
            {title: title, vendor: vendor, 'options.id': optionID}, 
            {$push: {'options.$.values': bodyUpdated}}, 
            {$new: true, runValidator: true}
        );
        if (!productUpdated) {
            return res.status(404).json({'message': 'The title, vendor, and/or optionID selected are not found. Please try again later!'});
        }

    }catch(err) {
        return res.status(500).json({
            'message': 'Internal Server Error',
            'error': err.message
        });
    }
});

/* Variant Case*/

// append the variant to a specific product based on the title and vendor selected
router.put('/title/:title/vendor/:vendor/variants', async (req, res) => {
    try {
        const {title, vendor} = req.params;
        const bodyUpdated = req.body;
        if (Object.keys(bodyUpdated).length === 0) {
            return res.status(400).json({'message': 'No data updated to be provided!'});
        }
        const productUpdated = await productsCollection.findOneAndUpdate(
            {title: title, vendor: vendor}, 
            {$push: {variants: bodyUpdated}}, 
            {$new: true, runValidators: true}
        );
        if (!productUpdated) {
            return res.status(404).json({'message': 'The title and/or vendor selected are not found. Please try again later!'});
        }
        return res.status(200).json(productUpdated);
    }catch(err) {
        return res.status(500).json({
            'message': 'Internal Server Error',
            'error': err.message
        });
    }
})

// update the variant of a specific product based on the title, vendor, and variantID selected
router.put('/title/:title/vendor/:vendor/variants/:variantID', async (req, res) => {
    try{
        const {title, vendor, variantID} = req.params;
        const bodyUpdated = req.body;
        if (Object.keys(bodyUpdated).length === 0) {
            return res.status(400).json({'message': 'No data updated to be provided!'});
        }
        const productUpdated = await productsCollection.findOneAndUpdate(
            {title: title, vendor: vendor, 'variants.variantId': variantID}, 
            {$set: {'variants.$': bodyUpdated}}, 
            {$new: true, runValidators: true}
        );
        if (!productUpdated) {
            return res.status(404).json({'message': 'The title, vendor, and/or variantID selected are not found. Please try again later!'});
        }
        return res.status(200).json(productUpdated);
    }catch(err) {
        return res.status(500).json({
            'message': 'Internal Server Error',
            'error': err.message
        });
    }
});

// The option of a specific variant is inserted based on title, vendor, and variantID selected 
router.put('/title/:title/vendor/:vendor/variants/:variantID/options', async (req, res) => {
    try {
        const {title, vendor, variantID} = req.params;
        const bodyUpdated = req.body;
        if (Object.keys(bodyUpdated).length === 0) {
            return res.status(400).json({'message': 'No data updated to be provided!'});
        }
        const productUpdated = await productsCollection.findOneAndUpdate(
            {title: title, vendor: vendor, 'variants.variantId': variantID}, 
            {$push: {'variants.$.selectedOptions': bodyUpdated}},
            {$new: true, runValidators: true}
        );
        if (!productUpdated) {
            return res.status(404).json({'message': 'The title, vendor, and/or variantID selected are not found. Please try again later!'});
        }
        return res.status(200).json(productUpdated);
    }catch(err) {
        return res.status(500).json({
           'message': 'Internal Server Error',
           'error': err.message
        });
    }
});

// update the option of a specific variant based on the title, vendor, variantID, and the name of the variant option selected
router.put('/title/:title/vendor/:vendor/variants/:variantID/options/:name', async (req, res) => {
    try {
        const {title, vendor, variantID, name} = req.params;
        const bodyUpdated = req.body;
        if (Object.keys(bodyUpdated).length === 0) {
            return res.status(400).json({'message': 'No data updated to be provided!'});
        }
        const productUpdated = await productsCollection.findOneAndUpdate(
            {title: title, vendor: vendor, 'variants.variantId': variantID, 'variants.selectedOptions.name': name}, 
            {$set: {'variants.$.selectedOptions.$': bodyUpdated}}, 
            {$new: true, runvalidators: true}
        );
        if (!productUpdated) {
            return res.status(404).json({'message': 'The title, vendor, variantId, and/or name selected are not found. Please try again later!'});
        }
        return res.status(200).json(productUpdated);
    }catch(err) {
        return res.status(500).json({
            'message': 'Internal Server Error',
            'error': err.message
        });
    }
});

// append the image of the variant to the variant object based on title, vendor, and variantID selected
router.put('title/:title/vendor/:vendor/variants/:variantID/images', async (req, res) => {
    try {
        const {title, vendor, variantID} = req.params;
        const bodyUpdated = req.body;
        if (Object.keys(bodyUpdated).length === 0) {
            return res.status(400).json({'message': 'No data provided to be updated!'});
        }
        const productUpdated = await productsCollection.findOneAndUpdate(
            {title: title, vendor: vendor, 'variants.variantId': variantID}, 
            {$push: {'variants.$.images': bodyUpdated}}, 
            {$new: true, runValidators: true}
        );
        if (!productUpdated) {
            return res.status(404).json({'message': 'The title, vendor, and/or variantID selected are not found. Please try again later!'});
        }
        return res.status(200).json(productUpdated);
    }catch(err) {
        return res.status(500).json({
            'message': 'Internal Server Error',
            'error': err.message
        });
    }
});

// update the image of the variant to the variant object based on title, vendor, variantID, and imageID selected
router.put('/title/:title/vendor/:vendor/variants/:variantID/images/:imageID', async (req, res) => {
    try {
        const {title, vendor, variantID, imageID} = req.params;
        const bodyUpdated = req.body;
        if (Object.keys(bodyUpdated).length === 0) {
            return res.status(400).json({'message': 'No data provided to be updated!'});
        }
        const productUpdated = await productsCollection.findOneAndUpdate(
            {title: title, vendor: vendor, 'variants.variantId': variantID, 'variants.images.imageId': imageID},
            {$set: {'varuants.$.images.$': bodyUpdated}},
            {$new: true, runValidators: true}
        );
        if (!productUpdated) {
            return res.status(404).json({'message': 'The title, vendor, variantID, and/or imageID selected are not found. Please try again later!'});
        }
        return res.status(200).json(productUpdated);
    }catch(err) {
        return res.status(500).json({
            'message': 'Internal Server Error',
            'error': err.message
        });
    }
});

/* Image Case */
// The image of the product is appended based on title and vendor selected
router.put('/title/:title/vendor/:vendor/images', async (req, res) => {
     try {
        const {title, vendor} = req.params;
        const bodyUpdated = req.body;
        if (Object.keys(bodyUpdated).length === 0) {
            return res.status(400).json({'message': 'No data provided to be updated!'});
        }
        const productUpdated = await productsCollection.findOneAndUpdate(
            {title: title, vendor: vendor}, 
            {$push: {images: bodyUpdated}}, 
            {$new: true, runValidators: true}
        );
        if (!productUpdated) {
            return res.status(404).json({'message': 'The title and/or vendor selected are not found. Please try again later!'});
        }
        return res.status(200).json(productUpdated);
    } catch(err) {
        return res.status(500).json({
            'message': 'Internal Server Error',
            'error': err.message
        });
     } 
});

// update the image of a specific product based on title, vendor, and imageID selected
router.put('/title/:title/vendor/:vendor/images/:imageID', async (req, res) => {
    try {
        const {title, vendor, imageID} = req.params;
        const bodyUpdated = req.body;
        if (Object.keys(bodyUpdated).length === 0) {
            return res.status(400).json({'message': 'No data provided to be updated!'});
        }
        const productUpdated = await productsCollection.findOneAndUpdate(
            {title: title, vendor: vendor, 'images.imageId': imageID},
            {$set: {'images.$': bodyUpdated}}, 
            {$new: true, runValidators: true} 
        );
        if (!productUpdated) {
            return res.status(404).json({'message': 'The title, vendor, and/or imageID selected are not found. Please try again later!'});
        }
        return res.status(200).json(productUpdated);

    }catch(err) {
        return res.status(500).json({
            'message': 'Internal Server Error',
            'error': err.message
        })
    }
});

/* DELETE Endpoints */

/* General Case */
// delete a specific product based on the shopifyID selected
router.delete('/:shopifyID', async (req, res) => {
    try {
        const shopifyIDSelected = req.params.shopifyID;
        const productDeleted = await productsCollection.findOneAndDelete({shopifyId: shopifyIDSelected});
        if (!productDeleted) {
            return res.status(404).json({'message': 'The shopifyID selected is not found. Please try again later!'});
        }
        return res.status(200).json(productDeleted);
    }catch(err) {
        return res.status(500).json({
            "message": "Internal Server Error",
            "error": err.message
        });
    }
});

// delete a specific product based on the title and the vendor selected
router.delete('/title/:title/vendor/:vendor', async (req, res) => {
    try {
        const {title, vendor} = req.params;
        const productDeleted = await productsCollection.findOneAndDelete({title: title, vendor: vendor});
        if (!productDeleted) {
            return res.status(404).json({'message': 'The title and/or the vendor selected are not found. Please try again later!'});
        }
        return res.status(200).json(productDeleted);

    }catch(err) {
       return res.status(500).json({
          'message': 'Internal Server Error',
          'error': err.message
       });
    }
});

// delete the option of a specific product at an array
router.delete('/title/:title/vendor/:vendor/:optionID', async (req, res) => {
    try {
      const {title, vendor, optionID} = req.params;
      const productUpdated = await productsCollection.findOneAndUpdate(
        {title: title, vendor: vendor},
        {$pull: {options: {id: optionID}}},
        {$new: true}
      );
      if (!productUpdated) {
        return res.status(404).json({'message': 'The title, vendor, and optionID selected are not found. Please try again later!'});
      }
      return res.status(200).json(productUpdated);
    }catch(err) {
       return res.status(500).json({
            'message': 'Internal Server Error',
            'error': err.message        
       })
    }
});

// delete the value of a specific option of a product based on the title, vendor, and optionID selected
router.delete('/title/:title/vendor/:vendor/option/:optionID/values', async(req, res) => {
     try {
        const {title, vendor, optionID} = req.params;
        const productUpdated = await productsCollection.findOneAndUpdate(
            {title: title, vendor: vendor},
            {$pull: {'options.$.values': {id: optionID}}},
            {$new: true}
        );
        if (!productUpdated || productUpdated.options.length === 0) {
            return res.status(404).json({message: 'The title, vendor, and optionID are not found, or the length of the option values array is 0.' 
                                                   + 'Please try again later!'});
        }
        return res.status(200).json(productUpdated);

     }catch(err) {
        return res.status(500).json({
            'message': 'Internal Server Error',
            'error': err.message
        });
     }
});

// delete the tag of a specific product based on title and vendor selected
router.delete('/title/:title/vendor/:vendor/tags', async (req, res) => {
    try {
        const {title, vendor} = req.params;
        const productUpdated = await productsCollection.findOneAndUpdate(
            {title: title, vendor: vendor}, 
            {$pull: tags}, 
            {$new: true}
        );
        if (!productUpdated || productUpdated.options.length === 0) {
            return res.status(404).json({'message': 'the title and the vendor for this product are not found, or there exists no tags at this array.' +   
                                                    'Please try again later!'});
        }
        return res.status(200).json(productUpdated);
    }catch(err) {
        return res.status(500).json({
            'message': 'Internal Server Error',
            'error': err.message
        });
    }

});

/* Variant Cases */
// delete the variant of a specific product based on title and vendor selected
router.delete('/title/:title/vendor/:vendor/variants/:variantID', async (req, res) => {
    try {
        const {title, vendor, variantID} = req.params;
        const productUpdated = await productsCollection.findOneAndUpdate(
            {title: title, vendor: vendor}, 
            {$pull: {variants: {variantId: variantID}}}, 
            {$new: true}
        );
        if (!productUpdated || productUpdated.variants.length === 0) {
            return res.status(404).json({'message': 'The title and the vendor for this product cannot be found, and there exists no variants for this product.' +  
                                                    'Please try again later!'});
        }
        return res.status(200).json(productUpdated);
    }catch(err) {
       return res.status(500).json({
           'message': 'Internal Server Error',
           'error': err.message
       });
    }
});

router.delete('/title/:title/vendor/:vendor/variants/:variantID/options/:name', async (req, res) => {
    try {
        const {title, vendor, variantID, name} = req.params;
        const productUpdated = await productsCollection.findOneAndUpdate(
            {title: title, vendor: vendor, 'variants.variantId': variantID}, 
            {$pull: {'variants.$.selectedOptions': {name: name}}}, 
            {$new: true}
        );
        if (!productUpdated || 'productUpdated.variants.$.selectedOptions'.length === 0) {
            return res.status(404).json();
        }
        return res.status(200).json(productUpdated);
    }catch(err) {
        return res.status(500).json({
            'message': 'Internal Server Error',
            'error': err.message
        });
    }
});


router.delete('/title/:title/vendor/:vendor/variants/:variantID/images/:imageID', async (req, res) => {
    try {
      const {title, vendor, variantID, imageID} = req.params;
      const productUpdated = await productsCollection.findOneAndUpdate(
        {title: title, vendor: vendor, 'variants.variantId': variantID}, 
        {$pull: {'variants.$.images': {imageId: imageID}}}, 
        {$new: true}
      );
      if (!productUpdated || 'productUpdated.variants.$.images'.length === 0) {
          return res.status(404).json({'message': 'The title, vendor, variantID, and/or imageID selected are not found, or there exists no images for this variant.' 
                                                  + 'Please try again later!'});
      }
      return res.status(200).json(productUpdated);
    }catch(err) {
        return res.status(500).json({
            'message': 'Internal Server Error',
            'error': err.message
        });
    }
});

/* Image Case */
router.delete('/title/:title/vendor/:vendor/images/:imageID', async (req, res) => {
   try {
        const {title, vendor, imageID} = req.params;
        const productUpdated = await productsCollection.findOneAndUpdate(
            {title: title, vendor: vendor}, 
            {$pull: {images: {imageId: imageID}}}, 
            {$new: true}
        );
        if (!productUpdated || productUpdated.images.length === 0) {
            return res.status(404).json({'message': 'The title, vendor, and imageID selected are not found, or the length of the images array is 0.' 
                                                     + 'Please try again later!'});
        }
        return res.status(200).json(productUpdated);
   }catch(err) {
       return res.status(500).json({
          'message': 'Internal Server Error',
          'error': err.message
       });
   }
});

module.exports = router;






