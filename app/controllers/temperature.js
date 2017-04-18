var TemperatureEvent = require('../models/TemperatureEvent');
var settings = require('../config/settings');
var apn = require('apn')

/**
 * GET /temperature
 * Gets the last record of the temperature sensor inserted into MongoDB and returns it to the user
 */
exports.temperature = function (req, res) {

    var deviceToken = req.params.deviceToken
    res.setHeader('Content-Type', 'application/json');
    var events = TemperatureEvent.find({})
        .sort({ date: -1 })
        .limit(1)
    events.exec(function (e, docs) {
        res.send(docs);
    });
};
