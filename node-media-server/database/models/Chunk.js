const {Sequelize, DataTypes, Model} = require('sequelize');
const database = require('../database');

class Chunk extends Model { 

}

Chunk.init({
    id: {
        type: DataTypes.UUIDV4,
        primaryKey: true,
        allowNull: false
    },
    created: {
        type: DataTypes.DATE,
        defaultValue: DataTypes.NOW,
        allowNull: false
    },
    path: {
        type: DataTypes.STRING,
        allowNull: false
    },
    totalSize: {
        type: DataTypes.INTEGER,
        allowNull: false
    },
    uploaded: {
        type: DataTypes.INTEGER,
        defaultValue: 0,
        allowNull: false
    }
}, {
    sequelize: database,
    modelName: 'Chunk'
});

module.exports = Chunk;