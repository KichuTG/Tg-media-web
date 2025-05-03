const express = require('express');
const cors = require('cors');
const { MongoClient } = require('mongodb');

const app = express();
app.use(cors());

// Environment variables - configure these
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017';
const DATABASE_NAME = process.env.DATABASE_NAME || 'your_database_name';
const COLLECTION_NAME = process.env.COLLECTION_NAME || 'your_collection_name';

let db;

async function connectToDatabase() {
    const client = new MongoClient(MONGODB_URI);
    await client.connect();
    db = client.db(DATABASE_NAME);
    console.log('Connected to MongoDB');
}

// Search endpoint
app.get('/api/search', async (req, res) => {
    try {
        const query = req.query.query;
        
        if (!query || query.trim() === '') {
            return res.json([]);
        }

        // Create a regex pattern similar to your Python implementation
        const queryWords = query.split(' ').filter(w => w.trim() !== '');
        let regexPattern;
        
        if (queryWords.length === 1) {
            regexPattern = new RegExp(`(\\b|[\.\\+\\-_])${queryWords[0]}(\\b|[\.\\+\\-_])`, 'i');
        } else {
            regexPattern = new RegExp(queryWords.join('.*[\\s\\.\\+\\-_]'), 'i');
        }

        const collection = db.collection(COLLECTION_NAME);
        
        const results = await collection.find({
            $or: [
                { file_name: { $regex: regexPattern } },
                { caption: { $regex: regexPattern } }
            ]
        })
        .sort({ $natural: -1 })
        .limit(50)
        .toArray();

        res.json(results);
    } catch (error) {
        console.error('Search error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Start server
const PORT = process.env.PORT || 8000;
connectToDatabase().then(() => {
    app.listen(PORT, () => {
        console.log(`Server running on port ${PORT}`);
    });
});
